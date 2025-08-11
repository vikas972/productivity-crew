"""Hashing utilities for deterministic content generation."""

import hashlib
import json
from typing import Any, Dict, List


class DeterministicHasher:
    """Provides deterministic hashing for reproducible content generation."""

    @staticmethod
    def hash_string(content: str, seed: int = 42) -> str:
        """Generate a deterministic hash for a string."""
        combined = f"{content}:{seed}"
        return hashlib.sha256(combined.encode()).hexdigest()

    @staticmethod
    def hash_object(obj: Any, seed: int = 42) -> str:
        """Generate a deterministic hash for any object."""
        # Convert to JSON string for consistent hashing
        json_str = json.dumps(obj, sort_keys=True, default=str)
        return DeterministicHasher.hash_string(json_str, seed)

    @staticmethod
    def short_hash(content: str, length: int = 8, seed: int = 42) -> str:
        """Generate a short hash of specified length."""
        full_hash = DeterministicHasher.hash_string(content, seed)
        return full_hash[:length]

    @staticmethod
    def content_fingerprint(data: Dict[str, Any]) -> str:
        """Generate a fingerprint for data integrity verification."""
        # Sort keys and create canonical representation
        canonical = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(canonical.encode()).hexdigest()

    @staticmethod
    def batch_fingerprint(items: List[Dict[str, Any]]) -> str:
        """Generate a fingerprint for a batch of items."""
        # Create hash of all individual fingerprints
        fingerprints = [
            DeterministicHasher.content_fingerprint(item) for item in items
        ]
        combined = ":".join(sorted(fingerprints))
        return hashlib.sha256(combined.encode()).hexdigest()

    @staticmethod
    def verify_integrity(
        data: Dict[str, Any], expected_hash: str
    ) -> bool:
        """Verify data integrity against expected hash."""
        actual_hash = DeterministicHasher.content_fingerprint(data)
        return actual_hash == expected_hash
