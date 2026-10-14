from flask import Blueprint
from flask_jwt_extended import jwt_required

from app.controllers import auth_controller

bp = Blueprint("auth", __name__, url_prefix="/api/v1/auth")

bp.add_url_rule("/register", view_func=auth_controller.registrar,
                methods=["POST"])
bp.add_url_rule("/login", view_func=auth_controller.login, methods=["POST"])
bp.add_url_rule("/me", view_func=jwt_required()(auth_controller.me),
                methods=["GET"])
