"""QA Auditor agent for validating generated content."""

from typing import Any, Dict

from crewai import Task
from .base import BaseAgent


class QAAuditorAgent(BaseAgent):
    """Agent responsible for validating all generated content against business rules."""

    @property
    def role(self) -> str:
        return "Quality Assurance Auditor"

    @property
    def goal(self) -> str:
        return "Validate all generated content for referential integrity, business rules, and data quality"

    @property
    def backstory(self) -> str:
        return """You are a meticulous quality assurance specialist with expertise in data 
        validation, business rule compliance, and system integrity checks. You understand 
        the importance of data consistency and can identify issues that would compromise 
        the realism and usability of synthetic datasets."""

    def create_task(self, description: str, context: Dict[str, Any]) -> Task:
        """Create QA audit task."""
        okg_data = context.get("okg_data", {})
        validation_rules = context.get("validation_rules", [])
        
        task_description = f"""
        Perform comprehensive quality assurance audit on all generated data:
        
        Data to Validate:
        - Persons: {len(okg_data.get('persons', []))} team members
        - Tickets: {len(okg_data.get('tickets', []))} Jira tickets
        - Mail Messages: {sum(len(msgs) for msgs in okg_data.get('mail_messages', {}).values())} emails
        - Projects: {len(okg_data.get('projects', []))} projects
        - Epics: {len(okg_data.get('epics', []))} epics
        - Sprints: {len(okg_data.get('sprints', []))} sprints
        
        VALIDATION CATEGORIES:
        
        1. REFERENTIAL INTEGRITY:
        - All person manager_ids reference valid persons
        - All ticket assignee_ids and reporter_ids reference valid persons
        - All email ticket references point to existing tickets
        - All epic project_ids reference valid projects
        - All ticket epic_ids reference valid epics
        
        2. BUSINESS RULES VALIDATION:
        
        Ticket Mention Rule:
        - Email subjects MUST contain [KEY-####] when referencing tickets
        - refs.ticket_ids MUST be populated when tickets are mentioned
        - Ticket IDs in subjects must match refs.ticket_ids
        
        Done Ticket Rule:
        - Tickets with "Done" status MUST have code review comments
        - Code review indicators: "lgtm", "looks good", "approved", "reviewed"
        - At least one comment must indicate code review completion
        
        Manager Inbox Diversity:
        - Manager inboxes MUST have ≥20% non-project email categories
        - Non-project categories: corporate, hr, vendor, security, event, facilities, spam, phishing_sim
        - Calculate percentage and flag violations
        
        Business Hours Realism:
        - ≤15% of emails should be outside business hours (9 AM - 6 PM IST)
        - Weekend emails should be minimal and justified
        - After-hours emails should have context explaining urgency
        
        Spam Limits:
        - Spam category should be ≤5% of total emails per person
        - Phishing simulation should be ≤1% of total emails per person
        - Flag accounts with excessive spam
        
        3. DATA QUALITY CHECKS:
        
        Timeline Consistency:
        - Ticket status transitions must be chronological
        - Email timestamps must be realistic
        - Sprint dates must not overlap incorrectly
        - Comments must align with ticket status at time of creation
        
        Deterministic Ordering:
        - Tickets ordered by ticket_id
        - Emails ordered by timestamp within each person
        - All IDs follow proper format patterns
        - Consistent data across multiple runs
        
        Content Realism:
        - Technical terms appropriate for fintech domain
        - Indian context maintained (names, locations, timezone)
        - Appropriate complexity distribution across skill levels
        - Realistic communication patterns by role
        
        4. SCHEMA COMPLIANCE:
        - All objects conform to Pydantic models
        - Required fields populated
        - Field formats match regex patterns
        - Enum values within allowed ranges
        
        5. VOLUME VALIDATION:
        - Ticket count within configured range
        - Email volume per person within configured range
        - Comment ratio approximately matches configuration
        - Sprint count appropriate for time window
        
        AUDIT OUTPUT:
        
        Generate an IntegrityReport with:
        - passed: boolean (true if all validations pass)
        - errors: list of critical errors that must be fixed
        - warnings: list of issues that should be reviewed
        - ticket_count: total tickets generated
        - email_count: total emails generated
        - person_count: total persons generated
        
        Error Severity:
        - CRITICAL: Referential integrity failures, business rule violations
        - WARNING: Data quality issues, minor inconsistencies
        - INFO: Statistics and observations
        
        For each error/warning, include:
        - Category (referential_integrity, business_rules, data_quality, etc.)
        - Description of the issue
        - Affected entities (IDs, counts)
        - Suggested remediation
        
        Provide detailed validation results with specific examples of failures.
        """
        
        return Task(
            description=task_description,
            agent=self.agent,
            expected_output="An IntegrityReport with comprehensive validation results"
        )
