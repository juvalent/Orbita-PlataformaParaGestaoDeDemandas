from flask import jsonify
from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException

from app.errors import AppError
from app.extensions import db, jwt


def registrar_error_handlers(app):
    """Todas as respostas de erro da API saem em JSON, no mesmo formato."""

    @app.errorhandler(ValidationError)
    def erro_validacao(e):
        return jsonify({"erro": "Dados inválidos.",
                        "campos": e.messages}), 422

    @app.errorhandler(AppError)
    def erro_de_negocio(e):
        return jsonify({"erro": e.mensagem}), e.status_code

    @app.errorhandler(HTTPException)
    def erro_http(e):
        return jsonify({"erro": e.description}), e.code

    @app.errorhandler(Exception)
    def erro_inesperado(e):
        db.session.rollback()
        app.logger.exception(e)
        return jsonify({"erro": "Erro interno. Tente novamente mais "
                                "tarde."}), 500

    # Erros do JWT (token ausente, inválido ou expirado)
    @jwt.unauthorized_loader
    def token_ausente(motivo):
        return jsonify({"erro": "Token de acesso ausente."}), 401

    @jwt.invalid_token_loader
    def token_invalido(motivo):
        return jsonify({"erro": "Token inválido."}), 401

    @jwt.expired_token_loader
    def token_expirado(header, payload):
        return jsonify({"erro": "Token expirado. Faça login novamente."}), 401
