from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import Base


class MovimentacaoKanban(Base):
    __tablename__ = "movimentacao_kanban"

    id_movimentacao: Mapped[int] = mapped_column(primary_key=True)
    id_projeto: Mapped[int] = mapped_column(ForeignKey("projeto.id_projeto"), nullable=False)
    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuario.id_usuario"), nullable=False)
    etapa_origem: Mapped[Optional[str]] = mapped_column(String(30), nullable=False)
    etapa_destino: Mapped[str] = mapped_column(String(30), nullable=False)
    data_movimentacao: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
