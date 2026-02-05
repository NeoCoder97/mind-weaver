"""
Entry data model for RSS/Atom feed entries.
"""

from datetime import datetime
from typing import Optional, TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, Index, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from spider_aggregation.models.feed import Base, FeedModel

if TYPE_CHECKING:
    from spider_aggregation.models.feed import FeedModel


class EntryModel(Base):
    """SQLAlchemy ORM model for Entry."""

    __tablename__ = "entries"

    # Composite indexes for common query patterns
    __table_args__ = (
        Index("ix_entries_feed_published", "feed_id", "published_at"),
        Index("ix_entries_feed_fetched", "feed_id", "fetched_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    feed_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("feeds.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Relationship to Feed
    feed: Mapped["FeedModel"] = relationship("FeedModel", back_populates="entries")

    # Basic entry fields
    title: Mapped[str] = mapped_column(String(1000), nullable=False)
    link: Mapped[str] = mapped_column(String(2048), nullable=False)
    author: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Content fields
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timestamps
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, index=True)
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )

    # Deduplication fields
    title_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    link_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    content_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)

    # Additional metadata
    tags: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string of tags
    language: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    reading_time_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<EntryModel(id={self.id}, title='{self.title}', link='{self.link}')>"


# Pydantic models for API


class EntryBase(BaseModel):
    """Base Entry schema."""

    title: str = Field(..., max_length=1000, description="Entry title")
    link: str = Field(..., max_length=2048, description="Entry link")
    author: Optional[str] = Field(None, max_length=500, description="Entry author")
    summary: Optional[str] = Field(None, description="Entry summary")
    content: Optional[str] = Field(None, description="Entry full content")
    published_at: Optional[datetime] = Field(None, description="Publication date")
    tags: Optional[list[str]] = Field(None, description="Entry tags")
    language: Optional[str] = Field(None, max_length=10, description="Content language")
    reading_time_seconds: Optional[int] = Field(None, ge=0, description="Estimated reading time")
    enabled: bool = Field(True, description="Whether the entry is enabled (visible/active)")


class EntryCreate(EntryBase):
    """Schema for creating a new entry."""

    feed_id: int = Field(..., description="Feed ID")
    title_hash: str = Field(..., max_length=64, description="Hash of title for deduplication")
    link_hash: str = Field(..., max_length=64, description="Hash of link for deduplication")
    content_hash: Optional[str] = Field(
        None, max_length=64, description="Hash of content for deduplication"
    )


class EntryUpdate(BaseModel):
    """Schema for updating an entry."""

    title: Optional[str] = Field(None, max_length=1000)
    summary: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[list[str]] = None
    language: Optional[str] = Field(None, max_length=10)
    reading_time_seconds: Optional[int] = Field(None, ge=0)
    enabled: Optional[bool] = Field(None, description="Enable or disable entry")


class EntryResponse(EntryBase):
    """Schema for entry response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    feed_id: int
    fetched_at: datetime
    title_hash: str
    link_hash: str
    content_hash: Optional[str] = None


class EntryListResponse(BaseModel):
    """Schema for entry list response."""

    model_config = ConfigDict(from_attributes=True)

    entries: list[EntryResponse]
    total: int
    page: int
    page_size: int
