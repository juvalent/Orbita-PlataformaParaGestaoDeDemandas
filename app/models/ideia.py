from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import Base


class Ideia(Base):
    __tablename__ = "ideia"

    id_ideia: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[Optional[str]] = mapped_column(String(30), unique=True, nullable=True)
    id_autor: Mapped[int] = mapped_column(ForeignKey("usuario.id_usuario"), nullable=False)
    id_desafio: Mapped[int] = mapped_column(ForeignKey("desafio.id_desafio"), nullable=False)
    titulo: Mapped[str] = mapped_column(String(150), nullable=False)
    descricao: Mapped[str] = mapped_column(Text, nullable=False)
    area: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    categoria: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    problema_resolvido: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    beneficio_esperado: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="submetida")
    data_criacao: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    data_atualizacao: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
