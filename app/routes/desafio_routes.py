"""Rotas REST autenticadas do CRUD de desafios."""

from flask import Blueprint
from flask_jwt_extended import verify_jwt_in_request

from app.controllers import desafio_controller

bp = Blueprint("desafio", __name__, url_prefix="/api/v1/desafios")


@bp.before_request
def exigir_token():
    verify_jwt_in_request()


bp.add_url_rule("", view_func=desafio_controller.registrar, methods=["POST"])
bp.add_url_rule("", view_func=desafio_controller.listar, methods=["GET"])
bp.add_url_rule("/<int:id_desafio>", view_func=desafio_controller.obter, methods=["GET"])
bp.add_url_rule("/<int:id_desafio>", view_func=desafio_controller.remover, methods=["DELETE"])
bp.add_url_rule("/<int:id_desafio>", view_func=desafio_controller.atualizar, methods=["PUT", "PATCH"])
