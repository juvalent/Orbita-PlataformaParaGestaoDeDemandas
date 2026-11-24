from sqlalchemy import func, or_, select

from app.extensions import db
from app.models import Ideia, MatchIdeiaDesafio, Projeto, Triagem


def buscar_por_id(id_projeto):
    return db.session.get(Projeto, id_projeto)


def buscar_por_match(id_match):
    return db.session.scalar(select(Projeto).where(Projeto.id_match == id_match))


def listar(filtros, page, page_size):
    consulta = (select(Projeto)
                .join(MatchIdeiaDesafio, MatchIdeiaDesafio.id_match == Projeto.id_match)
                .join(Ideia, Ideia.id_ideia == MatchIdeiaDesafio.id_ideia))
    if filtros.get("status_kanban"):
        consulta = consulta.where(Projeto.status_kanban == filtros["status_kanban"])
    if filtros.get("id_responsavel"):
        consulta = consulta.where(Projeto.id_responsavel == filtros["id_responsavel"])
    if filtros.get("id_ideia"):
        consulta = consulta.where(Ideia.id_ideia == filtros["id_ideia"])
    if filtros.get("q"):
        termo = f"%{filtros['q']}%"
        consulta = consulta.where(or_(Projeto.titulo.ilike(termo), Projeto.descricao.ilike(termo), Ideia.titulo.ilike(termo)))
    total = db.session.scalar(select(func.count()).select_from(consulta.subquery()))
    consulta = (consulta.order_by(Projeto.data_criacao.desc(), Projeto.id_projeto.desc())
                .limit(page_size).offset((page - 1) * page_size))
    return list(db.session.scalars(consulta)), total


def adicionar(projeto):
    db.session.add(projeto)
    db.session.flush()
    return projeto


def atualizar(projeto, campos):
    for campo, valor in campos.items():
        setattr(projeto, campo, valor)
    db.session.flush()
    return projeto


def listar_movimentacoes(id_projeto):
    from app.models import MovimentacaoKanban
    consulta = (select(MovimentacaoKanban)
                .where(MovimentacaoKanban.id_projeto == id_projeto)
                .order_by(MovimentacaoKanban.data_movimentacao, MovimentacaoKanban.id_movimentacao))
    return list(db.session.scalars(consulta))


def ultima_triagem_aprovada(id_match):
    consulta = (select(Triagem)
                .where(Triagem.id_match == id_match, Triagem.decisao == "aprovada")
                .order_by(Triagem.data_avaliacao.desc(), Triagem.id_triagem.desc())
                .limit(1))
    return db.session.scalar(consulta)
