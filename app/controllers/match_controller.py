from flask import jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity

from app.schemas.match_schema import (MatchCriarSchema, MatchFiltroSchema,
                                      MatchSugestaoSchema, MatchValidacaoSchema)
from app.services import match_service

def _json_da_requisicao():
    return request.get_json(silent=True) or {}

def _id_usuario_logado():
    return int(get_jwt_identity())

def _perfis_do_token():
    return get_jwt().get("perfis", [])

def registrar():
    dados = MatchCriarSchema().load(_json_da_requisicao())
    return jsonify(match_service.registrar(dados, _perfis_do_token())), 201

def listar():
    filtros = MatchFiltroSchema().load(request.args)
    page = filtros.pop("page")
    page_size = filtros.pop("page_size")
    return jsonify(match_service.listar(filtros, page, page_size, _perfis_do_token())), 200

def sugerir_por_regra():
    dados = MatchSugestaoSchema().load(_json_da_requisicao())
    return jsonify(match_service.sugerir_por_regra(dados, _perfis_do_token())), 201

def validar(id_match):
    dados = MatchValidacaoSchema().load(_json_da_requisicao())
    return jsonify(match_service.validar(id_match, dados, _id_usuario_logado(), _perfis_do_token())), 200
