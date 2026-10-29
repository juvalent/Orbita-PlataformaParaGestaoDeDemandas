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

def buscar_por_responsavel(responsavel):
    return db.session.scalar(select(Desafio).where(Desafio.id_responsavel == id_responsavel))

def buscar_todos():
    query = select(Desafio)
    return db.session.execute(query).scalars().all()

def cadastrar(desafio):
    db.session.add(desafio)
    db.session.flush()
    return desafio

def atualizar(desafio):
    db.session.add(desafio)
    db.session.flush()
    return desafio

def deletar(desafio):
    db.session.delete(desafio)
    db.session.flush()
