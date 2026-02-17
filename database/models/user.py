"""
User model
"""
from sqlalchemy import Column, BigInteger, String, DateTime, Boolean, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from database.models.base import Base

class User(Base):
    """User model for storing Telegram user data"""
    __tablename__ = "user"

    id = Column(BigInteger, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=True)
    username = Column(String, unique=True, nullable=True)
    language_code = Column(String, nullable=True)

    state = Column(String, default="language_select", index=True)
    state_data = Column(String, nullable=True) # json for complex data from states

    is_blocked = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)

    #indexing for common queries to make the bot run even faster
    __table_args__ = (
        Index("ix_users_active_role", "is_active"),
    )

    applications = relationship(
        "Application",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"
