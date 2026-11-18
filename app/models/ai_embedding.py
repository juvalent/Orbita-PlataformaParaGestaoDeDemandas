import uuid
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import (DateTime, Index, Integer, String, UniqueConstraint,
                        Uuid, func)
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import Base

# Dimensão fixa do vetor no banco (contrato do PDF: VECTOR(1536)).
EMBEDDING_DIM = 1536


class AiEmbedding(Base):
    """Vetor de um desafio ou de uma ideia, usado na busca semântica."""
    __tablename__ = "ai_embedding"

    __table_args__ = (
        UniqueConstraint("entidade_tipo", "entidade_id",
                         name="uq_ai_embedding_entidade"),
        Index("ix_ai_embedding_hash", "hash_conteudo"),
        # busca por similaridade de cosseno em sub-milissegundos
        Index("ix_ai_embedding_vetor_hnsw", "vetor",
              postgresql_using="hnsw",
              postgresql_ops={"vetor": "vector_cosine_ops"}),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    entidade_tipo: Mapped[str] = mapped_column(String(20), nullable=False)  # "desafio" | "ideia"
    entidade_id: Mapped[int] = mapped_column(Integer, nullable=False)
    hash_conteudo: Mapped[str] = mapped_column(String(64), nullable=False)  # SHA-256 do texto
    modelo_embedding: Mapped[str] = mapped_column(String(100), nullable=False)
    vetor = mapped_column(Vector(EMBEDDING_DIM), nullable=False)
    data_criacao: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    data_atualizacao: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
