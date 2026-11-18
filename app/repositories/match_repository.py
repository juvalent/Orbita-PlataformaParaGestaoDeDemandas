from sqlalchemy import func, select

from app.extensions import db
from app.models import Ideia, MatchIdeiaDesafio


def listar(filtros, page, page_size):
    consulta = select(MatchIdeiaDesafio)

    if filtros.get("id_desafio"):
        consulta = consulta.where(
            MatchIdeiaDesafio.id_desafio == filtros["id_desafio"])
    if filtros.get("id_ideia"):
        consulta = consulta.where(
            MatchIdeiaDesafio.id_ideia == filtros["id_ideia"])
    if filtros.get("status_match"):
        consulta = consulta.where(
            func.upper(MatchIdeiaDesafio.status_match)
            == filtros["status_match"].upper())

    total = db.session.scalar(
        select(func.count()).select_from(consulta.subquery()))

    consulta = (consulta
                .order_by(MatchIdeiaDesafio.data_criacao.desc(),
                          MatchIdeiaDesafio.id_match.desc())
                .limit(page_size)
                .offset((page - 1) * page_size))
    return list(db.session.scalars(consulta)), total


def buscar_por_id(id_match):
    return db.session.get(MatchIdeiaDesafio, id_match)


def buscar_por_par(id_desafio, id_ideia):
    consulta = select(MatchIdeiaDesafio).where(
        MatchIdeiaDesafio.id_desafio == id_desafio,
        MatchIdeiaDesafio.id_ideia == id_ideia)
    return db.session.scalar(consulta)


def ideias_por_ids(ids):
    """{id_ideia: (codigo, titulo)} para montar a resposta sem N+1 consultas."""
    ids = set(ids)
    if not ids:
        return {}
    consulta = select(Ideia.id_ideia, Ideia.codigo, Ideia.titulo).where(
        Ideia.id_ideia.in_(ids))
    return {
        id_ideia: (codigo, titulo)
        for id_ideia, codigo, titulo in db.session.execute(consulta).all()
    }


def adicionar(match):
    db.session.add(match)
    db.session.flush()
    return match
