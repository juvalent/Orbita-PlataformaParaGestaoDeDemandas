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
    app.json.ensure_ascii = False  

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=2)

    if config:
        app.config.update(config)

    if not app.config["SQLALCHEMY_DATABASE_URI"]:
        raise RuntimeError("Defina DATABASE_URL no arquivo .env")
    if not app.config["JWT_SECRET_KEY"]:
        raise RuntimeError("Defina JWT_SECRET_KEY no arquivo .env")

    CORS(app)
    db.init_app(app)
    jwt.init_app(app)


    from app import models


    registrar_error_handlers(app)

    from app.routes import bp_auth, bp_health, bp_desafio
    app.register_blueprint(bp_health)
    app.register_blueprint(bp_auth)
    app.register_blueprint(bp_desafio)

    return app
