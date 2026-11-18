from sqlalchemy import func, select

from app.extensions import db
from app.models import AiEmbedding, AiSugestao, Ideia, MatchIdeiaDesafio


# ------------------------------------------------------------- embeddings
def buscar_embedding(entidade_tipo, entidade_id):
    return db.session.scalar(select(AiEmbedding).where(
        AiEmbedding.entidade_tipo == entidade_tipo,
        AiEmbedding.entidade_id == entidade_id))


def embeddings_por_entidades(entidade_tipo, ids):
    ids = list(ids)
    if not ids:
        return {}
    consulta = select(AiEmbedding).where(
        AiEmbedding.entidade_tipo == entidade_tipo,
        AiEmbedding.entidade_id.in_(ids))
    return {e.entidade_id: e for e in db.session.scalars(consulta)}


def buscar_vetor_por_hash(hash_conteudo, modelo):
    """Deduplicação: reaproveita o vetor de qualquer texto idêntico."""
    return db.session.scalar(
        select(AiEmbedding.vetor).where(
            AiEmbedding.hash_conteudo == hash_conteudo,
            AiEmbedding.modelo_embedding == modelo).limit(1))


def salvar_embedding(entidade_tipo, entidade_id, hash_conteudo, modelo, vetor):
    registro = buscar_embedding(entidade_tipo, entidade_id)
    if registro is None:
        registro = AiEmbedding(entidade_tipo=entidade_tipo,
                               entidade_id=entidade_id)
        db.session.add(registro)
    registro.hash_conteudo = hash_conteudo
    registro.modelo_embedding = modelo
    registro.vetor = vetor
    registro.data_atualizacao = func.now()
    db.session.flush()
    return registro


def ideias_para_indexar(modelo):
    """Ideias ativas sem vetor, com vetor de outro modelo ou editadas depois."""
    consulta = (select(Ideia)
                .outerjoin(AiEmbedding, (AiEmbedding.entidade_tipo == "ideia")
                           & (AiEmbedding.entidade_id == Ideia.id_ideia))
                .where(Ideia.status != "arquivada")
                .where((AiEmbedding.id.is_(None))
                       | (AiEmbedding.modelo_embedding != modelo)
                       | (Ideia.data_atualizacao > AiEmbedding.data_atualizacao))
                .order_by(Ideia.data_criacao.desc()))
    return list(db.session.scalars(consulta))


def ideias_por_ids(ids):
    ids = list(ids)
    if not ids:
        return []
    return list(db.session.scalars(select(Ideia).where(Ideia.id_ideia.in_(ids))))


def ideias_mais_proximas(vetor_desafio, modelo, top_n):
    """Top N ideias por similaridade de cosseno (índice HNSW do pgvector).

    Devolve [(id_ideia, similaridade 0..1)], da mais para a menos parecida.
    """
    distancia = AiEmbedding.vetor.cosine_distance(vetor_desafio)
    ativas = select(Ideia.id_ideia).where(Ideia.status != "arquivada")
    consulta = (select(AiEmbedding.entidade_id, distancia)
                .where(AiEmbedding.entidade_tipo == "ideia",
                       AiEmbedding.modelo_embedding == modelo,
                       AiEmbedding.entidade_id.in_(ativas))
                .order_by(distancia)
                .limit(top_n))
    return [(id_ideia, 1.0 - float(dist))
            for id_ideia, dist in db.session.execute(consulta)]


# ------------------------------------------------------- match / sugestão
def buscar_match(id_desafio, id_ideia):
    return db.session.scalar(select(MatchIdeiaDesafio).where(
        MatchIdeiaDesafio.id_desafio == id_desafio,
        MatchIdeiaDesafio.id_ideia == id_ideia))


def adicionar(objeto):
    db.session.add(objeto)
    db.session.flush()
    return objeto


def adicionar_sugestao(sugestao: AiSugestao):
    return adicionar(sugestao)
