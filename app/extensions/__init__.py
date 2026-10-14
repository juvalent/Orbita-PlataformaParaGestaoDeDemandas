from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Classe base de todos os models do projeto."""
    pass


db = SQLAlchemy(model_class=Base)
jwt = JWTManager()
