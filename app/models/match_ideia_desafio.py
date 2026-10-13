from datetime import datetime
from typing import Optional

from sqlalchemy import (String, Text, Float, DateTime, ForeignKey, UniqueConstraint, func)
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import Base


class MatchIdeiaDesafio(Base):
    __tablename__ = "match_ideia_desafio"

    # a mesma ideia não pode ser ligada duas vezes ao mesmo desafio
    __table_args__ = (UniqueConstraint("id_desafio", "id_ideia"),)

    id_match: Mapped[int] = mapped_column(primary_key=True)
    id_desafio: Mapped[int] = mapped_column(ForeignKey("desafio.id_desafio"), nullable=False)
    id_ideia: Mapped[int] = mapped_column(ForeignKey("ideia.id_ideia"), nullable=False)
    id_validado_por: Mapped[Optional[int]] = mapped_column(ForeignKey("usuario.id_usuario"), nullable=True)
    score_compatibilidade: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    justificativa: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    origem_match: Mapped[str] = mapped_column(String(20), nullable=False, default="manual")
    status_match: Mapped[str] = mapped_column(String(20), nullable=False, default="PENDENTE")
    data_criacao: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    data_validacao: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
