"""Industry Selector agent for generating company context."""

from typing import Any, Dict

from crewai import Task
from .base import BaseAgent


class IndustrySelectorAgent(BaseAgent):
    """Agent responsible for generating company context based on industry."""

    @property
    def role(self) -> str:
        return "Industry Context Specialist"

    @property
    def goal(self) -> str:
        return "Generate realistic company context including tone, products, and constraints for the specified industry"

    @property
    def backstory(self) -> str:
        return """You are an expert in various industries and understand how companies in different 
        sectors operate, communicate, and structure their products. You specialize in creating 
        authentic company contexts that reflect real-world industry practices, especially in 
        the Indian market."""

    def create_task(self, description: str, context: Dict[str, Any]) -> Task:
        """Create industry selection task."""
        industry = context.get("industry", "Fintech SaaS")
        company_config = context.get("company", {})
        
        task_description = f"""
        Generate a comprehensive company context for a {industry} company with the following requirements:
        
        Base Information:
        - Company Name: {company_config.get('name', 'TechCorp')}
        - Mission: {company_config.get('mission', 'Innovation in technology')}
        - Tone: {company_config.get('tone', 'professional')}
        - Values: {company_config.get('values', [])}
        
        Your task is to expand this into a rich company context including:
        1. Industry-specific products and services (3-5 key offerings)
        2. Market constraints and challenges specific to this industry
        3. Regulatory considerations
        4. Technology stack preferences
        5. Communication style guidelines
        6. Customer base characteristics
        
        For Fintech SaaS specifically, consider:
        - Digital payment solutions
        - SME focus in India
        - Regulatory compliance (RBI guidelines)
        - Security and trust requirements
        - Integration challenges
        - Scalability needs
        
        Return a structured dictionary with:
        - products: List of 3-5 product/service offerings
        - constraints: List of 3-5 industry-specific challenges
        - tech_stack: Preferred technologies
        - communication_style: Detailed style guide
        - target_customers: Customer segment descriptions
        """
        
        return Task(
            description=task_description,
            agent=self.agent,
            expected_output="A comprehensive company context dictionary"
        )
