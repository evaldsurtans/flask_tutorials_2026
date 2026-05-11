from models.Database import Base
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from sqlalchemy import String, ForeignKey
from datetime import datetime


class ModelTags(Base):
    __tablename__ = "tags"

    tag_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tag_name: Mapped[str] = mapped_column(String(255))

    post_tags: Mapped[list["ModelPostTags"]] = relationship(back_populates="tags")
