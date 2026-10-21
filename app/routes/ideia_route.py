"""Rotas REST autenticadas do CRUD de ideias."""

from flask import Blueprint
from flask_jwt_extended import jwt_required

from app.controllers import ideia_controller

bp_ideia = Blueprint("ideia", __name__, url_prefix="/api/v1/ideias")

bp_ideia.add_url_rule(
    "",
    view_func=jwt_required()(ideia_controller.listar),
    methods=["GET"],
)
bp_ideia.add_url_rule(
    "",
    view_func=jwt_required()(ideia_controller.criar),
    methods=["POST"],
)
bp_ideia.add_url_rule(
    "/<int:id_ideia>",
    view_func=jwt_required()(ideia_controller.obter),
    methods=["GET"],
)
bp_ideia.add_url_rule(
    "/<int:id_ideia>",
    view_func=jwt_required()(ideia_controller.atualizar),
    methods=["PATCH", "PUT"],  # o contrato do PDF fala em PUT; aceita parcial
)
bp_ideia.add_url_rule(
    "/<int:id_ideia>",
    view_func=jwt_required()(ideia_controller.arquivar),
    endpoint="arquivar_delete",  # nome próprio: o POST /arquivar usa "arquivar"
    methods=["DELETE"],  # DELETE = arquivar (a ideia não é apagada do banco)
)
bp_ideia.add_url_rule(
    "/<int:id_ideia>/aprovar",
    view_func=jwt_required()(ideia_controller.aprovar),
    methods=["POST"],
)
bp_ideia.add_url_rule(
    "/<int:id_ideia>/arquivar",
    view_func=jwt_required()(ideia_controller.arquivar),
    methods=["POST"],
)
