from flask import jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity

from app.schemas.match_schema import MatchCriarSchema, MatchFiltroSchema
from app.services import match_service


def _json_da_requisicao():
    return request.get_json(silent=True) or {}


def _id_usuario_logado():
    return int(get_jwt_identity())


def _perfis_do_token():
    return get_jwt().get("perfis", [])


def listar():
    filtros = MatchFiltroSchema().load(request.args)
    page = filtros.pop("page")
    page_size = filtros.pop("page_size")
    resultado = match_service.listar(filtros, page, page_size,
                                     _perfis_do_token())
    return jsonify(resultado), 200


def obter(id_match):
    return jsonify(match_service.obter(id_match, _perfis_do_token())), 200


def criar():
    dados = MatchCriarSchema().load(_json_da_requisicao())
    match = match_service.criar(dados, _id_usuario_logado(),
                                _perfis_do_token())
    return jsonify(match), 201
