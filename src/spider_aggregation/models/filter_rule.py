"""Filter rule data model for content filtering."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import Boolean, DateTime, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from spider_aggregation.models.base import Base


class FilterRuleModel(Base):
    """SQLAlchemy ORM model for FilterRule."""

    __tablename__ = "filter_rules"

    # Composite index for enabled rules query
    __table_args__ = (Index("ix_filter_rules_enabled_priority", "enabled", "priority"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Rule configuration
    rule_type: Mapped[str] = mapped_column(
        String(50), nullable=False  # keyword, regex, tag, language
    )
    match_type: Mapped[str] = mapped_column(String(50), nullable=False)  # include, exclude
    pattern: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def __repr__(self) -> str:
        return f"<FilterRuleModel(id={self.id}, name='{self.name}', type='{self.rule_type}')>"


# Pydantic models for API


class FilterRuleBase(BaseModel):
    """Base FilterRule schema."""

    name: str = Field(..., max_length=500, description="Rule name")
    enabled: bool = Field(default=True, description="Whether the rule is enabled")
    rule_type: str = Field(
        ..., max_length=50, description="Rule type: keyword, regex, tag, language"
    )
    match_type: str = Field(..., max_length=50, description="Match type: include, exclude")
    pattern: str = Field(..., description="Pattern to match")
    priority: int = Field(default=0, ge=0, description="Rule priority (higher first)")


class FilterRuleCreate(FilterRuleBase):
    """Schema for creating a new filter rule."""


class FilterRuleUpdate(BaseModel):
    """Schema for updating a filter rule."""

    name: Optional[str] = Field(None, max_length=500)
    enabled: Optional[bool] = None
    rule_type: Optional[str] = Field(None, max_length=50)
    match_type: Optional[str] = Field(None, max_length=50)
    pattern: Optional[str] = None
    priority: Optional[int] = Field(None, ge=0)


class FilterRuleResponse(FilterRuleBase):
    """Schema for filter rule response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class FilterRuleListResponse(BaseModel):
    """Schema for filter rule list response."""

    model_config = ConfigDict(from_attributes=True)

    rules: list[FilterRuleResponse]
    total: int
