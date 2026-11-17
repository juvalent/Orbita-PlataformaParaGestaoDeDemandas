"""Rotas REST autenticadas da Triagem/Priorização."""

from flask import Blueprint
from flask_jwt_extended import verify_jwt_in_request

from app.controllers import triagem_controller

bp = Blueprint("triagem", __name__, url_prefix="/api/v1/triagens")


@bp.before_request
def exigir_token():
    verify_jwt_in_request()


bp.add_url_rule("", view_func=triagem_controller.registrar, methods=["POST"])
bp.add_url_rule("", view_func=triagem_controller.listar, methods=["GET"])
bp.add_url_rule("/<int:id_triagem>", view_func=triagem_controller.obter, methods=["GET"])
