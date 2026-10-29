from flask import jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity

from app.schemas.desafio_schema import DesafioSchema
from app.services import desafio_service

def __json_da_requisicao():
    return request.get_json(silent=True) or {}

def _id_usuario_logado():
    return int(get_jwt_identity())

def _perfis_do_token():
    return get_jwt().get("perfis", [])

def registrar():
    dados = DesafioSchema().load(__json_da_requisicao())
    return jsonify(desafio_service.registrar(dados, _id_usuario_logado(), _perfis_do_token())), 201

def listar():
    desafios = desafio_service.listar()
    return jsonify(desafios), 200

def remover(id_desafio):
    desafio_service.remover(id_desafio, _id_usuario_logado(), _perfis_do_token())
    return "", 204

def atualizar(id_desafio):
    dados = DesafioSchema(partial=True).load(__json_da_requisicao())
    return jsonify(desafio_service.atualizar(id_desafio, dados, _id_usuario_logado(), _perfis_do_token())), 200
