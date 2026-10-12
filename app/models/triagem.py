from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import Base


class Triagem(Base):
    __tablename__ = "triagem"

    id_triagem: Mapped[int] = mapped_column(primary_key=True)
    id_match: Mapped[int] = mapped_column(ForeignKey("match_ideia_desafio.id_match"), nullable=False)
    id_avaliador: Mapped[int] = mapped_column(ForeignKey("usuario.id_usuario"), nullable=False)
    impacto: Mapped[int] = mapped_column(Integer, nullable=False)
    urgencia: Mapped[int] = mapped_column(Integer, nullable=False)
    viabilidade: Mapped[int] = mapped_column(Integer, nullable=False)
    alinhamento: Mapped[int] = mapped_column(Integer, nullable=False)
    esforco: Mapped[int] = mapped_column(Integer, nullable=False)
    parecer: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    decisao: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    data_avaliacao: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
