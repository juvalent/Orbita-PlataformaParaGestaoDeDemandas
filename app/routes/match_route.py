"""Rotas REST autenticadas do Match entre ideia e desafio."""

from flask import Blueprint
from flask_jwt_extended import verify_jwt_in_request

from app.controllers import match_controller

bp = Blueprint("match", __name__, url_prefix="/api/v1/matches")


@bp.before_request
def exigir_token():
    verify_jwt_in_request()


bp.add_url_rule("", view_func=match_controller.registrar, methods=["POST"])
bp.add_url_rule("", view_func=match_controller.listar, methods=["GET"])
bp.add_url_rule("/<int:id_match>", view_func=match_controller.obter, methods=["GET"])
bp.add_url_rule("/sugerir-regra", view_func=match_controller.sugerir_por_regra, methods=["POST"])
bp.add_url_rule("/<int:id_match>/validacao", view_func=match_controller.validar, methods=["POST"])
