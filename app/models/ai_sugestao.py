import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String, Uuid, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import Base


class AiSugestao(Base):
    """Sugestão gerada pela IA. Fica PENDENTE até um humano revisar."""
    __tablename__ = "ai_sugestao"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    id_desafio: Mapped[int] = mapped_column(ForeignKey("desafio.id_desafio", ondelete="CASCADE"), nullable=False)
    id_ideia: Mapped[int] = mapped_column(ForeignKey("ideia.id_ideia", ondelete="CASCADE"), nullable=False)
    id_match: Mapped[Optional[int]] = mapped_column(ForeignKey("match_ideia_desafio.id_match", ondelete="SET NULL"), nullable=True)
    solicitado_por_id: Mapped[int] = mapped_column(ForeignKey("usuario.id_usuario"), nullable=False)
    sugestao: Mapped[dict] = mapped_column(JSONB, nullable=False)  # {scoreCompatibilidade, justificativa}
    modelo_versao: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    status_revisao: Mapped[str] = mapped_column(String(20), nullable=False, default="PENDENTE")
    revisado_por_id: Mapped[Optional[int]] = mapped_column(ForeignKey("usuario.id_usuario"), nullable=True)
    data_criacao: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    data_revisao: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
