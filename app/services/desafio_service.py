from sqlalchemy.exc import IntegrityError

from app.errors import (AppError, ConflitoError, NaoEncontradoError, ProibidoError)
from app.extensions import db
from app.models import Desafio
from app.repositories import desafio_repository, usuario_repository

_PERFIS_ANALISTA = {"analista/hub", "analista", "hub", "administrador",
                    "admin"}
_PERFIS_GESTOR = {"gestor demandante", "gestor"}


def _nomes_de_perfil(perfis):
    return {str(perfil).strip().casefold() for perfil in (perfis or [])}


def _e_analista(perfis):
    return bool(_nomes_de_perfil(perfis) & _PERFIS_ANALISTA)


def _e_gestor(perfis):
    return bool(_nomes_de_perfil(perfis) & _PERFIS_GESTOR)


def _exigir_gestor_ou_analista(perfis):
    """Colaborador só consulta desafios; não registra, edita nem remove."""
    if not (_e_analista(perfis) or _e_gestor(perfis)):
        raise ProibidoError("Apenas Gestor Demandante ou Analista/Hub pode "
                            "realizar esta ação.")


def _exigir_gerenciar(desafio, id_usuario, perfis):
    """Analista/Hub gerencia qualquer desafio; Gestor só os que são seus."""
    _exigir_gestor_ou_analista(perfis)
    if _e_analista(perfis):
        return
    if desafio.id_responsavel != id_usuario:
        raise ProibidoError("Você só pode gerenciar os desafios sob sua "
                            "responsabilidade.")


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

def registrar(dados, id_usuario, perfis):
    _exigir_gestor_ou_analista(perfis)
    gestor_email = dados["email"].strip().lower()
    gestor_responsavel = usuario_repository.buscar_por_email(gestor_email)
    if gestor_responsavel is None:
        raise NaoEncontradoError("Usuário responsável não encontrado.")
    if (not _e_analista(perfis)
            and gestor_responsavel.id_usuario != id_usuario):
        raise ProibidoError("Você só pode registrar desafios sob sua " "própria responsabilidade.")
    
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

def remover(id_desafio, id_usuario, perfis):
    desafio = desafio_repository.buscar_por_id(id_desafio)
    if not desafio:
        raise NaoEncontradoError("Desafio não encontrado.")
    _exigir_gerenciar(desafio, id_usuario, perfis)
    desafio_repository.deletar(desafio)
    db.session.commit()

def atualizar(id_desafio, dados, id_usuario, perfis):
    desafio = desafio_repository.buscar_por_id(id_desafio)
    if not desafio:
        raise NaoEncontradoError("Desafio não encontrado.")
    _exigir_gerenciar(desafio, id_usuario, perfis)

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
