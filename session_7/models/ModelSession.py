from models.Database import Base
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from sqlalchemy import String, Integer, ForeignKey, Text, TIMESTAMP
from datetime import datetime

class ModelSession(Base):
    __tablename__ = 'sessions'

    session_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.uuid'))
    token: Mapped[str] = mapped_column(String(255))
    expires_at: Mapped[datetime] = mapped_column(TIMESTAMP)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(default=func.now())

    users: Mapped["ModelUser"] = relationship(back_populates="sessions")