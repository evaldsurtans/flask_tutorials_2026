from models.Database import Base
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.ext.associationproxy import association_proxy, AssociationProxy
from sqlalchemy.sql import func
from sqlalchemy import String, ForeignKey, Text, JSON
from datetime import datetime


from models.EnumPostStatus import EnumPostStatus

class ModelPost(Base):
    __tablename__ = 'posts'
    post_id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(512))
    body: Mapped[str] = mapped_column(String(5000)) # around 1k words
    created: Mapped[datetime] = mapped_column(default=func.now())
    modified: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())
    url_slug: Mapped[str] = mapped_column(String(128))
    thumbnail_uuid: Mapped[str | None] = mapped_column(String(256)) # not used
    status: Mapped[EnumPostStatus | None] = mapped_column(default=EnumPostStatus.not_set) # not used
    parent_post_id: Mapped[int | None] = mapped_column(ForeignKey("posts.post_id"), default=None) # not used
    owner_uuid: Mapped[int] = mapped_column(ForeignKey("users.uuid"))

    users: Mapped["ModelUser"] = relationship(back_populates="posts")
    files: Mapped[list["ModelFile"]] = relationship(back_populates="posts")
    post_tags: Mapped[list["ModelTagsInPost"]] = relationship(back_populates="posts", cascade="all, delete-orphan")
    tag_names: AssociationProxy[list[str]] = association_proxy("post_tags", "tag_name_attr")

    def __init__(self):
        super().__init__()
        self.post_id = None
        self.title = ""
        self.body = ""
        self.tags = ""
        self.url_slug = ""

