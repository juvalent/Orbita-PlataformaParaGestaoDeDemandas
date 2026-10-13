from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import Base


class UsuarioPerfil(Base):
    __tablename__ = "usuario_perfil"

    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuario.id_usuario"), primary_key=True)
    id_perfil: Mapped[int] = mapped_column(ForeignKey("perfil.id_perfil"), primary_key=True)
