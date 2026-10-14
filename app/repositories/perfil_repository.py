from sqlalchemy import select

from app.extensions import db
from app.models import Perfil, UsuarioPerfil


def obter_ou_criar(nome):
    """Devolve o perfil pelo nome; se ainda não existir, cria."""
    perfil = db.session.scalar(select(Perfil).where(Perfil.nome == nome))
    if perfil is None:
        perfil = Perfil(nome=nome)
        db.session.add(perfil)
        db.session.flush()
    return perfil


def associar(id_usuario, id_perfil):
    db.session.add(UsuarioPerfil(id_usuario=id_usuario,
                                 id_perfil=id_perfil))


def listar_nomes_do_usuario(id_usuario):
    consulta = (select(Perfil.nome)
                .join(UsuarioPerfil, UsuarioPerfil.id_perfil == Perfil.id_perfil)
                .where(UsuarioPerfil.id_usuario == id_usuario))
    return list(db.session.scalars(consulta))
