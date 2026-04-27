from typing import List

from models.ModelFile import ModelFile
from models.Database import Base
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import String, Integer, ForeignKey

class ModelUser(Base):
    __tablename__ = 'users'

    uuid: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(256), unique=True)
    password: Mapped[str] = mapped_column(String(256))

    files: Mapped[List["ModelFile"]] = relationship(back_populates="users")
    posts: Mapped[List["ModelPost"]] = relationship(back_populates="users")
    sessions: Mapped[List["ModelSession"]] = relationship(back_populates="users")