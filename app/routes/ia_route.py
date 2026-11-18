"""Rotas REST autenticadas dos recursos de IA (consultivos)."""

from flask import Blueprint
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from flask_limiter.util import get_remote_address

from app.controllers import ia_controller
from app.extensions import limiter

bp = Blueprint("ia", __name__, url_prefix="/api/v1/ia")


@bp.before_request
def exigir_token():
    verify_jwt_in_request()


def _chave_por_usuario():
    """Cota individual: 10 requisições por minuto por usuário autenticado."""
    try:
        verify_jwt_in_request()
        return f"usuario:{get_jwt_identity()}"
    except Exception:
        return get_remote_address()


bp.add_url_rule(
    "/matches/sugerir-ia",
    view_func=limiter.limit("10 per minute", key_func=_chave_por_usuario)(
        ia_controller.sugerir_ia),
    methods=["POST"],
)
