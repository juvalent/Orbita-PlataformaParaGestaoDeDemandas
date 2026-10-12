from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import Base


class Projeto(Base):
    __tablename__ = "projeto"

    id_projeto: Mapped[int] = mapped_column(primary_key=True)
    id_match: Mapped[int] = mapped_column(ForeignKey("match_ideia_desafio.id_match"), nullable=False, unique=True)
    id_responsavel: Mapped[int] = mapped_column(ForeignKey("usuario.id_usuario"), nullable=False)
    titulo: Mapped[str] = mapped_column(String(150), nullable=False)
    descricao: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status_kanban: Mapped[str] = mapped_column(String(30), nullable=False,default="Aprovado")
    data_criacao: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    data_atualizacao: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
