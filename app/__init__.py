import os
from datetime import timedelta

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

from app.extensions import db, jwt
from app.middlewares.error_handler import registrar_error_handlers

load_dotenv()


def create_app(config=None):
    app = Flask(__name__)
    app.json.ensure_ascii = False  # acentos legíveis no JSON

    # Valores vêm do arquivo .env (veja o .env.example)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=2)

    if config:  # usado nos testes para trocar o banco, por exemplo
        app.config.update(config)

    if not app.config["SQLALCHEMY_DATABASE_URI"]:
        raise RuntimeError("Defina DATABASE_URL no arquivo .env")
    if not app.config["JWT_SECRET_KEY"]:
        raise RuntimeError("Defina JWT_SECRET_KEY no arquivo .env")

    CORS(app)  # permite o front React chamar a API
    db.init_app(app)
    jwt.init_app(app)

    # Importar os models faz o SQLAlchemy conhecer todas as tabelas
    from app import models  # noqa: F401

    registrar_error_handlers(app)

    from app.routes import bp_auth, bp_health
    app.register_blueprint(bp_health)
    app.register_blueprint(bp_auth)

    return app
