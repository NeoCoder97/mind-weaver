"""
Base repository with common CRUD operations.

This module provides a generic base repository class that encapsulates
common database operations to eliminate code duplication across repositories.
"""

from abc import abstractmethod
from datetime import datetime
from typing import TypeVar, Generic, Optional, Type, Any

from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Base repository with common CRUD operations.

    This class provides a generic implementation of common database operations
    that are shared across all repositories: create, get_by_id, list, count,
    update, and delete.

    Type Args:
        ModelType: The SQLAlchemy model type
        CreateSchemaType: The Pydantic create schema type
        UpdateSchemaType: The Pydantic update schema type
    """

    def __init__(self, session: Session, model: Type[ModelType]) -> None:
        """Initialize repository with a database session and model.

        Args:
            session: SQLAlchemy Session instance
            model: SQLAlchemy model class
        """
        self.session = session
        self.model = model

    def create(self, obj_data: CreateSchemaType) -> ModelType:
        """Create a new record.

        Args:
            obj_data: Creation data from Pydantic schema

        Returns:
            Created model instance
        """
        obj = self.model(**obj_data.model_dump())
        self.session.add(obj)
        self.session.flush()
        self.session.refresh(obj)
        return obj

    def get_by_id(self, obj_id: int) -> Optional[ModelType]:
        """Get a record by ID.

        Args:
            obj_id: Record ID

        Returns:
            Model instance or None
        """
        return self.session.query(self.model).filter(self.model.id == obj_id).first()

    def list(
        self,
        limit: int = 100,
        offset: int = 0,
        order_by: str = "created_at",
        order_desc: bool = True,
        **filters: Any,
    ) -> list[ModelType]:
        """List records with optional filtering and pagination.

        Args:
            limit: Maximum number of results
            offset: Number of results to skip
            order_by: Field to order by
            order_desc: Sort in descending order
            **filters: Additional filter parameters (e.g., enabled_only=True)

        Returns:
            List of model instances
        """
        query = self.session.query(self.model)

        # Apply filters if provided
        for key, value in filters.items():
            if value is not None and hasattr(self.model, key):
                query = query.filter(getattr(self.model, key) == value)

        # Apply ordering
        # Try to get the order_by column, fallback to common timestamp fields
        if hasattr(self.model, order_by):
            order_column = getattr(self.model, order_by)
        elif hasattr(self.model, "created_at"):
            order_column = self.model.created_at
        elif hasattr(self.model, "fetched_at"):
            order_column = self.model.fetched_at
        elif hasattr(self.model, "id"):
            order_column = self.model.id
        else:
            # No suitable column found, skip ordering
            order_column = None

        if order_column is not None:
            if order_desc:
                query = query.order_by(desc(order_column))
            else:
                query = query.order_by(asc(order_column))

        return query.limit(limit).offset(offset).all()

    def count(self, **filters: Any) -> int:
        """Count records with optional filtering.

        Args:
            **filters: Filter parameters (e.g., enabled_only=True)

        Returns:
            Number of records
        """
        query = self.session.query(self.model)

        # Apply filters if provided
        for key, value in filters.items():
            if value is not None and hasattr(self.model, key):
                query = query.filter(getattr(self.model, key) == value)

        return query.count()

    def update(self, obj: ModelType, obj_data: UpdateSchemaType) -> ModelType:
        """Update a record.

        Args:
            obj: Model instance to update
            obj_data: Update data from Pydantic schema

        Returns:
            Updated model instance
        """
        update_data = obj_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(obj, field, value)

        # Auto-update updated_at if model has it
        if hasattr(obj, "updated_at"):
            obj.updated_at = datetime.utcnow()

        self.session.flush()
        self.session.refresh(obj)
        return obj

    def delete(self, obj: ModelType) -> None:
        """Delete a record.

        Args:
            obj: Model instance to delete
        """
        self.session.delete(obj)
        self.session.flush()

    def exists(self, **filters: Any) -> bool:
        """Check if a record exists with the given filters.

        Args:
            **filters: Filter parameters

        Returns:
            True if a matching record exists, False otherwise
        """
        return self.count(**filters) > 0
