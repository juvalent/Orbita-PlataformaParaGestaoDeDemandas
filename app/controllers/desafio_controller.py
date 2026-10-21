from flask import jsonify, request

from app.schemas.desafio_schema import DesafioSchema
from app.services import desafio_service

def __json_da_requisicao():
    return request.get_json(silent=True) or {}

def registrar():
    dados = DesafioSchema().load(__json_da_requisicao())
    return jsonify(desafio_service.registrar(dados)), 201

def listar():
    desafios = desafio_service.listar()
    return jsonify(desafios), 200

def remover(id_desafio):
    desafio_service.remover(id_desafio)
    return "", 204
