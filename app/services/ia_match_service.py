"""Sugestão de match Desafio x Ideia com IA (consultiva, human-in-the-loop).

Fluxo de POST /api/v1/ia/matches/sugerir-ia:
  1. embedding do desafio (SHA-256 evita chamar a API se o texto já foi vetorizado);
  2. indexação preguiçosa das ideias que ainda não têm vetor;
  3. busca das N ideias mais próximas no pgvector (cosseno, índice HNSW);
  4. o LLM atribui score e justificativa a cada par (em paralelo, temperature 0.2);
  5. só se TODAS as respostas forem válidas: grava o match e a ai_sugestao como
     PENDENTE. Qualquer falha descarta a resposta da IA (503/504) e o fluxo
     manual continua livre. Nada é aprovado automaticamente.
"""

import hashlib
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from app.errors import (ConflitoError, IAIndisponivelError,
                        NaoEncontradoError)
from app.extensions import db
from app.models import AiSugestao, MatchIdeiaDesafio
from app.repositories import ai_repository, desafio_repository
from app.services.ai_service_adapter import AIServiceAdapter

MAX_CHARS_EMBEDDING = 8000
LOTE_EMBEDDING = 50        # ideias indexadas por requisição (1 chamada em lote)


# --------------------------------------------------------------- helpers
def _juntar(*partes):
    return "\n".join(p.strip() for p in partes if p and p.strip())


def texto_do_desafio(desafio):
    """titulo + descricao + problema (+ quem afeta e impacto)."""
    return _juntar(desafio.titulo, desafio.descricao_problema,
                   desafio.quem_afeta, desafio.impacto)[:MAX_CHARS_EMBEDDING]


def texto_da_ideia(ideia):
    """titulo + descricao + problema_resolvido + beneficio_esperado."""
    return _juntar(ideia.titulo, ideia.descricao, ideia.problema_resolvido,
                   ideia.beneficio_esperado)[:MAX_CHARS_EMBEDDING]


def hash_do_texto(texto):
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


# ------------------------------------------------------------ embeddings
def _garantir_embedding(tipo, entidade_id, texto, adapter, prazo):
    """Devolve o vetor do texto, chamando a API só se for realmente novo."""
    modelo = adapter.emb_model
    hash_atual = hash_do_texto(texto)

    existente = ai_repository.buscar_embedding(tipo, entidade_id)
    if (existente is not None and existente.hash_conteudo == hash_atual
            and existente.modelo_embedding == modelo):
        return existente.vetor

    vetor = ai_repository.buscar_vetor_por_hash(hash_atual, modelo)
    if vetor is None:
        vetores, _ = adapter.gerar_embeddings([texto], prazo)
        vetor = vetores[0]
    ai_repository.salvar_embedding(tipo, entidade_id, hash_atual, modelo, vetor)
    return vetor


def _indexar_ideias_pendentes(adapter, prazo):
    """Vetoriza (em lote) as ideias ativas sem vetor ou com texto alterado."""
    modelo = adapter.emb_model
    pendentes = ai_repository.ideias_para_indexar(modelo)[:LOTE_EMBEDDING]
    a_enviar = []   # (ideia, hash, texto) que realmente precisam da API
    for ideia in pendentes:
        texto = texto_da_ideia(ideia)
        hash_atual = hash_do_texto(texto)
        existente = ai_repository.buscar_embedding("ideia", ideia.id_ideia)
        if (existente is not None and existente.hash_conteudo == hash_atual
                and existente.modelo_embedding == modelo):
            existente.data_atualizacao = func.now()   # texto igual: só renova
            continue
        vetor = ai_repository.buscar_vetor_por_hash(hash_atual, modelo)
        if vetor is not None:
            ai_repository.salvar_embedding("ideia", ideia.id_ideia, hash_atual,
                                           modelo, vetor)
        else:
            a_enviar.append((ideia, hash_atual, texto))

    if a_enviar:
        vetores, _ = adapter.gerar_embeddings([t for _, _, t in a_enviar],
                                              prazo)
        for (ideia, hash_atual, _), vetor in zip(a_enviar, vetores):
            ai_repository.salvar_embedding("ideia", ideia.id_ideia, hash_atual,
                                           modelo, vetor)
    db.session.commit()   # vetores são cache: valem mesmo se o LLM falhar


# ------------------------------------------------------------------- LLM
def _avaliar_pares(adapter, texto_desafio, ideias, prazo):
    """Chama o LLM para cada par, em paralelo. Qualquer falha propaga."""
    def avaliar(ideia):
        return adapter.avaliar_compatibilidade(
            texto_desafio, texto_da_ideia(ideia), prazo)

    with ThreadPoolExecutor(max_workers=max(1, min(len(ideias), 5))) as pool:
        return list(pool.map(avaliar, ideias))


# ------------------------------------------------------------ persistência
# ATENÇÃO: criar/atualizar o match é do módulo de Match (Lucas). Está aqui só
# para devolver o matchId do contrato; troque por uma chamada ao serviço dele.
def _registrar_match_e_sugestao(desafio, ideia, avaliacao, id_usuario):
    match = ai_repository.buscar_match(desafio.id_desafio, ideia.id_ideia)
    if match is None:
        match = ai_repository.adicionar(MatchIdeiaDesafio(
            id_desafio=desafio.id_desafio,
            id_ideia=ideia.id_ideia,
            score_compatibilidade=avaliacao["scoreCompatibilidade"],
            justificativa=avaliacao["justificativa"],
            origem_match="ia",
            status_match="PENDENTE",
        ))
    elif match.origem_match == "ia" and match.status_match == "PENDENTE":
        # nova sugestão da IA ainda não revisada: atualiza
        match.score_compatibilidade = avaliacao["scoreCompatibilidade"]
        match.justificativa = avaliacao["justificativa"]
    # match manual ou já revisado por humano: nunca é sobrescrito pela IA

    sugestao = ai_repository.adicionar_sugestao(AiSugestao(
        id_desafio=desafio.id_desafio,
        id_ideia=ideia.id_ideia,
        id_match=match.id_match,
        solicitado_por_id=id_usuario,
        sugestao={"scoreCompatibilidade": avaliacao["scoreCompatibilidade"],
                  "justificativa": avaliacao["justificativa"]},
        modelo_versao=avaliacao["modelo"],
        status_revisao="PENDENTE",
    ))
    return match, sugestao


# ------------------------------------------------------------- caso de uso
def sugerir_matches(id_desafio, top_n, id_usuario):
    """Ponto de entrada para a rota. A rota deve restringir a Analista/Hub."""
    desafio = desafio_repository.buscar_por_id(id_desafio)
    if desafio is None:
        raise NaoEncontradoError("Desafio não encontrado.")

    adapter = AIServiceAdapter()
    if not adapter.emb_model:
        raise IAIndisponivelError(
            "Provedor de embeddings não configurado (AI_EMBEDDING_MODEL).")
    prazo = adapter.novo_prazo()   # 10 s para TODA a requisição de IA

    texto_desafio = texto_do_desafio(desafio)
    vetor_desafio = _garantir_embedding("desafio", desafio.id_desafio,
                                        texto_desafio, adapter, prazo)
    _indexar_ideias_pendentes(adapter, prazo)

    proximas = ai_repository.ideias_mais_proximas(
        vetor_desafio, adapter.emb_model, top_n)
    ideias = {i.id_ideia: i for i in ai_repository.ideias_por_ids(
        [id_ideia for id_ideia, _ in proximas])}
    candidatas = [ideias[id_ideia] for id_ideia, _ in proximas
                  if id_ideia in ideias]

    avaliacoes = (_avaliar_pares(adapter, texto_desafio, candidatas, prazo)
                  if candidatas else [])

    # Todas as respostas chegaram válidas: só agora grava (tudo ou nada).
    sugestoes = []
    try:
        for ideia, avaliacao in zip(candidatas, avaliacoes):
            match, sugestao = _registrar_match_e_sugestao(
                desafio, ideia, avaliacao, id_usuario)
            sugestoes.append({
                "sugestaoId": str(sugestao.id),
                "matchId": match.id_match,
                "ideiaId": ideia.id_ideia,
                "demandaId": desafio.id_desafio,
                "ideiaTitulo": ideia.titulo,
                "scoreCompatibilidade": avaliacao["scoreCompatibilidade"],
                "justificativa": avaliacao["justificativa"],
                "statusMatch": match.status_match,
            })
        db.session.commit()
    except IntegrityError as erro:
        db.session.rollback()
        raise ConflitoError("Não foi possível registrar as sugestões. "
                            "Tente novamente.") from erro

    sugestoes.sort(key=lambda s: s["scoreCompatibilidade"], reverse=True)
    scores = [s["scoreCompatibilidade"] for s in sugestoes]
    return {
        "sugestoes": sugestoes,
        "aiMetadata": {
            "modeloVersao": (avaliacoes[0]["modelo"] if avaliacoes
                             else adapter.model),
            "grauConfianca": (round(sum(scores) / len(scores) * 100, 1)
                              if scores else 0.0),
            "humanInTheLoop": True,
            "generatedAt": datetime.now(timezone.utc)
            .strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
    }
