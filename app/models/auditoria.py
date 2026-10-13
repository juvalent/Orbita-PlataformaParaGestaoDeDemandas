from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import Base


class Auditoria(Base):
    __tablename__ = "auditoria"

    id_auditoria: Mapped[int] = mapped_column(primary_key=True)
    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuario.id_usuario"), nullable=False)
    entidade: Mapped[str] = mapped_column(String(50), nullable=False)
    id_registro: Mapped[int] = mapped_column(nullable=False)
    acao: Mapped[str] = mapped_column(String(50), nullable=False)
    detalhes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    data_hora: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
