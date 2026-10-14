from sqlalchemy import select

from app.extensions import db
from app.models import Usuario


def buscar_por_email(email):
    return db.session.scalar(select(Usuario).where(Usuario.email == email))


def buscar_por_id(id_usuario):
    return db.session.get(Usuario, id_usuario)


def adicionar(usuario):
    """Adiciona na sessão e gera o id (o commit é feito no service)."""
    db.session.add(usuario)
    db.session.flush()
    return usuario
