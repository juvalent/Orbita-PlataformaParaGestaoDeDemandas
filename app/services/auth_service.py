from flask_jwt_extended import create_access_token
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from app.errors import (ConflitoError, NaoAutenticadoError, NaoEncontradoError, ProibidoError)
from app.extensions import db
from app.models import Usuario
from app.repositories import perfil_repository, usuario_repository

PERFIS = {
    "colaborador": "Colaborador",
    "gestor": "Gestor Demandante",
    "analista": "Analista/Hub",
}


def _usuario_para_dict(usuario, perfis):
    return {
        "id_usuario": usuario.id_usuario,
        "nome": usuario.nome,
        "email": usuario.email,
        "area": usuario.area,
        "status": usuario.status,
        "perfis": perfis,
        "data_criacao": usuario.data_criacao.isoformat()
        if usuario.data_criacao else None,
    }


def registrar(dados):
    email = dados["email"].strip().lower()

    if usuario_repository.buscar_por_email(email):
        raise ConflitoError("Já existe um usuário com este e-mail.")

    try:
        perfil = perfil_repository.obter_ou_criar(PERFIS[dados["perfil"]])
        usuario = usuario_repository.adicionar(Usuario(
            nome=dados["nome"].strip(),
            email=email,
            senha_hash=generate_password_hash(dados["senha"]),
            area=dados["area"],
        ))
        perfil_repository.associar(usuario.id_usuario, perfil.id_perfil)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise ConflitoError("Já existe um usuário com este e-mail.")

    return _usuario_para_dict(usuario, [perfil.nome])


def login(dados):
    email = dados["email"].strip().lower()
    usuario = usuario_repository.buscar_por_email(email)
    if usuario is None or not check_password_hash(usuario.senha_hash,
                                                  dados["senha"]):
        raise NaoAutenticadoError("E-mail ou senha inválidos.")

    if usuario.status != "ativo":
        raise ProibidoError("Usuário inativo. Procure o administrador.")

    perfis = perfil_repository.listar_nomes_do_usuario(usuario.id_usuario)
    token = create_access_token(
        identity=str(usuario.id_usuario),
        additional_claims={"perfis": perfis},
    )
    return {
        "access_token": token,
        "token_type": "Bearer",
        "usuario": _usuario_para_dict(usuario, perfis),
    }


def obter_usuario_logado(id_usuario):
    usuario = usuario_repository.buscar_por_id(int(id_usuario))
    if usuario is None:
        raise NaoEncontradoError("Usuário não encontrado.")
    perfis = perfil_repository.listar_nomes_do_usuario(usuario.id_usuario)
    return _usuario_para_dict(usuario, perfis)
