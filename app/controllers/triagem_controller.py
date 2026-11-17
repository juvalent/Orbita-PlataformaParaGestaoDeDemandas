from flask import jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity

from app.schemas.triagem_schema import TriagemCriarSchema, TriagemFiltroSchema
from app.services import triagem_service

def _json_da_requisicao():
    return request.get_json(silent=True) or {}

def _id_usuario_logado():
    return int(get_jwt_identity())

def _perfis_do_token():
    return get_jwt().get("perfis", [])

def registrar():
    dados = TriagemCriarSchema().load(_json_da_requisicao())
    return jsonify(triagem_service.registrar(dados, _id_usuario_logado(), _perfis_do_token())), 201

def listar():
    filtros = TriagemFiltroSchema().load(request.args)
    page = filtros.pop("page")
    page_size = filtros.pop("page_size")
    return jsonify(triagem_service.listar(filtros, page, page_size, _perfis_do_token())), 200

def obter(id_triagem):
    return jsonify(triagem_service.obter(id_triagem, _perfis_do_token())), 200
