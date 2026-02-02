"""
Base model class
"""
from datetime import datetime

from sqlalchemy import Column, DateTime
from sqlalchemy.orm import DeclarativeBase, declared_attr


class Base(DeclarativeBase):
    """Base class for all models"""

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + "s"

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
