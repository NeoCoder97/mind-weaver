"""
Digest log model for tracking email digest history.
"""

from datetime import datetime
from typing import Optional, TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from spider_aggregation.models.base import Base

if TYPE_CHECKING:
    from spider_aggregation.models.feed import FeedModel


class DigestLogModel(Base):
    """SQLAlchemy ORM model for Digest log."""

    __tablename__ = "digest_logs"

    __table_args__ = (
        Index("ix_digest_logs_sent_at", "sent_at"),
        Index("ix_digest_logs_status", "status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Send metadata
    sent_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(
        String(20), default="pending", nullable=False, index=True
    )  # pending, success, failed

    # Content summary
    entry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    feed_ids: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array of feed IDs

    # Email details
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    to_addresses: Mapped[str] = mapped_column(Text, nullable=False)  # JSON array

    # Generated content
    summary_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Error tracking
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<DigestLogModel(id={self.id}, sent_at='{self.sent_at}', status='{self.status}')>"


# Pydantic models for API


class DigestLogBase(BaseModel):
    """Base DigestLog schema."""

    entry_count: int = Field(default=0, ge=0, description="Number of entries included")
    feed_ids: list[int] = Field(default_factory=list, description="Feed IDs included")
    subject: str = Field(..., max_length=500, description="Email subject")
    to_addresses: list[str] = Field(..., description="Recipient email addresses")
    summary_content: Optional[str] = Field(None, description="Generated summary content")


class DigestLogCreate(DigestLogBase):
    """Schema for creating a digest log."""

    status: str = Field(default="pending", description="Status: pending, success, failed")
    error_message: Optional[str] = Field(None, description="Error message if failed")


class DigestLogUpdate(BaseModel):
    """Schema for updating a digest log."""

    status: Optional[str] = Field(None, description="Status: pending, success, failed")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    summary_content: Optional[str] = Field(None, description="Generated summary content")


class DigestLogResponse(DigestLogBase):
    """Schema for digest log response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    sent_at: datetime
    status: str
    error_message: Optional[str] = None


class DigestLogListResponse(BaseModel):
    """Schema for digest log list response."""

    model_config = ConfigDict(from_attributes=True)

    logs: list[DigestLogResponse]
    total: int
    page: int
    page_size: int
