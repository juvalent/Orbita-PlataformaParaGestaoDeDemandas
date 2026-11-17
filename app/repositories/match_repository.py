from sqlalchemy import func, select

from app.extensions import db
from app.models import Ideia, MatchIdeiaDesafio

def buscar_por_id(id_match):
    return db.session.get(MatchIdeiaDesafio, id_match)

def listar(filtros, page, page_size):
    consulta = select(MatchIdeiaDesafio)

    for campo in ("id_desafio", "id_ideia", "status_match", "origem_match"):
        if filtros.get(campo):
            consulta = consulta.where(getattr(MatchIdeiaDesafio, campo) == filtros[campo])

    total = db.session.scalar(
        select(func.count()).select_from(consulta.subquery()))

    consulta = (consulta
                .order_by(MatchIdeiaDesafio.data_criacao.desc(), MatchIdeiaDesafio.id_match.desc())
                .limit(page_size)
                .offset((page - 1) * page_size))
    return list(db.session.scalars(consulta)), total

def ideias_candidatas(id_desafio):
    ja_ligadas = select(MatchIdeiaDesafio.id_ideia).where(
        MatchIdeiaDesafio.id_desafio == id_desafio)
    consulta = select(Ideia).where(Ideia.status != "arquivada",
                                   Ideia.id_ideia.not_in(ja_ligadas))
    return list(db.session.scalars(consulta))

def adicionar(match):
    db.session.add(match)
    db.session.flush()
    return match

def atualizar(match):
    db.session.add(match)
    db.session.flush()
    return match
