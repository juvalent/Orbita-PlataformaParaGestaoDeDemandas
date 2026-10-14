from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity

from app.schemas.auth_schema import LoginSchema, RegistroSchema
from app.services import auth_service


def _json_da_requisicao():
    return request.get_json(silent=True) or {}


def registrar():
    dados = RegistroSchema().load(_json_da_requisicao())
    return jsonify(auth_service.registrar(dados)), 201


def login():
    dados = LoginSchema().load(_json_da_requisicao())
    return jsonify(auth_service.login(dados)), 200


def me():
    usuario = auth_service.obter_usuario_logado(get_jwt_identity())
    return jsonify(usuario), 200
