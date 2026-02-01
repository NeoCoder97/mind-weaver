"""
Category data model for organizing feeds into groups.
"""

from datetime import datetime
from typing import Optional, TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import Boolean, DateTime, Integer, String, Table, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from spider_aggregation.models.base import Base

if TYPE_CHECKING:
    from spider_aggregation.models.feed import FeedModel


class CategoryModel(Base):
    """SQLAlchemy ORM model for Category."""

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    color: Mapped[Optional[str]] = mapped_column(String(7), nullable=True)  # Hex color for UI
    icon: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # Icon name/class
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationship to Feeds (many-to-many)
    feeds: Mapped[list["FeedModel"]] = relationship(
        "FeedModel",
        secondary="feed_categories",
        back_populates="categories",
    )

    def __repr__(self) -> str:
        return f"<CategoryModel(id={self.id}, name='{self.name}')>"


# Pydantic models for API


class CategoryBase(BaseModel):
    """Base Category schema."""

    name: str = Field(..., max_length=100, description="Category name")
    description: Optional[str] = Field(None, description="Category description")
    color: Optional[str] = Field(
        None, max_length=7, pattern="^#[0-9A-Fa-f]{6}$", description="Hex color code"
    )
    icon: Optional[str] = Field(None, max_length=50, description="Icon name or class")
    enabled: bool = Field(default=True, description="Whether the category is enabled")


class CategoryCreate(CategoryBase):
    """Schema for creating a new category."""

    pass


class CategoryUpdate(BaseModel):
    """Schema for updating a category."""

    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    color: Optional[str] = Field(None, max_length=7, pattern="^#[0-9A-Fa-f]{6}$")
    icon: Optional[str] = Field(None, max_length=50)
    enabled: Optional[bool] = None


class CategoryResponse(CategoryBase):
    """Schema for category response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class CategoryListResponse(BaseModel):
    """Schema for category list response."""

    model_config = ConfigDict(from_attributes=True)

    categories: list[CategoryResponse]
    total: int
