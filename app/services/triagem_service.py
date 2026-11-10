from math import ceil

from sqlalchemy.exc import IntegrityError

from app.errors import ConflitoError, NaoEncontradoError, ProibidoError
from app.extensions import db
from app.models import Triagem
from app.repositories import ideia_repository, match_repository, triagem_repository

_PERFIS_ANALISTA = {"analista/hub", "analista", "hub", "administrador",
                    "admin"}


def _e_analista(perfis):
    nomes = {str(perfil).strip().casefold() for perfil in (perfis or [])}
    return bool(nomes & _PERFIS_ANALISTA)


def _exigir_analista(perfis):
    if not _e_analista(perfis):
        raise ProibidoError("Apenas o Analista/Hub pode realizar esta ação.")


def _pontuacao(triagem):
    """Média de 1 a 5 dos critérios; o esforço entra invertido. Só ordena, não decide."""
    soma = (triagem.impacto + triagem.urgencia + triagem.viabilidade
            + triagem.alinhamento + (6 - triagem.esforco))
    return round(soma / 5, 2)


def _triagem_para_dict(triagem, id_desafio, id_ideia):
    return {
        "id_triagem": triagem.id_triagem,
        "id_match": triagem.id_match,
        "id_desafio": id_desafio,
        "id_ideia": id_ideia,
        "id_avaliador": triagem.id_avaliador,
        "impacto": triagem.impacto,
        "urgencia": triagem.urgencia,
        "viabilidade": triagem.viabilidade,
        "alinhamento": triagem.alinhamento,
        "esforco": triagem.esforco,
        "pontuacao": _pontuacao(triagem),
        "parecer": triagem.parecer,
        "decisao": triagem.decisao,
        "data_avaliacao": triagem.data_avaliacao.isoformat()
    }


def registrar(dados, id_usuario, perfis):
    _exigir_analista(perfis)
    match = match_repository.buscar_por_id(dados["id_match"])
    if not match:
        raise NaoEncontradoError("Match não encontrado.")
    if match.status_match != "VALIDADO":
        raise ConflitoError("Só é possível triar um match validado.")
    ideia = ideia_repository.buscar_por_id(match.id_ideia)
    if (ideia.status or "").strip().casefold() == "arquivada":
        raise ConflitoError("Não é possível triar uma ideia arquivada.")

    try:
        triagem = triagem_repository.adicionar(Triagem(
            id_match=match.id_match,
            id_avaliador=id_usuario,
            impacto=dados["impacto"],
            urgencia=dados["urgencia"],
            viabilidade=dados["viabilidade"],
            alinhamento=dados["alinhamento"],
            esforco=dados["esforco"],
            parecer=dados["parecer"],
            decisao=dados.get("decisao")
        ))
        # a ideia passa a "em avaliação"; a aprovação continua sendo uma ação humana separada
        if (ideia.status or "").strip().casefold() in ("submetida", "nova"):
            ideia_repository.alterar_status(ideia, "em_avaliacao")
        db.session.commit()
        db.session.refresh(triagem)
    except IntegrityError:
        db.session.rollback()
        raise ConflitoError("Não foi possível registrar a triagem com os dados informados.")

    return _triagem_para_dict(triagem, match.id_desafio, match.id_ideia)


def listar(filtros, page, page_size, perfis):
    _exigir_analista(perfis)
    linhas, total = triagem_repository.listar(filtros, page, page_size)
    return {
        "items": [_triagem_para_dict(*linha) for linha in linhas],
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": ceil(total / page_size) if total else 0
    }


def obter(id_triagem, perfis):
    _exigir_analista(perfis)
    linha = triagem_repository.buscar_por_id(id_triagem)
    if not linha:
        raise NaoEncontradoError("Triagem não encontrada.")
    return _triagem_para_dict(*linha)
