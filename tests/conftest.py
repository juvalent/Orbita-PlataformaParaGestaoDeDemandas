"""Testes de integração da camada de IA. Exigem PostgreSQL com pgvector.

    TEST_DATABASE_URL=postgresql+psycopg2://u:s@127.0.0.1:5433/orbita_test pytest tests -q

ATENÇÃO: o banco informado é APAGADO (drop_all) ao fim da sessão. Por isso o
teste se recusa a rodar se o nome do banco não terminar em "_test".
"""
import os

import pytest
from sqlalchemy import text

URL = os.getenv("TEST_DATABASE_URL")


@pytest.fixture(scope="session")
def app():
    if not URL:
        pytest.skip("defina TEST_DATABASE_URL")
    if not URL.rsplit("/", 1)[-1].split("?")[0].endswith("_test"):
        pytest.exit("TEST_DATABASE_URL deve apontar para um banco *_test "
                    "(os testes apagam as tabelas).", returncode=2)
    from app import create_app
    from app.extensions import db, limiter
    # a URL do teste entra no create_app: não depende do DATABASE_URL do .env
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": URL,
                      "JWT_SECRET_KEY": "teste-com-mais-de-32-caracteres-123"})
    with app.app_context():
        db.session.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        db.session.commit()
        db.drop_all()
        db.create_all()
    yield app
    with app.app_context():
        db.drop_all()


@pytest.fixture(autouse=True)
def ambiente_ia(monkeypatch):
    """Fixa a config de IA dos testes (não depende do .env de ninguém)."""
    for chave, valor in {
        "AI_EMBEDDING_PROVIDER": "api",
        "AI_API_KEY": "k", "AI_BASE_URL": "http://llm.test/v1",
        "AI_MODEL_NAME": "llama-test", "AI_TIMEOUT_SECONDS": "10",
        "AI_EMBEDDING_BASE_URL": "http://emb.test/v1",
        "AI_EMBEDDING_API_KEY": "k", "AI_EMBEDDING_MODEL": "emb-test",
    }.items():
        monkeypatch.setenv(chave, valor)
