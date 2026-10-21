from flask import jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity

from app.schemas.ideia_schema import (IdeiaAtualizarSchema, IdeiaCriarSchema,
                                      IdeiaFiltroSchema)
from app.services import ideia_service


def _json_da_requisicao():
    return request.get_json(silent=True) or {}


def _id_usuario_logado():
    return int(get_jwt_identity())


def _perfis_do_token():
    return get_jwt().get("perfis", [])


def listar():
    filtros = IdeiaFiltroSchema().load(request.args)
    page = filtros.pop("page")
    page_size = filtros.pop("page_size")
    return jsonify(ideia_service.listar(filtros, page, page_size)), 200


def criar():
    dados = IdeiaCriarSchema().load(_json_da_requisicao())
    return jsonify(ideia_service.criar(dados, _id_usuario_logado())), 201


def obter(id_ideia):
    return jsonify(ideia_service.obter(id_ideia)), 200


def atualizar(id_ideia):
    dados = IdeiaAtualizarSchema().load(_json_da_requisicao())
    ideia = ideia_service.atualizar(id_ideia, dados, _id_usuario_logado(),
                                    _perfis_do_token())
    return jsonify(ideia), 200


def aprovar(id_ideia):
    return jsonify(ideia_service.aprovar(id_ideia, _perfis_do_token())), 200


def arquivar(id_ideia):
    return jsonify(ideia_service.arquivar(id_ideia, _perfis_do_token())), 200
