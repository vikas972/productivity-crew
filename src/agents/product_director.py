"""Product Director agent for creating project and epic structure."""

from typing import Any, Dict

from crewai import Task
from .base import BaseAgent


class ProductDirectorAgent(BaseAgent):
    """Agent responsible for creating project structure with epics and OKRs."""

    @property
    def role(self) -> str:
        return "Product Strategy Director"

    @property
    def goal(self) -> str:
        return "Define product strategy with projects, epics, and achievable OKRs aligned to business objectives"

    @property
    def backstory(self) -> str:
        return """You are a seasoned product director with expertise in fintech products, 
        strategic planning, and OKR frameworks. You understand how to break down complex 
        product initiatives into manageable epics and set realistic, measurable objectives 
        that drive business value."""

    def create_task(self, description: str, context: Dict[str, Any]) -> Task:
        """Create product strategy task."""
        project_config = context.get("project", {})
        company_context = context.get("company_context", {})
        time_window = context.get("time_window", {})
        org = context.get("org", {})
        
        project_key = project_config.get("key", "PROJ")
        project_name = project_config.get("name", "Product Development")
        sprint_length = project_config.get("sprint_length_days", 14)
        
        task_description = f"""
        Create a comprehensive product strategy for the following project:
        
        Project Configuration:
        - Key: {project_key}
        - Name: {project_name}
        - Sprint Length: {sprint_length} days
        - Time Window: {time_window.get('start')} to {time_window.get('end')}
        - Team: {org.get('team_name')}
        
        Company Context:
        - Industry: Fintech SaaS
        - Products: {company_context.get('products', [])}
        - Mission: Focus on digital payments for SMEs in India
        
        Your deliverables:
        
        1. PROJECT DEFINITION:
        - project_id: PROJ-{project_key}
        - key: {project_key}
        - name: {project_name}
        - description: Detailed project description (2-3 sentences)
        
        2. EPICS (create 2-3 epics):
        For each epic:
        - epic_id: EPIC-{project_key}-01, EPIC-{project_key}-02, etc.
        - project_id: PROJ-{project_key}
        - title: Epic title
        - description: Epic description with business value
        - owner_id: Assign to TL or Mgr level team members
        
        Epic themes for Payments Reliability:
        - Payment Gateway Optimization
        - Fraud Detection Enhancement
        - System Monitoring & Alerting
        - API Performance Improvement
        - Customer Experience Enhancement
        
        3. OKRs (2-3 objectives):
        For each OKR:
        - objective: What we want to achieve
        - key_results: 3-4 measurable outcomes
        - owner_id: Person responsible
        - timeline: When to achieve by
        
        Example fintech OKRs:
        - Improve payment success rate from 95% to 98%
        - Reduce average transaction processing time by 30%
        - Achieve 99.9% API uptime
        - Decrease fraud rate to below 0.1%
        
        Ensure all objectives are:
        - Achievable within the time window
        - Measurable with specific metrics
        - Aligned with business value
        - Owned by appropriate team members
        
        Return structured data with project, epics list, and okrs list.
        """
        
        return Task(
            description=task_description,
            agent=self.agent,
            expected_output="A dictionary with project, epics, and okrs"
        )
