"""Engineering Manager persona implementation."""

from typing import Dict, List, Any

from .base import BasePersona, PersonaLevel
from ..okg.models import Ticket


class ManagerPersona(BasePersona):
    """Persona for Engineering Managers focused on people, process, and priorities."""

    def email_style(self) -> Dict[str, Any]:
        """Managers align capacity, set priorities, and coordinate across teams."""
        return {
            "tone": "strategic, people-focused, priority-setting",
            "question_ratio": 0.3,  # Ask strategic questions
            "greeting_formality": "executive",  # "Hi everyone", "Team"
            "signature_style": "executive",
            "typical_phrases": [
                "From a strategic perspective",
                "Let's align our priorities",
                "I'll work with leadership on",
                "Here's what I'm seeing across teams",
                "We need to balance capacity with",
                "I'll take this to the next level",
                "This aligns with our OKRs",
                "Let me get context from",
                "We should consider the impact on",
                "I'll follow up with stakeholders"
            ],
            "avg_response_length": "long",
            "code_snippet_frequency": 0.1,  # Rarely includes code
            "attachment_likelihood": 0.6     # Often includes docs/reports
        }

    def ticket_fit(self, ticket: Ticket) -> float:
        """Managers rarely take implementation tickets, focus on coordination."""
        base_probability = 0.1  # Low base probability
        
        # Prefer coordination and process tickets
        type_modifiers = {
            "Task": 0.2,     # Process and coordination tasks
            "Story": -0.05,  # Rarely implementation stories
            "Bug": -0.1,     # Rarely bug fixes
            "Spike": 0.1     # Research and planning
        }
        
        base_probability += type_modifiers.get(ticket.type, 0)
        
        # More likely to handle high-priority coordination
        priority_modifiers = {
            "Critical": 0.2,  # Crisis management
            "High": 0.1,      # Important coordination
            "Medium": 0.0,
            "Low": -0.05
        }
        
        base_probability += priority_modifiers.get(ticket.priority, 0)
        
        # Less likely for technical story points
        if ticket.story_points and ticket.story_points > 3:
            base_probability -= 0.1
        
        return max(0, min(1, base_probability))

    def communication_patterns(self) -> Dict[str, Any]:
        """Managers have the highest communication volume and broadest scope."""
        return {
            "daily_email_volume": {"min": 40, "max": 80},
            "initiate_thread_probability": 0.7,
            "reply_probability": 0.6,
            "escalation_tendency": "strategic",  # Escalate strategically
            "meeting_talk_time": "high",         # Lead strategic discussions
            "cross_functional_communication": "very_high"  # Broad stakeholder base
        }

    def typical_email_categories(self) -> Dict[str, float]:
        """Managers have the most diverse email portfolio with high non-project content."""
        return {
            "work": 0.35,          # Lower direct work, more coordination
            "managerial": 0.35,    # High people and process management
            "customer": 0.04,      # Some customer escalations
            "corporate": 0.15,     # Significant corporate involvement
            "hr": 0.06,           # People management issues
            "vendor": 0.02,       # Strategic vendor relationships
            "security": 0.02,     # Security oversight
            "event": 0.006,       # Some corporate events
            "facilities": 0.004,  # Minimal facilities
            "spam": 0.02,         # Lower spam rate (better filters)
            "phishing_sim": 0.002 # Security awareness
        }

    def response_time_profile(self) -> Dict[str, Any]:
        """Managers balance quick strategic responses with thoughtful decisions."""
        return {
            "urgent_response_minutes": {"min": 10, "max": 60},   # Quick on urgent items
            "normal_response_hours": {"min": 2, "max": 12},      # Thoughtful responses
            "low_priority_response_hours": {"min": 8, "max": 72}, # Delegate when possible
            "weekend_response_probability": 0.3,
            "after_hours_response_probability": 0.5
        }

    def get_tone_indicators(self) -> List[str]:
        """Managers are strategic and people-focused."""
        base_tones = super().get_tone_indicators()
        manager_tones = ["strategic", "people-focused", "priority-setting", "executive"]
        return base_tones + manager_tones

    def should_participate_in_thread(self, subject: str, participants: List[str]) -> bool:
        """Managers participate in strategic, people, and escalation threads."""
        base_participation = super().should_participate_in_thread(subject, participants)
        
        # More likely to participate in strategic threads
        strategic_keywords = [
            "strategy", "roadmap", "okr", "goal", "priority", "resource",
            "budget", "planning", "leadership", "executive"
        ]
        is_strategic = any(
            keyword in subject.lower() for keyword in strategic_keywords
        )
        
        # More likely to participate in people-related threads
        people_keywords = [
            "team", "hire", "performance", "career", "promotion", 
            "feedback", "1:1", "mentoring", "development"
        ]
        is_people_related = any(
            keyword in subject.lower() for keyword in people_keywords
        )
        
        # More likely to participate in escalations
        escalation_keywords = [
            "escalation", "urgent", "critical", "blocker", "crisis",
            "customer complaint", "incident"
        ]
        is_escalation = any(
            keyword in subject.lower() for keyword in escalation_keywords
        )
        
        # Less likely to participate in deep technical threads
        deep_technical_keywords = [
            "implementation", "code review", "debugging", "algorithm",
            "data structure", "api design"
        ]
        is_deep_technical = any(
            keyword in subject.lower() for keyword in deep_technical_keywords
        )
        
        if is_strategic or is_people_related or is_escalation:
            return True
        elif is_deep_technical:
            return False
        
        return base_participation

    def get_meeting_participation_likelihood(self, meeting_type: str) -> float:
        """Managers attend strategic meetings and skip deep technical ones."""
        base_likelihood = super().get_meeting_participation_likelihood(meeting_type)
        
        # Adjustments for manager level
        adjustments = {
            "one_on_one": 0.7,             # Essential for people management
            "all_hands": 0.4,             # Important for communication
            "leadership_sync": 0.5,        # Cross-team coordination
            "okr_review": 0.5,            # Strategic planning
            "hiring_committee": 0.4,       # People decisions
            "sprint_planning": 0.1,        # Observe but don't lead
            "standup": -0.3,              # Often delegate to TL
            "code_review": -0.5,          # Rarely involved in code
            "architecture_review": 0.0,    # Strategic input only
            "retrospective": 0.2,         # Process improvement
            "customer_escalation": 0.4     # Handle escalations
        }
        
        adjustment = adjustments.get(meeting_type, 0)
        return max(0, min(1, base_likelihood + adjustment))
