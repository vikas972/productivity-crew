"""Mailbox Generator agent for creating person-specific email content."""

from typing import Any, Dict

from crewai import Task
from .base import BaseAgent


class MailboxGeneratorAgent(BaseAgent):
    """Agent responsible for generating realistic email content for each team member."""

    @property
    def role(self) -> str:
        return "Email Content Generation Specialist"

    @property
    def goal(self) -> str:
        return "Generate realistic email conversations for each team member based on their role and persona"

    @property
    def backstory(self) -> str:
        return """You are an expert in workplace communication patterns and understand how 
        different roles interact via email. You know the typical communication patterns of 
        junior engineers, senior engineers, team leads, and managers, and can generate 
        authentic email content that reflects realistic workplace dynamics and conversations."""

    def create_task(self, description: str, context: Dict[str, Any]) -> Task:
        """Create mailbox generation task."""
        org = context.get("org", {})
        persons = context.get("persons", [])
        tickets = context.get("tickets", [])
        volumes = context.get("volumes", {})
        mail_config = context.get("mail", {})
        time_window = context.get("time_window", {})
        
        # Extract project key for ticket references
        project_key = org.get("project", {}).get("key", "PAY")
        
        emails_per_week = volumes.get("emails_per_person_per_week", {"min": 25, "max": 60})
        categories = mail_config.get("categories", [])
        thread_depth = mail_config.get("thread_depth", {"min": 2, "max": 6})
        
        task_description = f"""
        Generate realistic email content for each team member:
        
        Team Context:
        - Team: {org.get('team_name')}
        - Members: {len(persons)} people
        - Tickets: {len(tickets)} tickets available for reference
        - Time Window: {time_window.get('start')} to {time_window.get('end')}
        
        Email Volume:
        - Per person per week: {emails_per_week["min"]}-{emails_per_week["max"]} emails
        - Thread depth: {thread_depth["min"]}-{thread_depth["max"]} messages per thread
        - Categories: {categories}
        
        PERSONA-SPECIFIC REQUIREMENTS:
        
        Junior Engineers:
        - Volume: Lower end (25-35 emails/week)
        - Categories: 60% work, 10% managerial, 8% corporate, 6% hr, rest distributed
        - Tone: Eager, question-heavy, learning-focused
        - Subjects: "Quick question about...", "Need help with...", "How do I..."
        
        Senior Engineers:
        - Volume: Medium (35-50 emails/week)
        - Categories: 65% work, 15% managerial, 6% corporate, 4% hr, rest distributed
        - Tone: Confident, solution-oriented, technical
        - Subjects: "Recommendation for...", "Technical approach...", "Code review..."
        
        Team Leads:
        - Volume: Higher (45-60 emails/week)
        - Categories: 55% work, 25% managerial, 8% corporate, 5% hr, rest distributed
        - Tone: Coordinating, balanced, decisive
        - Subjects: "Sprint planning...", "Team alignment...", "Cross-team..."
        
        Managers:
        - Volume: Highest (60-80 emails/week)
        - Categories: 35% work, 35% managerial, 15% corporate, 6% hr, rest distributed
        - Tone: Strategic, people-focused, priority-setting
        - Subjects: "Resource allocation...", "Strategic alignment...", "Team performance..."
        
        EMAIL CONTENT RULES:
        
        1. TICKET REFERENCES:
        - When referencing tickets, use [{project_key}-####] in subject
        - Include ticket_id in refs.ticket_ids
        - Appropriate context for ticket discussions
        
        2. THREAD DYNAMICS:
        - Realistic reply patterns based on roles
        - Junior engineers ask more questions
        - Senior engineers provide solutions
        - Managers focus on priorities and resources
        - Team leads coordinate and align
        
        3. BUSINESS HOURS:
        - 85% of emails during 9 AM - 6 PM IST
        - 15% outside hours with rationale
        - Weekend emails only for urgent matters
        
        4. EMAIL CATEGORIES:
        Generate realistic content for each category:
        - work: Project discussions, technical problems, code reviews
        - managerial: 1:1s, performance, team coordination
        - customer: Support escalations, feedback (minimal for engineers)
        - corporate: All-hands, announcements, company updates
        - hr: Training, policies, benefits
        - vendor: Tool integrations, procurement
        - security: Security training, incident notifications
        - event: Team events, tech talks
        - facilities: Office-related (minimal for remote)
        - spam: Realistic spam content (≤5% total)
        - phishing_sim: Security training simulations (≤1% total)
        
        5. MANAGER INBOX SPECIAL REQUIREMENTS:
        - MUST have ≥20% non-project categories
        - Higher volume of corporate, hr, vendor emails
        - Strategic discussions and escalations
        - People management communications
        
        6. REALISTIC CONTENT:
        - Include code snippets in technical emails
        - Attach relevant files (logs, screenshots)
        - Use Indian context (timezones, holidays, locations)
        - Professional but authentic tone
        - Appropriate urgency levels
        
        7. DETERMINISTIC ORDERING:
        - Sort emails by timestamp within each person
        - Consistent thread organization
        - Proper reply relationships
        
        For each person, generate their complete mailbox as a list of MailMessage objects.
        Return as a dictionary: {{'person_id': ['MailMessage']}}
        """
        
        return Task(
            description=task_description,
            agent=self.agent,
            expected_output="A dictionary mapping person_id to list of MailMessage objects"
        )
