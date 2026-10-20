from flask import Blueprint
from flask_jwt_extended import jwt_required

from app.controllers import auth_controller
from app.extensions import limiter

bp = Blueprint("auth", __name__, url_prefix="/api/v1/auth")


LIMITE_LOGIN = "5 per minute" 
LIMITE_CADASTRO = "3 per minute" 

bp.add_url_rule("/register",
                view_func=limiter.limit(LIMITE_CADASTRO)(
                    auth_controller.registrar),
                methods=["POST"])
bp.add_url_rule("/login",
                view_func=limiter.limit(LIMITE_LOGIN)(auth_controller.login),
                methods=["POST"])
bp.add_url_rule("/me", view_func=jwt_required()(auth_controller.me),
                methods=["GET"])
