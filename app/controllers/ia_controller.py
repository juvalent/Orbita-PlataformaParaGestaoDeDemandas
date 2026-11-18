from flask import jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity

from app.schemas.ia_schema import SugerirMatchSchema
from app.services import ia_match_service
from app.services.match_service import _exigir_analista


def _json_da_requisicao():
    return request.get_json(silent=True) or {}


def sugerir_ia():
    """Sugere matches Desafio x Ideia com IA. Tudo nasce PENDENTE: a decisão
    é humana, em POST /api/v1/matches/<id>/validacao."""
    _exigir_analista(get_jwt().get("perfis", []))
    dados = SugerirMatchSchema().load(_json_da_requisicao())
    resultado = ia_match_service.sugerir_matches(
        dados["id_desafio"], dados["top_n"], int(get_jwt_identity()))
    return jsonify(resultado), 200
