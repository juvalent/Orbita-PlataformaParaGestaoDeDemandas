from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import Base


class Desafio(Base):
    __tablename__ = "desafio"

    id_desafio: Mapped[int] = mapped_column(primary_key=True)
    id_responsavel: Mapped[int] = mapped_column(ForeignKey("usuario.id_usuario"), nullable=False)
    titulo: Mapped[str] = mapped_column(String(150), nullable=False)
    descricao_problema: Mapped[str] = mapped_column(Text, nullable=False)
    area_demandante: Mapped[str] = mapped_column(String(100), nullable=False)
    quem_afeta: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    impacto: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    urgencia: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    categoria: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="aberto")
    data_criacao: Mapped[datetime] = mapped_column(DateTime,server_default=func.now())
    data_atualizacao: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
