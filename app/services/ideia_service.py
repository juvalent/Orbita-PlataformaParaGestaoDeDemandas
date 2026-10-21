"""Regras de negócio do CRUD de ideias."""

from datetime import datetime, timezone
from math import ceil

from sqlalchemy.exc import IntegrityError

from app.errors import ConflitoError, NaoEncontradoError, ProibidoError
from app.extensions import db
from app.models import Ideia
from app.repositories import desafio_repository, ideia_repository, usuario_repository
from app.schemas.ideia_schema import IdeiaResponseSchema

_RESPOSTA_IDEIA = IdeiaResponseSchema()
_PERFIS_GESTAO = {
    "gestor demandante",
    "analista/hub",
    "gestor",
    "analista",
    "hub",
    "administrador",
    "admin",
}
_STATUS_EDITAVEIS = {"submetida", "rascunho", "nova"}
_STATUS_APROVAVEIS = {"submetida", "nova", "em_avaliacao", "em avaliação"}


def _serializar(ideia):
    """Converte o modelo SQLAlchemy para um dicionário JSON seguro."""
    return _RESPOSTA_IDEIA.dump(ideia)


def _status_normalizado(status):
    return (status or "").strip().casefold().replace("-", "_")


def _tem_perfil_gestor(perfis):
    """Aceita os nomes de perfil emitidos pelo serviço de autenticação atual."""
    nomes = {str(perfil).strip().casefold() for perfil in (perfis or [])}
    return bool(nomes.intersection(_PERFIS_GESTAO))


def _exigir_gestor(perfis):
    if not _tem_perfil_gestor(perfis):
        raise ProibidoError("Apenas Gestor ou Analista/Hub pode realizar esta ação.")


def _buscar_ideia_ou_404(id_ideia):
    ideia = ideia_repository.buscar_por_id(id_ideia)
    if ideia is None:
        raise NaoEncontradoError("Ideia não encontrada.")
    return ideia


def _validar_desafio(id_desafio):
    desafio = desafio_repository.buscar_por_id(id_desafio)
    if desafio is None:
        raise NaoEncontradoError("Desafio não encontrado.")
    return desafio


def _proximo_codigo():
    """Gera o próximo código IDE-AAAA-NNNN com base nos códigos do ano."""
    ano = datetime.now(timezone.utc).year
    ultimo_codigo = ideia_repository.ultimo_codigo_do_ano(ano)
    sequencial = 0
    if ultimo_codigo:
        try:
            sequencial = int(ultimo_codigo.rsplit("-", 1)[1])
        except (IndexError, ValueError):
            # Um código legado fora do formato esperado não deve interromper o cadastro.
            sequencial = 0
    return f"IDE-{ano}-{sequencial + 1:04d}"


def listar(filtros, page, page_size):
    """Retorna ideias paginadas e metadados da consulta."""
    filtros = {
        chave: valor.strip() if isinstance(valor, str) else valor
        for chave, valor in filtros.items()
    }
    filtros = {chave: valor for chave, valor in filtros.items() if valor not in (None, "")}
    ideias, total = ideia_repository.listar(filtros, page, page_size)
    return {
        "items": [_serializar(ideia) for ideia in ideias],
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": ceil(total / page_size) if total else 0,
    }


def obter(id_ideia):
    """Busca uma ideia pelo identificador numérico."""
    return _serializar(_buscar_ideia_ou_404(id_ideia))


def criar(dados, id_autor):
    """Cria uma ideia vinculada ao usuário autenticado e a um desafio existente."""
    usuario = usuario_repository.buscar_por_id(id_autor)
    if usuario is None:
        raise NaoEncontradoError("Usuário autenticado não encontrado.")

    _validar_desafio(dados["id_desafio"])
    payload = dict(dados)
    payload["titulo"] = payload["titulo"].strip()
    payload["descricao"] = payload["descricao"].strip()

    # Uma colisão pode ocorrer se dois cadastros simultâneos calcularem o mesmo código.
    # Tentamos novamente após rollback, consultando o maior código já persistido.
    for tentativa in range(3):
        ideia = Ideia(
            codigo=_proximo_codigo(),
            id_autor=id_autor,
            id_desafio=payload["id_desafio"],
            titulo=payload["titulo"],
            descricao=payload["descricao"],
            area=payload.get("area"),
            categoria=payload.get("categoria"),
            problema_resolvido=payload.get("problema_resolvido"),
            beneficio_esperado=payload.get("beneficio_esperado"),
            status="submetida",
        )
        try:
            ideia_repository.adicionar(ideia)
            db.session.commit()
            db.session.refresh(ideia)
            return _serializar(ideia)
        except IntegrityError as erro:
            db.session.rollback()
            if tentativa == 2:
                raise ConflitoError(
                    "Não foi possível gerar um código único para a ideia. Tente novamente."
                ) from erro

    # O laço sempre retorna ou levanta uma exceção; o retorno protege analisadores estáticos.
    raise ConflitoError("Não foi possível cadastrar a ideia.")


def atualizar(id_ideia, dados, id_usuario, perfis):
    """Atualiza uma ideia editável, conforme autoria ou perfil de gestão."""
    ideia = _buscar_ideia_ou_404(id_ideia)
    gestor = _tem_perfil_gestor(perfis)

    if ideia.id_autor != id_usuario and not gestor:
        raise ProibidoError("Você não tem permissão para editar esta ideia.")

    if _status_normalizado(ideia.status) not in _STATUS_EDITAVEIS:
        raise ProibidoError("Esta ideia não pode mais ser editada no status atual.")

    payload = dict(dados)
    for campo in ("titulo", "descricao"):
        if campo in payload:
            payload[campo] = payload[campo].strip()

    if "id_desafio" in payload:
        _validar_desafio(payload["id_desafio"])

    try:
        ideia_repository.atualizar(ideia, payload)
        db.session.commit()
        db.session.refresh(ideia)
        return _serializar(ideia)
    except IntegrityError as erro:
        db.session.rollback()
        raise ConflitoError("Não foi possível atualizar a ideia com os dados informados.") from erro


def aprovar(id_ideia, perfis):
    """Aprova uma ideia submetida, exclusivamente por perfil de gestão."""
    _exigir_gestor(perfis)
    ideia = _buscar_ideia_ou_404(id_ideia)
    status_atual = _status_normalizado(ideia.status)

    if status_atual in {"aprovada", "arquivada"}:
        raise ConflitoError("A ideia já foi aprovada ou arquivada e não pode ser aprovada novamente.")
    if status_atual not in _STATUS_APROVAVEIS:
        raise ConflitoError("A ideia não está em um status que permita aprovação.")

    return _persistir_novo_status(ideia, "aprovada")


def arquivar(id_ideia, perfis):
    """Arquiva uma ideia por perfil de gestão; operação não é repetível."""
    _exigir_gestor(perfis)
    ideia = _buscar_ideia_ou_404(id_ideia)
    if _status_normalizado(ideia.status) == "arquivada":
        raise ConflitoError("A ideia já está arquivada.")
    return _persistir_novo_status(ideia, "arquivada")


def _persistir_novo_status(ideia, novo_status):
    try:
        ideia_repository.alterar_status(ideia, novo_status)
        db.session.commit()
        db.session.refresh(ideia)
        return _serializar(ideia)
    except IntegrityError as erro:
        db.session.rollback()
        raise ConflitoError("Não foi possível alterar o status da ideia.") from erro
