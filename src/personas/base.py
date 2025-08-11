"""Base persona classes for role-specific behavior patterns."""

from abc import ABC, abstractmethod
from typing import Dict, List, Any
from enum import Enum

from ..okg.models import Person, Ticket


class PersonaLevel(Enum):
    """Persona levels mapping to organizational hierarchy."""
    
    JUNIOR = "Jr"
    SENIOR = "Sr"
    TEAM_LEAD = "TL"
    MANAGER = "Mgr"


class BasePersona(ABC):
    """Abstract base class for all persona implementations."""

    def __init__(self, person: Person) -> None:
        """Initialize persona with person data."""
        self.person = person

    @abstractmethod
    def email_style(self) -> Dict[str, Any]:
        """Return email writing style characteristics for this persona."""
        pass

    @abstractmethod
    def ticket_fit(self, ticket: Ticket) -> float:
        """Return probability (0-1) that this persona would be assigned this ticket."""
        pass

    @abstractmethod
    def communication_patterns(self) -> Dict[str, Any]:
        """Return communication behavior patterns."""
        pass

    @abstractmethod
    def typical_email_categories(self) -> Dict[str, float]:
        """Return probability distribution over email categories."""
        pass

    @abstractmethod
    def response_time_profile(self) -> Dict[str, Any]:
        """Return response time characteristics."""
        pass

    def get_signature(self) -> str:
        """Generate email signature for this persona."""
        return f"""
Best regards,
{self.person.name}
{self.person.role}
VistaraPay - Payments Core Team
{self.person.location}
"""

    def get_tone_indicators(self) -> List[str]:
        """Get tone indicators for this persona's communication."""
        base_tones = ["professional", "collaborative"]
        return base_tones

    def should_participate_in_thread(self, subject: str, participants: List[str]) -> bool:
        """Determine if this persona should participate in an email thread."""
        # Base logic - participate if directly mentioned or if it's work-related
        is_mentioned = self.person.name.lower() in subject.lower()
        is_work_related = any(
            keyword in subject.lower() 
            for keyword in ["project", "sprint", "ticket", "bug", "feature"]
        )
        
        return is_mentioned or is_work_related

    def get_meeting_participation_likelihood(self, meeting_type: str) -> float:
        """Return likelihood of participating in different meeting types."""
        base_participation = {
            "standup": 0.9,
            "sprint_planning": 0.8,
            "retrospective": 0.7,
            "all_hands": 0.6,
            "tech_talk": 0.4,
            "one_on_one": 0.3,  # Depends on role hierarchy
        }
        
        return base_participation.get(meeting_type, 0.5)
