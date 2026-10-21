from sqlalchemy import select

from app.extensions import db
from app.models import Desafio


def buscar_por_id(id_desafio):
    return db.session.get(Desafio, id_desafio)


def titulos_por_ids(ids):
    ids = set(ids)
    if not ids:
        return {}
    consulta = select(Desafio.id_desafio, Desafio.titulo).where(
        Desafio.id_desafio.in_(ids))
    return dict(db.session.execute(consulta).all())


def usuario_e_responsavel(id_desafio, id_usuario):
    consulta = select(Desafio.id_desafio).where(
        Desafio.id_desafio == id_desafio,
        Desafio.id_responsavel == id_usuario)
    return db.session.scalar(consulta) is not None
