"""Organization Designer agent for creating team structure."""

from typing import Any, Dict

from crewai import Task
from .base import BaseAgent


class OrgDesignerAgent(BaseAgent):
    """Agent responsible for designing organization structure and team members."""

    @property
    def role(self) -> str:
        return "Organization Design Specialist"

    @property
    def goal(self) -> str:
        return "Create realistic team structures with proper hierarchy, reporting lines, and role distribution"

    @property
    def backstory(self) -> str:
        return """You are an expert in organizational design with deep knowledge of engineering 
        team structures, reporting hierarchies, and role distributions. You understand how to 
        create balanced teams with appropriate spans of control and skill distributions across 
        different engineering levels."""

    def create_task(self, description: str, context: Dict[str, Any]) -> Task:
        """Create organization design task."""
        org_config = context.get("org", {})
        company_context = context.get("company_context", {})
        
        team_name = org_config.get("team_name", "Engineering Team")
        levels = org_config.get("levels", ["Jr", "Sr", "TL", "Mgr"])
        manager_span = org_config.get("manager_span", {"min": 6, "max": 8})
        geo_locations = org_config.get("geo", ["Bengaluru", "Mumbai", "Remote-IN"])
        
        task_description = f"""
        Design a {team_name} organization structure with the following requirements:
        
        Team Configuration:
        - Team Name: {team_name}
        - Levels: {levels}
        - Manager Span: {manager_span["min"]}-{manager_span["max"]} direct reports
        - Geographic Distribution: {geo_locations}
        
        Requirements:
        1. Create 7-10 team members with realistic Indian names
        2. Ensure proper level distribution (30% Jr, 45% Sr, 20% TL, 5% Mgr)
        3. Establish clear reporting hierarchy
        4. Assign realistic skill sets based on levels
        5. Distribute across geographic locations
        6. Ensure manager span of control is within limits
        
        For each person, generate:
        - person_id (format: PER-0001)
        - name (realistic Indian names)
        - role (Software Engineer | Team Lead | Engineering Manager)
        - level (Jr | Sr | TL | Mgr)
        - team_id (format: TEAM-{team_name[:3].upper()})
        - manager_id (if applicable)
        - skills (5-8 relevant technical skills)
        - location (from provided geo list)
        
        Technical Skills Pool:
        - Programming: Python, Java, JavaScript, TypeScript, Go, Kotlin
        - Frameworks: React, Node.js, Spring Boot, Django, Flask
        - Databases: PostgreSQL, MongoDB, Redis, Elasticsearch
        - Cloud: AWS, GCP, Azure, Kubernetes, Docker
        - Tools: Git, Jenkins, JIRA, Confluence
        - Fintech: Payment APIs, KYC, Fraud Detection, Blockchain
        
        Level-specific skill distributions:
        - Jr: 3-5 skills, focus on core technologies
        - Sr: 5-7 skills, broader stack knowledge
        - TL: 6-8 skills, including leadership and architecture
        - Mgr: 5-7 skills, strategic and people management focus
        
        Return a list of Person objects with all required fields populated.
        """
        
        return Task(
            description=task_description,
            agent=self.agent,
            expected_output="A list of Person objects representing the team structure"
        )
