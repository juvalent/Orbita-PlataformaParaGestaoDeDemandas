from flask import Blueprint

from app.controllers import desafio_controller

bp = Blueprint("desafio", __name__, url_prefix="/api/v1/desafio")

bp.add_url_rule("", view_func = desafio_controller.registrar, methods=["POST"])
bp.add_url_rule("", view_func = desafio_controller.listar, methods=["GET"])
bp.add_url_rule("/<int:id_desafio>", view_func = desafio_controller.remover, methods=["DELETE"])
bp.add_url_rule("/<int:id_desafio>", view_func = desafio_controller.atualizar, methods=["PUT", "PATCH"])
