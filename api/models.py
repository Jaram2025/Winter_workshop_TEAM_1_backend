from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import Boolean, Integer, String

from .database import Base


class FileModel(Base):
    """Model for file"""
    __tablename__ = "files"

    id = Column(String(255), primary_key=True)
    name = Column(String(255), index=True)
    path = Column(String(512))
    size = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)


class User(Base):
    """Model for user."""
    __tablename__ = "user"

    id: Mapped[str] = mapped_column(String(200), primary_key=True)
    email: Mapped[str] = mapped_column(String(200), unique=False)  # noqa: WPS432
    password: Mapped[str] = mapped_column(String(200), nullable=False)  # noqa: WPS432
    first_name: Mapped[str] = mapped_column(
        String(length=200),  # noqa: WPS432
        nullable=False,
    )
    last_name: Mapped[str] = mapped_column(
        String(length=200),  # noqa: WPS432
        nullable=False,
    )
  
