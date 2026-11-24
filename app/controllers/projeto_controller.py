from flask import jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity

from app.schemas.projeto_schema import (ProjetoAtualizarSchema, ProjetoCriarSchema,
                                        ProjetoFiltroSchema, ProjetoKanbanSchema)
from app.services import projeto_service


def _id_usuario_logado():
    return int(get_jwt_identity())


def _perfis_do_token():
    return get_jwt().get("perfis", [])


def criar():
    dados = ProjetoCriarSchema().load(request.get_json(silent=True) or {})
    return jsonify(projeto_service.criar(dados, _id_usuario_logado(), _perfis_do_token())), 201


def listar():
    filtros = ProjetoFiltroSchema().load(request.args)
    page = filtros.pop("page")
    page_size = filtros.pop("page_size")
    return jsonify(projeto_service.listar(filtros, page, page_size, _id_usuario_logado(), _perfis_do_token())), 200


def obter(id_projeto):
    return jsonify(projeto_service.obter(id_projeto, _id_usuario_logado(), _perfis_do_token())), 200


def atualizar(id_projeto):
    dados = ProjetoAtualizarSchema().load(request.get_json(silent=True) or {})
    return jsonify(projeto_service.atualizar(id_projeto, dados, _id_usuario_logado(), _perfis_do_token())), 200


def movimentar(id_projeto):
    dados = ProjetoKanbanSchema().load(request.get_json(silent=True) or {})
    return jsonify(projeto_service.movimentar(id_projeto, dados["etapa"], _id_usuario_logado(), _perfis_do_token())), 200
