from datetime import datetime
from typing import Optional

from sqlalchemy import Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import Base


class Resultado(Base):
    __tablename__ = "resultado"

    id_resultado: Mapped[int] = mapped_column(primary_key=True)
    id_projeto: Mapped[int] = mapped_column(ForeignKey("projeto.id_projeto"), nullable=False)
    id_mvp: Mapped[Optional[int]] = mapped_column(ForeignKey("mvp.id_mvp"), nullable=False)
    descricao: Mapped[str] = mapped_column(Text, nullable=False)
    observacao: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    data_registro: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
