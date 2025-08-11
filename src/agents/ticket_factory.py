"""Ticket Factory agent for generating realistic Jira tickets."""

from typing import Any, Dict

from crewai import Task
from .base import BaseAgent


class TicketFactoryAgent(BaseAgent):
    """Agent responsible for generating realistic Jira tickets with full lifecycle."""

    @property
    def role(self) -> str:
        return "Technical Ticket Generation Specialist"

    @property
    def goal(self) -> str:
        return "Generate realistic Jira tickets with proper lifecycle, comments, and status transitions"

    @property
    def backstory(self) -> str:
        return """You are an expert in software development workflows and Jira ticket management. 
        You understand how real development teams work, how tickets progress through different 
        states, and what kinds of comments and interactions happen during the development process. 
        You create authentic ticket content that reflects real engineering work."""

    def create_task(self, description: str, context: Dict[str, Any]) -> Task:
        """Create ticket generation task."""
        volumes = context.get("volumes", {})
        project = context.get("project", {})
        epics = context.get("epics", [])
        sprints = context.get("sprints", [])
        org = context.get("org", {})
        time_window = context.get("time_window", {})
        
        min_tickets = volumes.get("jira_tickets_in_window", {}).get("min", 28)
        max_tickets = volumes.get("jira_tickets_in_window", {}).get("max", 40)
        project_key = project.get("key", "PROJ")
        
        task_description = f"""
        Generate {min_tickets}-{max_tickets} realistic Jira tickets for the project:
        
        Project Context:
        - Project Key: {project_key}
        - Project: {project.get('name')}
        - Epics: {len(epics)} epics available
        - Sprints: {len(sprints)} sprints planned
        - Time Window: {time_window.get('start')} to {time_window.get('end')}
        - Team Members: Available for assignment
        
        Ticket Distribution:
        - Story: 60% (feature development)
        - Bug: 25% (defect fixes)
        - Task: 12% (non-feature work)
        - Spike: 3% (research/investigation)
        
        Priority Distribution:
        - Low: 30%
        - Medium: 50%
        - High: 15%
        - Critical: 5%
        
        Story Points Distribution:
        - 1 point: 10%
        - 2 points: 20%
        - 3 points: 25%
        - 5 points: 25%
        - 8 points: 15%
        - 13 points: 4%
        - 21 points: 1%
        
        For each ticket, generate:
        
        1. BASIC INFO:
        - ticket_id: {project_key}-#### (sequential)
        - project_id: PROJ-{project_key}
        - epic_id: Link to appropriate epic (80% of tickets)
        - type: Based on distribution above
        - title: Realistic, specific title
        - description: Detailed description with acceptance criteria
        - priority: Based on distribution
        - story_points: For Stories only, based on distribution
        - reporter_id: Team member (usually TL or Mgr)
        - assignee_id: Team member (appropriate for complexity)
        
        2. STATUS TIMELINE:
        Realistic progression through states:
        - Backlog → To Do → In Progress → Code Review → Testing → Done
        - Ensure timing aligns with sprints
        - Some tickets may still be in progress
        - Done tickets should span the full timeline
        
        3. COMMENTS:
        Generate realistic comments throughout lifecycle:
        - Initial questions and clarifications
        - Progress updates
        - Code review feedback
        - Testing notes
        - Resolution confirmation
        - Average 1.6 comments per ticket
        
        Comment types by stage:
        - To Do: Questions about requirements
        - In Progress: Progress updates, blockers
        - Code Review: "LGTM", feedback, suggestions
        - Testing: Test results, edge cases
        - Done: Deployment confirmation
        
        4. ATTACHMENTS:
        Minimal realistic attachments:
        - Screenshots for UI tickets
        - Log files for bugs
        - Architecture diagrams for complex features
        - ~20% of tickets have attachments
        
        5. FINTECH-SPECIFIC CONTENT:
        Include realistic fintech scenarios:
        - Payment gateway integration
        - KYC verification flows
        - Fraud detection rules
        - API rate limiting
        - Security compliance
        - Performance optimization
        - Customer onboarding
        - Transaction monitoring
        
        VALIDATION RULES:
        - Done tickets MUST have code review comments
        - Status transitions must be chronological
        - Comments must align with current status
        - Assignees must match ticket complexity
        - All ticket references must be valid
        
        Return a list of complete Ticket objects with all fields populated.
        """
        
        return Task(
            description=task_description,
            agent=self.agent,
            expected_output="A list of Ticket objects with complete lifecycle data"
        )
