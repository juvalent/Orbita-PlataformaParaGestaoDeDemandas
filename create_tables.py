from sqlalchemy import text

from app import create_app
from app.extensions import db

app = create_app()

with app.app_context():
    # pgvector precisa existir antes das tabelas ai_* (coluna VECTOR e índice HNSW)
    db.session.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    db.session.commit()
    db.create_all()
    print("Tabelas criadas com sucesso!")
