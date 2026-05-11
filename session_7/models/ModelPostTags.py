from models.Database import Base
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from sqlalchemy import String, ForeignKey
from datetime import datetime


class ModelPostTags(Base):
    __tablename__ = "post_tags"

    post_id: Mapped[int] = mapped_column(ForeignKey("posts.post_id"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.tag_id"), primary_key=True)

    posts: Mapped["ModelPost"] = relationship(back_populates="post_tags")
    tags: Mapped["ModelTags"] = relationship(back_populates="post_tags")

    @property
    def tag_name_attr(self):
        return self.tags.tag_name