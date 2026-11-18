"""Regras de negócio do Match (vínculo entre Ideia e Desafio)."""

from datetime import datetime, timezone
from math import ceil

from sqlalchemy.exc import IntegrityError

from app.errors import ConflitoError, NaoEncontradoError, ProibidoError
from app.extensions import db
from app.models import MatchIdeiaDesafio
from app.repositories import (desafio_repository, ideia_repository,
                              match_repository)

_PERFIS_ANALISTA = {"analista/hub", "analista", "hub", "administrador",
                    "admin"}

# Vínculo feito à mão pelo Analista já nasce validado por ele.
ORIGEM_MANUAL = "manual"
STATUS_MATCH_VALIDADO = "VALIDADO"


def _e_analista(perfis):
    nomes = {str(perfil).strip().casefold() for perfil in (perfis or [])}
    return bool(nomes & _PERFIS_ANALISTA)


def _exigir_analista(perfis):
    if not _e_analista(perfis):
        raise ProibidoError("Apenas o Analista/Hub pode realizar esta ação.")


def _iso(valor):
    return valor.isoformat() if valor else None


def _serializar(match, ideias, desafios):
    codigo, titulo_ideia = ideias.get(match.id_ideia, (None, None))
    return {
        "id_match": match.id_match,
        "id_ideia": match.id_ideia,
        "ideia_codigo": codigo,
        "ideia_titulo": titulo_ideia,
        "id_desafio": match.id_desafio,
        "desafio_titulo": desafios.get(match.id_desafio),
        "id_validado_por": match.id_validado_por,
        "score_compatibilidade": match.score_compatibilidade,
        "justificativa": match.justificativa,
        "origem_match": match.origem_match,
        "status_match": match.status_match,
        "data_criacao": _iso(match.data_criacao),
        "data_validacao": _iso(match.data_validacao),
    }


def _serializar_um(match):
    ideias = match_repository.ideias_por_ids([match.id_ideia])
    desafios = desafio_repository.titulos_por_ids([match.id_desafio])
    return _serializar(match, ideias, desafios)


def listar(filtros, page, page_size, perfis):
    _exigir_analista(perfis)
    filtros = {chave: valor for chave, valor in filtros.items()
               if valor not in (None, "")}
    matches, total = match_repository.listar(filtros, page, page_size)
    ideias = match_repository.ideias_por_ids(m.id_ideia for m in matches)
    desafios = desafio_repository.titulos_por_ids(m.id_desafio for m in matches)
    return {
        "items": [_serializar(m, ideias, desafios) for m in matches],
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": ceil(total / page_size) if total else 0,
    }


def obter(id_match, perfis):
    _exigir_analista(perfis)
    match = match_repository.buscar_por_id(id_match)
    if match is None:
        raise NaoEncontradoError("Match não encontrado.")
    return _serializar_um(match)


def criar(dados, id_usuario, perfis):
    _exigir_analista(perfis)

    ideia = ideia_repository.buscar_por_id(dados["id_ideia"])
    if ideia is None:
        raise NaoEncontradoError("Ideia não encontrada.")
    if desafio_repository.buscar_por_id(dados["id_desafio"]) is None:
        raise NaoEncontradoError("Desafio não encontrado.")

    if (ideia.status or "").strip().casefold() == "arquivada":
        raise ConflitoError(
            "Uma ideia arquivada não pode ser vinculada a um desafio.")

    if match_repository.buscar_por_par(dados["id_desafio"], dados["id_ideia"]):
        raise ConflitoError("Esta ideia já está vinculada a este desafio.")

    match = MatchIdeiaDesafio(
        id_desafio=dados["id_desafio"],
        id_ideia=dados["id_ideia"],
        id_validado_por=id_usuario,
        justificativa=dados.get("justificativa") or None,
        origem_match=ORIGEM_MANUAL,
        status_match=STATUS_MATCH_VALIDADO,
        data_validacao=datetime.now(timezone.utc).replace(tzinfo=None),
    )
    try:
        match_repository.adicionar(match)
        db.session.commit()
        db.session.refresh(match)
    except IntegrityError as erro:
        db.session.rollback()
        # corrida entre dois cliques: a UniqueConstraint do banco é a garantia final
        raise ConflitoError(
            "Esta ideia já está vinculada a este desafio.") from erro

    return _serializar_um(match)
