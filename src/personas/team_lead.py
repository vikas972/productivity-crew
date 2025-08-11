"""Team Lead persona implementation."""

from typing import Dict, List, Any

from .base import BasePersona, PersonaLevel
from ..okg.models import Ticket


class TeamLeadPersona(BasePersona):
    """Persona for Team Leads who balance technical work with team coordination."""

    def email_style(self) -> Dict[str, Any]:
        """Team leads negotiate, coordinate, and balance technical with people concerns."""
        return {
            "tone": "balanced, coordinating, decisive",
            "question_ratio": 0.25,  # Balanced questions and statements
            "greeting_formality": "professional",  # "Hi all", "Team"
            "signature_style": "professional",
            "typical_phrases": [
                "Let's align on",
                "I'll coordinate with",
                "From a team perspective",
                "We need to balance",
                "I'll take this offline with",
                "Let me get back to you on",
                "Here's what I'm thinking",
                "We should prioritize",
                "I'll follow up on this"
            ],
            "avg_response_length": "medium-long",
            "code_snippet_frequency": 0.4,
            "attachment_likelihood": 0.5
        }

    def ticket_fit(self, ticket: Ticket) -> float:
        """Team leads handle coordination tasks and complex technical work."""
        base_probability = 0.35
        
        # Prefer medium to high story points
        if ticket.story_points:
            if ticket.story_points >= 5:
                base_probability += 0.2
            elif ticket.story_points >= 3:
                base_probability += 0.3
            else:
                base_probability += 0.1  # Still take some smaller tasks
        
        # Prefer coordination and architecture tasks
        type_modifiers = {
            "Story": 0.2,    # Feature coordination
            "Task": 0.1,     # Often coordination tasks
            "Spike": 0.1,    # Research and planning
            "Bug": 0.0       # Neutral on bugs
        }
        
        base_probability += type_modifiers.get(ticket.type, 0)
        
        # Good at handling all priorities
        priority_modifiers = {
            "Critical": 0.1,  # Leadership needed
            "High": 0.15,     # Good coordination needed
            "Medium": 0.1,
            "Low": -0.05
        }
        
        base_probability += priority_modifiers.get(ticket.priority, 0)
        
        return max(0, min(1, base_probability))

    def communication_patterns(self) -> Dict[str, Any]:
        """Team leads have high communication volume for coordination."""
        return {
            "daily_email_volume": {"min": 20, "max": 35},
            "initiate_thread_probability": 0.6,
            "reply_probability": 0.8,
            "escalation_tendency": "balanced",  # Knows when to escalate
            "meeting_talk_time": "high",        # Lead discussions
            "cross_team_communication": "high"  # Coordinate across teams
        }

    def typical_email_categories(self) -> Dict[str, float]:
        """Team leads have significant managerial responsibilities."""
        return {
            "work": 0.55,          # Still high technical work
            "managerial": 0.25,    # Significant people management
            "customer": 0.03,      # Some customer escalations
            "corporate": 0.08,     # Some corporate involvement
            "hr": 0.05,           # Team member issues
            "vendor": 0.03,       # Technical vendor coordination
            "security": 0.04,     # Security processes
            "event": 0.02,        # Team events
            "facilities": 0.01,   # Minimal facilities
            "spam": 0.02,         # Lower spam rate
            "phishing_sim": 0.003 # Security awareness
        }

    def response_time_profile(self) -> Dict[str, Any]:
        """Team leads respond quickly for coordination but thoughtfully for decisions."""
        return {
            "urgent_response_minutes": {"min": 20, "max": 90},
            "normal_response_hours": {"min": 1, "max": 6},
            "low_priority_response_hours": {"min": 4, "max": 24},
            "weekend_response_probability": 0.5,
            "after_hours_response_probability": 0.6
        }

    def get_tone_indicators(self) -> List[str]:
        """Team leads are balanced between technical and people focus."""
        base_tones = super().get_tone_indicators()
        lead_tones = ["coordinating", "balanced", "decisive", "diplomatic"]
        return base_tones + lead_tones

    def should_participate_in_thread(self, subject: str, participants: List[str]) -> bool:
        """Team leads participate in coordination and cross-team discussions."""
        base_participation = super().should_participate_in_thread(subject, participants)
        
        # More likely to participate in coordination threads
        coordination_keywords = [
            "coordination", "alignment", "planning", "timeline", 
            "dependency", "resource", "sprint", "retrospective"
        ]
        is_coordination = any(
            keyword in subject.lower() for keyword in coordination_keywords
        )
        
        # More likely to participate in team-related threads
        team_keywords = ["team", "standup", "meeting", "process", "workflow"]
        is_team_related = any(
            keyword in subject.lower() for keyword in team_keywords
        )
        
        # More likely to participate in escalations
        escalation_keywords = ["escalation", "blocker", "urgent", "help needed"]
        is_escalation = any(
            keyword in subject.lower() for keyword in escalation_keywords
        )
        
        if is_coordination or is_team_related or is_escalation:
            return True
        
        return base_participation

    def get_meeting_participation_likelihood(self, meeting_type: str) -> float:
        """Team leads attend most meetings for coordination and leadership."""
        base_likelihood = super().get_meeting_participation_likelihood(meeting_type)
        
        # Adjustments for team lead level
        adjustments = {
            "sprint_planning": 0.2,         # Lead sprint planning
            "retrospective": 0.3,          # Lead retrospectives
            "standup": 0.1,               # Facilitate standups
            "one_on_one": 0.6,            # Regular team member 1:1s
            "cross_team_sync": 0.4,       # Important for coordination
            "architecture_review": 0.2,    # Input on technical decisions
            "all_hands": 0.1,             # Good for team context
            "tech_talk": 0.0              # Neutral on tech talks
        }
        
        adjustment = adjustments.get(meeting_type, 0)
        return max(0, min(1, base_likelihood + adjustment))
