"""Sprint Planner agent for creating sprint schedules and rituals."""

from typing import Any, Dict

from crewai import Task
from .base import BaseAgent


class SprintPlannerAgent(BaseAgent):
    """Agent responsible for creating sprint schedules and team rituals."""

    @property
    def role(self) -> str:
        return "Agile Sprint Planning Specialist"

    @property
    def goal(self) -> str:
        return "Create realistic sprint schedules with proper ceremonies and team rituals aligned to business calendar"

    @property
    def backstory(self) -> str:
        return """You are an experienced Scrum Master and Agile coach with deep knowledge of 
        sprint planning, team ceremonies, and productive development cycles. You understand 
        how to structure sprints for maximum team productivity while maintaining sustainable 
        pace and clear communication rhythms."""

    def create_task(self, description: str, context: Dict[str, Any]) -> Task:
        """Create sprint planning task."""
        project_config = context.get("project", {})
        time_window = context.get("time_window", {})
        org = context.get("org", {})
        
        sprint_length = project_config.get("sprint_length_days", 14)
        start_date = time_window.get("start")
        end_date = time_window.get("end")
        timezone = time_window.get("timezone", "Asia/Kolkata")
        business_days_only = time_window.get("business_days_only", True)
        
        task_description = f"""
        Create a comprehensive sprint planning structure for the project:
        
        Sprint Configuration:
        - Sprint Length: {sprint_length} days
        - Time Window: {start_date} to {end_date}
        - Timezone: {timezone}
        - Business Days Only: {business_days_only}
        - Team: {org.get('team_name')}
        
        Your deliverables:
        
        1. SPRINT SCHEDULE:
        Calculate and create 2-3 sprints within the time window:
        - sprint_id: SPRINT-1, SPRINT-2, etc.
        - name: Sprint descriptive name
        - start_date: Sprint start (datetime with timezone)
        - end_date: Sprint end (datetime with timezone)
        - project_id: PROJ-{project_config.get('key', 'PROJ')}
        
        2. TEAM RITUALS AND CEREMONIES:
        Create calendar templates for recurring meetings:
        
        Daily Standup:
        - event_type: "daily_standup"
        - frequency: "daily"
        - time: "09:45" (IST)
        - duration_minutes: 15
        - attendees: All team members
        
        Sprint Planning:
        - event_type: "sprint_planning"
        - frequency: "per_sprint"
        - time: "10:00" (first day of sprint)
        - duration_minutes: 120
        - attendees: All team members
        
        Sprint Retrospective:
        - event_type: "sprint_retrospective"
        - frequency: "per_sprint"
        - time: "15:00" (last day of sprint)
        - duration_minutes: 90
        - attendees: All team members
        
        Sprint Review:
        - event_type: "sprint_review"
        - frequency: "per_sprint"
        - time: "14:00" (last day of sprint)
        - duration_minutes: 60
        - attendees: Team + stakeholders
        
        Backlog Grooming:
        - event_type: "backlog_grooming"
        - frequency: "weekly"
        - time: "14:00" (mid-sprint)
        - duration_minutes: 60
        - attendees: Core team
        
        3. ADDITIONAL CONSIDERATIONS:
        - Ensure sprints start on Mondays and end on Fridays
        - Account for Indian holidays and weekends
        - Leave buffer time between sprints for planning
        - Consider team capacity and velocity
        - Plan for sprint overlap in ceremonies
        
        4. SPRINT THEMES:
        Suggest themes for each sprint based on project epics:
        - Sprint 1: Foundation and Setup
        - Sprint 2: Core Development
        - Sprint 3: Integration and Testing
        
        Return structured data with sprints list and calendar_templates list.
        """
        
        return Task(
            description=task_description,
            agent=self.agent,
            expected_output="A dictionary with sprints and calendar_templates"
        )
