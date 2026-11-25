from flask import Blueprint
from flask_jwt_extended import verify_jwt_in_request

from app.controllers import projeto_controller

bp_projeto = Blueprint("projeto", __name__, url_prefix="/api/v1/projetos")


@bp_projeto.before_request
def exigir_token():
    verify_jwt_in_request()


bp_projeto.add_url_rule("", view_func=projeto_controller.criar, methods=["POST"])
bp_projeto.add_url_rule("", view_func=projeto_controller.listar, methods=["GET"])
bp_projeto.add_url_rule("/<int:id_projeto>", view_func=projeto_controller.obter, methods=["GET"])
bp_projeto.add_url_rule("/<int:id_projeto>", view_func=projeto_controller.atualizar, methods=["PATCH", "PUT"])
bp_projeto.add_url_rule("/<int:id_projeto>/kanban", view_func=projeto_controller.movimentar, methods=["PATCH"])
