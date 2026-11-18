"""Rotas REST autenticadas do Match (vínculo Ideia × Desafio)."""

from flask import Blueprint
from flask_jwt_extended import jwt_required

from app.controllers import match_controller

bp_match = Blueprint("match", __name__, url_prefix="/api/v1/matches")

bp_match.add_url_rule(
    "",
    view_func=jwt_required()(match_controller.listar),
    methods=["GET"],
)
bp_match.add_url_rule(
    "",
    view_func=jwt_required()(match_controller.criar),
    methods=["POST"],
)
bp_match.add_url_rule(
    "/<int:id_match>",
    view_func=jwt_required()(match_controller.obter),
    methods=["GET"],
)
