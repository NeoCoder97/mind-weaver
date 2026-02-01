"""
Base class for SQLAlchemy ORM models.

This module is imported by all model modules to avoid circular imports.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""

    pass
