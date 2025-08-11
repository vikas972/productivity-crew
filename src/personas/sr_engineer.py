"""Senior Engineer persona implementation."""

from typing import Dict, List, Any

from .base import BasePersona, PersonaLevel
from ..okg.models import Ticket


class SeniorEngineerPersona(BasePersona):
    """Persona for Senior Software Engineers."""

    def email_style(self) -> Dict[str, Any]:
        """Senior engineers propose solutions and provide technical guidance."""
        return {
            "tone": "confident, solution-oriented, technical",
            "question_ratio": 0.15,  # Lower question rate, more statements
            "greeting_formality": "casual",  # "Hi", "Hello"
            "signature_style": "minimal",
            "typical_phrases": [
                "I think we should consider",
                "Based on my experience",
                "Here's a potential approach",
                "The technical impact of this would be",
                "I recommend we",
                "From an implementation perspective",
                "We could optimize this by"
            ],
            "avg_response_length": "long",
            "code_snippet_frequency": 0.6,
            "attachment_likelihood": 0.4
        }

    def ticket_fit(self, ticket: Ticket) -> float:
        """Senior engineers handle complex tickets and technical challenges."""
        base_probability = 0.4
        
        # Prefer higher story points (complex work)
        if ticket.story_points:
            if ticket.story_points >= 8:
                base_probability += 0.3
            elif ticket.story_points >= 5:
                base_probability += 0.2
            elif ticket.story_points <= 2:
                base_probability -= 0.2
        
        # Prefer certain ticket types
        type_modifiers = {
            "Story": 0.2,    # Feature development
            "Spike": 0.3,    # Research and investigation
            "Bug": 0.1,      # Complex bug fixing
            "Task": 0.0      # Neutral on tasks
        }
        
        base_probability += type_modifiers.get(ticket.type, 0)
        
        # Can handle any priority
        priority_modifiers = {
            "Critical": 0.2,  # Good at handling critical issues
            "High": 0.1,
            "Medium": 0.0,
            "Low": -0.1
        }
        
        base_probability += priority_modifiers.get(ticket.priority, 0)
        
        return max(0, min(1, base_probability))

    def communication_patterns(self) -> Dict[str, Any]:
        """Senior engineers are selective but thorough in communication."""
        return {
            "daily_email_volume": {"min": 12, "max": 25},
            "initiate_thread_probability": 0.4,
            "reply_probability": 0.7,
            "escalation_tendency": "medium",  # Balanced escalation
            "meeting_talk_time": "medium",    # Contribute technically
            "documentation_creation": "high"  # Create technical docs
        }

    def typical_email_categories(self) -> Dict[str, float]:
        """Senior engineers have broader technical responsibilities."""
        return {
            "work": 0.65,          # High work focus with technical depth
            "managerial": 0.15,    # Some cross-team coordination
            "customer": 0.05,      # Occasional customer technical calls
            "corporate": 0.06,     # Some corporate involvement
            "hr": 0.04,           # Minimal HR interaction
            "vendor": 0.04,       # Technical vendor discussions
            "security": 0.06,     # Security reviews and discussions
            "event": 0.025,       # Some technical events
            "facilities": 0.015,  # Minimal facilities
            "spam": 0.025,        # Slightly lower spam rate
            "phishing_sim": 0.005 # Security awareness
        }

    def response_time_profile(self) -> Dict[str, Any]:
        """Senior engineers balance quick response with thoughtful analysis."""
        return {
            "urgent_response_minutes": {"min": 30, "max": 120},
            "normal_response_hours": {"min": 2, "max": 8},
            "low_priority_response_hours": {"min": 8, "max": 48},
            "weekend_response_probability": 0.3,
            "after_hours_response_probability": 0.4
        }

    def get_tone_indicators(self) -> List[str]:
        """Senior engineers are confident and technically focused."""
        base_tones = super().get_tone_indicators()
        senior_tones = ["confident", "technical", "solution-focused", "mentoring"]
        return base_tones + senior_tones

    def should_participate_in_thread(self, subject: str, participants: List[str]) -> bool:
        """Senior engineers participate in technical discussions and mentoring."""
        base_participation = super().should_participate_in_thread(subject, participants)
        
        # More likely to participate in technical threads
        technical_keywords = [
            "architecture", "design", "performance", "scalability", 
            "technical", "implementation", "api", "database"
        ]
        is_technical = any(
            keyword in subject.lower() for keyword in technical_keywords
        )
        
        # More likely to participate in mentoring threads
        mentoring_keywords = ["review", "feedback", "guidance", "best practice"]
        is_mentoring = any(
            keyword in subject.lower() for keyword in mentoring_keywords
        )
        
        # Less interested in pure process discussions
        process_keywords = ["process", "procedure", "policy", "compliance"]
        is_process_only = any(
            keyword in subject.lower() for keyword in process_keywords
        ) and not is_technical
        
        if is_technical or is_mentoring:
            return True
        elif is_process_only:
            return base_participation * 0.5
        
        return base_participation

    def get_meeting_participation_likelihood(self, meeting_type: str) -> float:
        """Senior engineers focus on technical meetings and mentoring."""
        base_likelihood = super().get_meeting_participation_likelihood(meeting_type)
        
        # Adjustments for senior level
        adjustments = {
            "architecture_review": 0.4,     # High technical involvement
            "tech_talk": 0.3,              # Both learning and teaching
            "code_review": 0.3,            # Important for quality
            "design_discussion": 0.4,       # Lead technical discussions
            "one_on_one": 0.2,             # Mentoring others
            "all_hands": -0.1,             # Less interested in general updates
            "hr_training": -0.2            # Lower priority on HR training
        }
        
        adjustment = adjustments.get(meeting_type, 0)
        return max(0, min(1, base_likelihood + adjustment))
