"""
Content deduplication system.

Detects and prevents duplicate entries using multiple strategies:
- Link-based deduplication (exact URL matching)
- Title-based deduplication (exact/similar title matching)
- Content-based deduplication (fingerprint matching)
"""

from enum import Enum
from typing import Optional

from sqlalchemy.orm import Session

from spider_aggregation.config import get_config
from spider_aggregation.logger import get_logger
from spider_aggregation.models import EntryModel
from spider_aggregation.storage.repositories.entry_repo import EntryRepository
from spider_aggregation.utils.hash_utils import (
    compute_content_hash,
    compute_link_hash,
    compute_similarity_hash,
    compute_title_hash,
)

logger = get_logger(__name__)


class DedupStrategy(str, Enum):
    """Deduplication strategy levels."""

    STRICT = "strict"  # Match on link, title, AND content
    MEDIUM = "medium"  # Match on link OR (title AND content)
    RELAXED = "relaxed"  # Match on link OR title


class DedupResult:
    """Result of deduplication check."""

    def __init__(
        self,
        is_duplicate: bool,
        reason: Optional[str] = None,
        existing_entry: Optional[EntryModel] = None,
    ):
        """Initialize deduplication result.

        Args:
            is_duplicate: Whether the entry is a duplicate
            reason: Reason for deduplication decision
            existing_entry: The existing duplicate entry (if found)
        """
        self.is_duplicate = is_duplicate
        self.reason = reason
        self.existing_entry = existing_entry

    def __repr__(self) -> str:
        return f"DedupResult(is_duplicate={self.is_duplicate}, reason={self.reason})"


class Deduplicator:
    """Content deduplication system."""

    def __init__(
        self,
        session: Optional[Session] = None,
        strategy: DedupStrategy = DedupStrategy.MEDIUM,
    ):
        """Initialize deduplicator.

        Args:
            session: Database session for checking duplicates
            strategy: Deduplication strategy to use
        """
        config = get_config()

        self.session = session
        self.strategy = strategy or config.deduplicator.strategy
        self.enable_title_check = config.deduplicator.check_by_title
        self.enable_content_check = config.deduplicator.check_by_content
        self.similarity_threshold = config.deduplicator.title_similarity_threshold

        # Statistics
        self.stats = {
            "checks": 0,
            "duplicates_found": 0,
            "link_matches": 0,
            "title_matches": 0,
            "content_matches": 0,
        }

    def check_duplicate(
        self,
        entry: dict,
        feed_id: int,
    ) -> DedupResult:
        """Check if an entry is a duplicate.

        Args:
            entry: Parsed entry dictionary
            feed_id: Feed ID to check within

        Returns:
            DedupResult with duplicate status
        """
        self.stats["checks"] += 1

        if not self.session:
            logger.debug("No database session - skipping duplicate check")
            return DedupResult(is_duplicate=False, reason="No database session")

        repo = EntryRepository(self.session)

        # Extract hashes from entry
        link_hash = compute_link_hash(entry.get("link"))
        title_hash = compute_title_hash(entry.get("title"))
        content_hash = compute_content_hash(entry.get("content") or entry.get("summary"))

        # Strategy 1: Check by link (most reliable)
        if link_hash:
            existing = repo.get_by_link_hash(link_hash, feed_id)
            if existing:
                self.stats["duplicates_found"] += 1
                self.stats["link_matches"] += 1
                logger.info(f"Duplicate found by link: {entry.get('link')}")
                return DedupResult(
                    is_duplicate=True,
                    reason=f"Duplicate link (Entry ID: {existing.id})",
                    existing_entry=existing,
                )

        # Strategy 2: Check by title and content based on strategy
        if self.strategy == DedupStrategy.STRICT:
            # Strict: Match on both title AND content
            if title_hash and content_hash:
                existing = repo.get_by_title_and_content(title_hash, content_hash, feed_id)
                if existing:
                    self.stats["duplicates_found"] += 1
                    self.stats["title_matches"] += 1
                    self.stats["content_matches"] += 1
                    logger.info(f"Duplicate found by title+content: {entry.get('title')}")
                    return DedupResult(
                        is_duplicate=True,
                        reason=f"Duplicate title and content (Entry ID: {existing.id})",
                        existing_entry=existing,
                    )

        elif self.strategy == DedupStrategy.MEDIUM:
            # Medium: Match on title OR content (both enabled)
            if self.enable_title_check and title_hash:
                existing = repo.get_by_title_hash(title_hash, feed_id)
                if existing:
                    self.stats["duplicates_found"] += 1
                    self.stats["title_matches"] += 1
                    logger.info(f"Duplicate found by title: {entry.get('title')}")
                    return DedupResult(
                        is_duplicate=True,
                        reason=f"Duplicate title (Entry ID: {existing.id})",
                        existing_entry=existing,
                    )

            if self.enable_content_check and content_hash:
                existing = repo.get_by_content_hash(content_hash, feed_id)
                if existing:
                    self.stats["duplicates_found"] += 1
                    self.stats["content_matches"] += 1
                    logger.info(f"Duplicate found by content hash")
                    return DedupResult(
                        is_duplicate=True,
                        reason=f"Duplicate content (Entry ID: {existing.id})",
                        existing_entry=existing,
                    )

        elif self.strategy == DedupStrategy.RELAXED:
            # Relaxed: Match on title only
            if self.enable_title_check and title_hash:
                existing = repo.get_by_title_hash(title_hash, feed_id)
                if existing:
                    self.stats["duplicates_found"] += 1
                    self.stats["title_matches"] += 1
                    logger.info(f"Duplicate found by title (relaxed): {entry.get('title')}")
                    return DedupResult(
                        is_duplicate=True,
                        reason=f"Duplicate title (Entry ID: {existing.id})",
                        existing_entry=existing,
                    )

        # No duplicate found
        logger.debug(f"No duplicate found for: {entry.get('title') or entry.get('link')}")
        return DedupResult(is_duplicate=False, reason="No duplicate")

    def check_duplicate_across_feeds(
        self,
        entry: dict,
        feed_ids: Optional[list[int]] = None,
    ) -> DedupResult:
        """Check for duplicates across multiple feeds.

        Args:
            entry: Parsed entry dictionary
            feed_ids: List of feed IDs to check (None = all feeds)

        Returns:
            DedupResult with duplicate status
        """
        if not self.session:
            return DedupResult(is_duplicate=False, reason="No database session")

        repo = EntryRepository(self.session)

        link_hash = compute_link_hash(entry.get("link"))
        title_hash = compute_title_hash(entry.get("title"))

        if link_hash:
            existing = repo.get_by_link_hash_any_feed(link_hash, feed_ids)
            if existing:
                return DedupResult(
                    is_duplicate=True,
                    reason=f"Duplicate link across feeds (Entry ID: {existing.id})",
                    existing_entry=existing,
                )

        if title_hash and self.enable_title_check:
            existing = repo.get_by_title_hash_any_feed(title_hash, feed_ids)
            if existing:
                return DedupResult(
                    is_duplicate=True,
                    reason=f"Duplicate title across feeds (Entry ID: {existing.id})",
                    existing_entry=existing,
                )

        return DedupResult(is_duplicate=False, reason="No duplicate across feeds")

    def compute_hashes(self, entry: dict) -> dict:
        """Compute all hashes for an entry.

        Args:
            entry: Parsed entry dictionary

        Returns:
            Dictionary with link_hash, title_hash, content_hash
        """
        return {
            "link_hash": compute_link_hash(entry.get("link")),
            "title_hash": compute_title_hash(entry.get("title")),
            "content_hash": compute_content_hash(entry.get("content") or entry.get("summary")),
        }

    def get_stats(self) -> dict:
        """Get deduplication statistics.

        Returns:
            Dictionary with deduplication stats
        """
        return self.stats.copy()

    def reset_stats(self) -> None:
        """Reset deduplication statistics."""
        self.stats = {
            "checks": 0,
            "duplicates_found": 0,
            "link_matches": 0,
            "title_matches": 0,
            "content_matches": 0,
        }


def create_deduplicator(
    session: Optional[Session] = None,
    strategy: DedupStrategy = DedupStrategy.MEDIUM,
) -> Deduplicator:
    """Create a configured Deduplicator instance.

    Args:
        session: Optional database session
        strategy: Deduplication strategy

    Returns:
        Configured Deduplicator instance
    """
    return Deduplicator(session=session, strategy=strategy)
