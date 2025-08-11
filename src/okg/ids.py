"""Deterministic ID generation utilities."""

import hashlib
import random
from typing import Dict, Any


class IDGenerator:
    """Generates deterministic IDs based on a seed and context."""

    def __init__(self, seed: int = 42) -> None:
        """Initialize with a seed for reproducibility."""
        self.seed = seed
        self.counters: Dict[str, int] = {}
        self.rng = random.Random(seed)

    def _get_counter(self, prefix: str) -> int:
        """Get and increment counter for a given prefix."""
        if prefix not in self.counters:
            self.counters[prefix] = 0
        self.counters[prefix] += 1
        return self.counters[prefix]

    def person_id(self) -> str:
        """Generate a person ID like PER-0001."""
        counter = self._get_counter("PER")
        return f"PER-{counter:04d}"

    def team_id(self, name: str) -> str:
        """Generate a team ID like TEAM-PAY."""
        # Use first 3 chars of name, uppercase
        key = name.upper().replace(" ", "")[:3]
        return f"TEAM-{key}"

    def project_id(self, key: str) -> str:
        """Generate a project ID like PROJ-PAY."""
        return f"PROJ-{key.upper()}"

    def epic_id(self, project_key: str) -> str:
        """Generate an epic ID like EPIC-PAY-01."""
        counter = self._get_counter(f"EPIC-{project_key}")
        return f"EPIC-{project_key.upper()}-{counter:02d}"

    def ticket_id(self, project_key: str) -> str:
        """Generate a ticket ID like PAY-1421."""
        counter = self._get_counter(f"TICKET-{project_key}")
        # Start from a realistic number
        ticket_num = 1400 + counter
        return f"{project_key.upper()}-{ticket_num}"

    def sprint_id(self) -> str:
        """Generate a sprint ID like SPRINT-1."""
        counter = self._get_counter("SPRINT")
        return f"SPRINT-{counter}"

    def thread_id(self) -> str:
        """Generate a mail thread ID like MAIL-TH-009."""
        counter = self._get_counter("THREAD")
        return f"MAIL-TH-{counter:03d}"

    def message_id(self) -> str:
        """Generate a message ID like MSG-031."""
        counter = self._get_counter("MSG")
        return f"MSG-{counter:03d}"

    def deterministic_hash(self, data: Any) -> str:
        """Generate a deterministic hash for any data."""
        content = str(data) + str(self.seed)
        return hashlib.sha256(content.encode()).hexdigest()[:8]

    def reset_counters(self) -> None:
        """Reset all counters (useful for testing)."""
        self.counters.clear()
        self.rng = random.Random(self.seed)
