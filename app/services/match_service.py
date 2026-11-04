import re
from math import ceil

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from app.errors import ConflitoError, NaoEncontradoError, ProibidoError
from app.extensions import db
from app.models import MatchIdeiaDesafio
from app.repositories import desafio_repository, ideia_repository, match_repository

_PERFIS_ANALISTA = {"analista/hub", "analista", "hub", "administrador",
                    "admin"}
_SCORE_MINIMO = 0.1
_IGNORAR = {"sobre", "entre", "muito", "quando", "porque", "ainda", "então",
            "também"}


def _e_analista(perfis):
    nomes = {str(perfil).strip().casefold() for perfil in (perfis or [])}
    return bool(nomes & _PERFIS_ANALISTA)


def _exigir_analista(perfis):
    if not _e_analista(perfis):
        raise ProibidoError("Apenas o Analista/Hub pode realizar esta ação.")


def _match_para_dict(match):
    return {
        "id_match": match.id_match,
        "id_desafio": match.id_desafio,
        "id_ideia": match.id_ideia,
        "id_validado_por": match.id_validado_por,
        "score_compatibilidade": match.score_compatibilidade,
        "justificativa": match.justificativa,
        "origem_match": match.origem_match,
        "status_match": match.status_match,
        "data_criacao": match.data_criacao.isoformat(),
        "data_validacao": match.data_validacao.isoformat() if match.data_validacao else None
    }


def _palavras(texto):
    palavras = re.findall(r"\w+", texto.casefold())
    return {p for p in palavras if len(p) >= 5 and p not in _IGNORAR}


def _igual(a, b):
    return bool(a) and bool(b) and a.strip().casefold() == b.strip().casefold()


def _pontuar(desafio, ideia, palavras_desafio):
    score = 0.0
    motivos = []
    if _igual(ideia.area, desafio.area_demandante):
        score += 0.3
        motivos.append("mesma área")
    if _igual(ideia.categoria, desafio.categoria):
        score += 0.3
        motivos.append("mesma categoria")

    em_comum = palavras_desafio & _palavras(f"{ideia.titulo} {ideia.descricao}")
    if em_comum:
        score += 0.4 * min(len(em_comum), 3) / 3  # 3 palavras em comum já valem o máximo
        motivos.append("palavras em comum: " + ", ".join(sorted(em_comum)[:5]))

    return round(score, 2), "Compatibilidade por regra: " + "; ".join(motivos) + "."


def registrar(dados, perfis):
    _exigir_analista(perfis)
    if not desafio_repository.buscar_por_id(dados["id_desafio"]):
        raise NaoEncontradoError("Desafio não encontrado.")
    if not ideia_repository.buscar_por_id(dados["id_ideia"]):
        raise NaoEncontradoError("Ideia não encontrada.")

    try:
        match = match_repository.adicionar(MatchIdeiaDesafio(
            id_desafio=dados["id_desafio"],
            id_ideia=dados["id_ideia"],
            justificativa=dados.get("justificativa"),
            origem_match="manual",
            status_match="PENDENTE"
        ))
        db.session.commit()
        db.session.refresh(match)
    except IntegrityError:
        db.session.rollback()
        raise ConflitoError("Esta ideia já está vinculada a este desafio.")

    return _match_para_dict(match)


def listar(filtros, page, page_size, perfis):
    _exigir_analista(perfis)
    matches, total = match_repository.listar(filtros, page, page_size)
    return {
        "items": [_match_para_dict(match) for match in matches],
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": ceil(total / page_size) if total else 0
    }


def sugerir_por_regra(dados, perfis):
    _exigir_analista(perfis)
    desafio = desafio_repository.buscar_por_id(dados["id_desafio"])
    if not desafio:
        raise NaoEncontradoError("Desafio não encontrado.")

    palavras_desafio = _palavras(f"{desafio.titulo} {desafio.descricao_problema}")
    pontuadas = []
    for ideia in match_repository.ideias_candidatas(desafio.id_desafio):
        score, justificativa = _pontuar(desafio, ideia, palavras_desafio)
        if score >= _SCORE_MINIMO:
            pontuadas.append((score, justificativa, ideia))
    pontuadas.sort(key=lambda item: item[0], reverse=True)

    try:
        matches = [match_repository.adicionar(MatchIdeiaDesafio(
            id_desafio=desafio.id_desafio,
            id_ideia=ideia.id_ideia,
            score_compatibilidade=score,
            justificativa=justificativa,
            origem_match="regra",
            status_match="PENDENTE"
        )) for score, justificativa, ideia in pontuadas[:dados["limite"]]]
        db.session.commit()
        for match in matches:
            db.session.refresh(match)
    except IntegrityError:
        db.session.rollback()
        raise ConflitoError("Não foi possível gerar as sugestões. Tente novamente.")

    return {"sugestoes": [_match_para_dict(match) for match in matches]}


def validar(id_match, dados, id_usuario, perfis):
    _exigir_analista(perfis)
    match = match_repository.buscar_por_id(id_match)
    if not match:
        raise NaoEncontradoError("Match não encontrado.")
    if match.status_match != "PENDENTE":
        raise ConflitoError("Este match já foi validado ou descartado.")

    match.status_match = "VALIDADO" if dados["decisao"] == "validar" else "DESCARTADO"
    match.id_validado_por = id_usuario
    match.data_validacao = func.now()
    if dados.get("justificativa"):
        match.justificativa = dados["justificativa"]

    try:
        match_repository.atualizar(match)
        db.session.commit()
        db.session.refresh(match)
    except IntegrityError:
        db.session.rollback()
        raise ConflitoError("Não foi possível registrar a decisão do match.")

    return _match_para_dict(match)
