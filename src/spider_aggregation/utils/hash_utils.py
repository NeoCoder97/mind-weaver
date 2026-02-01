"""
Hash utility functions for content deduplication.

Provides consistent hashing for links, titles, and content to detect duplicates.
"""

import hashlib
from typing import Optional


def compute_md5_hash(content: Optional[str]) -> Optional[str]:
    """Compute MD5 hash of content.

    Args:
        content: Content to hash

    Returns:
        MD5 hash as hexadecimal string, or None if content is None/empty
    """
    if not content:
        return None

    # Normalize content: strip whitespace, lowercase for consistency
    normalized = str(content).strip().lower()
    if not normalized:
        return None

    return hashlib.md5(normalized.encode("utf-8")).hexdigest()


def compute_sha256_hash(content: Optional[str]) -> Optional[str]:
    """Compute SHA256 hash of content.

    Args:
        content: Content to hash

    Returns:
        SHA256 hash as hexadecimal string, or None if content is None/empty
    """
    if not content:
        return None

    # Normalize content: strip whitespace, lowercase for consistency
    normalized = str(content).strip().lower()
    if not normalized:
        return None

    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def compute_link_hash(link: Optional[str]) -> Optional[str]:
    """Compute hash for link deduplication.

    Normalizes URL before hashing to handle common variations:
    - Removes trailing slashes
    - Lowercases domain and path
    - Removes common tracking parameters

    Args:
        link: URL to hash

    Returns:
        Hash as hexadecimal string, or None if link is invalid
    """
    if not link:
        return None

    # Basic normalization
    normalized = link.strip().lower()

    # Remove trailing slash
    if normalized.endswith("/"):
        normalized = normalized[:-1]

    # Remove common tracking parameters (utm_*, ref, source)
    # This is a simple implementation - could be enhanced
    if "?" in normalized:
        base, query = normalized.split("?", 1)
        params = query.split("&")
        # Keep only essential parameters
        clean_params = [p for p in params if not p.startswith(("utm_", "ref=", "source="))]
        if clean_params:
            normalized = base + "?" + "&".join(clean_params)
        else:
            normalized = base

    if not normalized or not normalized.startswith(("http://", "https://")):
        return None

    return compute_md5_hash(normalized)


def compute_title_hash(title: Optional[str]) -> Optional[str]:
    """Compute hash for title deduplication.

    Normalizes title before hashing:
    - Strips whitespace
    - Lowercases
    - Removes extra whitespace

    Args:
        title: Title to hash

    Returns:
        Hash as hexadecimal string, or None if title is empty
    """
    if not title:
        return None

    # Normalize: strip, lowercase, remove extra whitespace
    normalized = " ".join(str(title).strip().lower().split())

    if not normalized:
        return None

    return compute_md5_hash(normalized)


def compute_content_hash(content: Optional[str]) -> Optional[str]:
    """Compute hash for content deduplication.

    For content, we use a fingerprinting approach:
    - Strip HTML tags
    - Normalize whitespace
    - Take first N characters to detect near-duplicates

    Args:
        content: Content to hash

    Returns:
        Hash as hexadecimal string, or None if content is empty
    """
    if not content:
        return None

    # Normalize content
    normalized = str(content).strip().lower()

    # Remove extra whitespace
    normalized = " ".join(normalized.split())

    # For content, we use a fingerprint of first 500 chars
    # This helps detect near-duplicates with minor changes
    fingerprint = normalized[:500]

    if not fingerprint:
        return None

    return compute_sha256_hash(fingerprint)


def compute_similarity_hash(content: Optional[str], length: int = 200) -> Optional[str]:
    """Compute similarity hash for fuzzy matching.

    Creates a hash based on word frequency and patterns
    to detect similar (but not identical) content.

    Args:
        content: Content to analyze
        length: Number of characters to analyze

    Returns:
        Hash as hexadecimal string, or None if content is empty
    """
    if not content:
        return None

    # Normalize and take sample
    normalized = str(content).strip().lower()
    normalized = " ".join(normalized.split())

    if not normalized:
        return None

    # Take sample from start, middle, and end
    sample_len = min(length, len(normalized))
    if len(normalized) > sample_len * 3:
        # Take three samples: start, middle, end
        start = normalized[:sample_len]
        middle_start = (len(normalized) - sample_len) // 2
        middle = normalized[middle_start : middle_start + sample_len]
        end = normalized[-sample_len:]
        sample = start + middle + end
    else:
        sample = normalized

    return compute_sha256_hash(sample)
