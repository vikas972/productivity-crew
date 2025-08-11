"""Junior Engineer persona implementation."""

from typing import Dict, List, Any

from .base import BasePersona, PersonaLevel
from ..okg.models import Ticket


class JuniorEngineerPersona(BasePersona):
    """Persona for Junior Software Engineers."""

    def email_style(self) -> Dict[str, Any]:
        """Junior engineers tend to ask questions and seek guidance."""
        return {
            "tone": "eager, learning-oriented, polite",
            "question_ratio": 0.4,  # High question rate
            "greeting_formality": "formal",  # "Dear", "Please"
            "signature_style": "full",
            "typical_phrases": [
                "Could you please help me understand",
                "I'm working on",
                "Quick question about",
                "Thank you for your guidance",
                "I'd appreciate any feedback",
                "Let me know if I'm missing something"
            ],
            "avg_response_length": "medium",
            "code_snippet_frequency": 0.3,
            "attachment_likelihood": 0.2
        }

    def ticket_fit(self, ticket: Ticket) -> float:
        """Junior engineers get simpler tickets and learning opportunities."""
        base_probability = 0.3
        
        # Prefer lower story points
        if ticket.story_points:
            if ticket.story_points <= 3:
                base_probability += 0.3
            elif ticket.story_points <= 5:
                base_probability += 0.1
            else:
                base_probability -= 0.2
        
        # Prefer certain ticket types
        type_modifiers = {
            "Bug": 0.2,      # Good learning opportunity
            "Task": 0.3,     # Often straightforward
            "Story": 0.1,    # Might be complex
            "Spike": -0.1    # Research tasks might be challenging
        }
        
        base_probability += type_modifiers.get(ticket.type, 0)
        
        # Prefer lower priority (less pressure)
        priority_modifiers = {
            "Low": 0.2,
            "Medium": 0.1,
            "High": -0.1,
            "Critical": -0.3
        }
        
        base_probability += priority_modifiers.get(ticket.priority, 0)
        
        return max(0, min(1, base_probability))

    def communication_patterns(self) -> Dict[str, Any]:
        """Junior engineers communicate frequently for guidance."""
        return {
            "daily_email_volume": {"min": 8, "max": 15},
            "initiate_thread_probability": 0.2,
            "reply_probability": 0.8,
            "escalation_tendency": "high",  # Quick to ask for help
            "meeting_talk_time": "low",     # Listen more than speak
            "documentation_requests": "high"
        }

    def typical_email_categories(self) -> Dict[str, float]:
        """Junior engineers focus on work and learning."""
        return {
            "work": 0.6,           # High work focus
            "managerial": 0.1,     # Low management involvement
            "customer": 0.02,      # Rarely customer-facing
            "corporate": 0.08,     # Some corporate communication
            "hr": 0.06,           # Some HR interaction
            "vendor": 0.02,       # Minimal vendor interaction
            "security": 0.04,     # Security training/updates
            "event": 0.03,        # Team events
            "facilities": 0.02,   # Minimal facilities
            "spam": 0.03,         # Normal spam rate
            "phishing_sim": 0.008 # Security simulations
        }

    def response_time_profile(self) -> Dict[str, Any]:
        """Junior engineers respond quickly, especially to guidance."""
        return {
            "urgent_response_minutes": {"min": 15, "max": 60},
            "normal_response_hours": {"min": 1, "max": 4},
            "low_priority_response_hours": {"min": 4, "max": 24},
            "weekend_response_probability": 0.1,
            "after_hours_response_probability": 0.2
        }

    def get_tone_indicators(self) -> List[str]:
        """Junior engineers are eager and respectful."""
        base_tones = super().get_tone_indicators()
        junior_tones = ["eager", "learning-focused", "respectful", "detail-oriented"]
        return base_tones + junior_tones

    def should_participate_in_thread(self, subject: str, participants: List[str]) -> bool:
        """Junior engineers participate when learning opportunities arise."""
        base_participation = super().should_participate_in_thread(subject, participants)
        
        # More likely to participate in learning threads
        learning_keywords = ["how to", "best practice", "tutorial", "guide", "documentation"]
        has_learning_content = any(
            keyword in subject.lower() for keyword in learning_keywords
        )
        
        # Less likely to participate in high-level strategy
        strategy_keywords = ["strategy", "roadmap", "executive", "board"]
        is_high_level = any(
            keyword in subject.lower() for keyword in strategy_keywords
        )
        
        if has_learning_content:
            return True
        elif is_high_level:
            return False
        
        return base_participation

    def get_meeting_participation_likelihood(self, meeting_type: str) -> float:
        """Junior engineers attend most meetings for learning."""
        base_likelihood = super().get_meeting_participation_likelihood(meeting_type)
        
        # Adjustments for junior level
        adjustments = {
            "standup": 0.05,         # Slightly higher attendance
            "sprint_planning": 0.1,   # Good learning opportunity
            "retrospective": 0.05,    # Learning from feedback
            "tech_talk": 0.3,        # High interest in learning
            "one_on_one": 0.4,       # Regular mentor meetings
            "architecture_review": -0.2  # Less involved in architecture
        }
        
        adjustment = adjustments.get(meeting_type, 0)
        return max(0, min(1, base_likelihood + adjustment))
