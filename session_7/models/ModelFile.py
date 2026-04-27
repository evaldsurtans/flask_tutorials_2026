from models.Database import Base
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from sqlalchemy import String, ForeignKey, Text, JSON
from datetime import datetime

class ModelFile(Base):
    __tablename__ = "files"

    file_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.uuid"))
    filename: Mapped[str] = mapped_column(String(255))
    mime_type: Mapped[str] = mapped_column(String(255))
    storage_path: Mapped[str] = mapped_column(String(255))
    upload_date: Mapped[datetime] = mapped_column(default=func.now())
    post_id: Mapped[int | None] = mapped_column(ForeignKey("posts.post_id"))

    users: Mapped["ModelUser"] = relationship(back_populates="files")
    posts: Mapped["ModelPost"] = relationship(back_populates="files")