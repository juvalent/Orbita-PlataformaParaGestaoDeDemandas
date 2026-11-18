import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (CheckConstraint, DateTime, ForeignKey, SmallInteger,
                        Text, Uuid, func)
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import Base


class AiFeedback(Base):
    """Avaliação humana de uma sugestão (auditoria de acurácia da IA)."""
    __tablename__ = "ai_feedback"

    __table_args__ = (
        CheckConstraint("nota BETWEEN 1 AND 5", name="ck_ai_feedback_nota"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    sugestao_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ai_sugestao.id", ondelete="CASCADE"), nullable=False)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuario.id_usuario"), nullable=False)
    nota: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    motivo_rejeicao: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    data_criacao: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
