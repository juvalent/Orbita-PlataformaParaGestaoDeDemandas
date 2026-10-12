from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import Base


class Mvp(Base):
    __tablename__ = "mvp"

    id_mvp: Mapped[int] = mapped_column(primary_key=True)
    id_projeto: Mapped[int] = mapped_column(ForeignKey("projeto.id_projeto"), nullable=False)
    objetivo_hipotese: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="planejado")
    resultado_validacao: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    data_criacao: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
