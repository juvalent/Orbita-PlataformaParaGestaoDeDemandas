from app.extensions import db
from app.models import Desafio


def buscar_por_id(id_desafio):
    return db.session.get(Desafio, id_desafio)
