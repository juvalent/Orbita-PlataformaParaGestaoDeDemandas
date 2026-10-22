import os

from dotenv import load_dotenv
from flask import Flask

from app.extensions import db

load_dotenv()


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")

    db.init_app(app)

    from app import models

    from app.routes import bp_auth, bp_health, bp_ideia

    registrar_error_handlers(app)

    from app.routes import bp_auth, bp_health, bp_desafio
    app.register_blueprint(bp_health)
    app.register_blueprint(bp_ideia)
    app.register_blueprint(bp_auth)
    app.register_blueprint(bp_desafio)

    return app
