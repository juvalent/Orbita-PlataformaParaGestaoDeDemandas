from sqlalchemy.exc import IntegrityError

from app.errors import (AppError, ConflitoError, NaoEncontradoError, ProibidoError)
from app.extensions import db
from app.models import Desafio
from app.repositories import desafio_repository, usuario_repository

def _desafio_para_dict(desafio):
    return {
        "id_desafio": desafio.id_desafio,
        "id_responsavel": desafio.id_responsavel,
        "titulo": desafio.titulo,
        "descricao_problema": desafio.descricao_problema,
        "area_demandante": desafio.area_demandante,
        "quem_afeta": desafio.quem_afeta,
        "impacto": desafio.impacto,
        "urgencia": desafio.urgencia,
        "categoria": desafio.categoria,
        "status": desafio.status,
        "data_criacao": desafio.data_criacao.isoformat(),
        "data_atualizacao": desafio.data_atualizacao.isoformat()
    }

def registrar(dados):
    gestor_email = dados["email"].strip().lower()
    gestor_responsavel = usuario_repository.buscar_por_email(gestor_email)
    
    # adicionar tratamento de erros
    
    try:
        desafio = desafio_repository.cadastrar(Desafio(
            id_responsavel=gestor_responsavel.id_usuario,
            titulo = dados["titulo"],
            descricao_problema = dados["descricao_problema"],
            area_demandante = dados["area_demandante"],
            quem_afeta = dados["quem_afeta"],
            impacto = dados["impacto"],
            urgencia = dados["urgencia"],
            categoria = dados["categoria"],
            status = dados["status"]
        ))
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise ConflitoError("O usuário não existe ou não é gestor.") # mudar depois

    return

def listar():
    desafios = desafio_repository.buscar_todos()
    resultado = []
    for desafio in desafios:
        resultado.append(_desafio_para_dict(desafio))
    return resultado

def remover(id_desafio):
    desafio = desafio_repository.buscar_por_id(id_desafio)
    if not desafio:
        raise NaoEncontradoError("Desafio não encontrado.")
    try:
        desafio_repository.deletar(desafio)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise ConflitoError(
            "Este desafio possui ideias vinculadas e não pode ser removido.")

def atualizar(id_desafio, dados):
    desafio = desafio_repository.buscar_por_id(id_desafio)
    if not desafio:
        raise NaoEncontradoError("Desafio não encontrado.")

    # o responsável (email) não é alterado por aqui; só os dados do desafio
    campos = ("titulo", "descricao_problema", "area_demandante", "quem_afeta",
              "impacto", "urgencia", "categoria", "status")
    alterados = {campo: dados[campo] for campo in campos if campo in dados}
    if not alterados:
        raise AppError("Informe ao menos um campo válido para atualizar.")

    for campo, valor in alterados.items():
        setattr(desafio, campo, valor)

    try:
        desafio_repository.atualizar(desafio)
        db.session.commit()
        db.session.refresh(desafio)
    except IntegrityError:
        db.session.rollback()
        raise ConflitoError("Não foi possível atualizar o desafio com os dados informados.")

    return _desafio_para_dict(desafio)
