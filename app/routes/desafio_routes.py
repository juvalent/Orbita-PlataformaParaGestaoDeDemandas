"""Rotas REST autenticadas do CRUD de desafios."""

from flask import Blueprint
from flask_jwt_extended import jwt_required

from app.controllers import desafio_controller

bp = Blueprint("desafio", __name__, url_prefix="/api/v1/desafio")

bp.add_url_rule("/add", view_func=jwt_required()(desafio_controller.registrar), methods=["POST"])
bp.add_url_rule("/listar_todos", view_func=jwt_required()(desafio_controller.listar), methods=["GET"])
bp.add_url_rule("/delete/<int:id_desafio>", view_func=jwt_required()(desafio_controller.remover), methods=["DELETE"])
bp.add_url_rule("/update/<int:id_desafio>", view_func=jwt_required()(desafio_controller.atualizar), methods=["PUT", "PATCH"])
