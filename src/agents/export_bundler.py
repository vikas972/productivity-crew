"""Export Bundler agent for generating final output files."""

from typing import Any, Dict

from crewai import Task
from .base import BaseAgent


class ExportBundlerAgent(BaseAgent):
    """Agent responsible for exporting data to final output formats."""

    @property
    def role(self) -> str:
        return "Data Export Specialist"

    @property
    def goal(self) -> str:
        return "Export all generated data to properly formatted JSON and JSONL files with integrity verification"

    @property
    def backstory(self) -> str:
        return """You are an expert in data serialization and export formats. You understand 
        the importance of data integrity, proper formatting, and comprehensive metadata for 
        exported datasets. You ensure that exported data is immediately usable and includes 
        all necessary verification information."""

    def create_task(self, description: str, context: Dict[str, Any]) -> Task:
        """Create export bundling task."""
        okg_data = context.get("okg_data", {})
        output_config = context.get("outputs", ["jira", "email"])
        output_dir = context.get("output_dir", "out")
        
        task_description = f"""
        Export all generated data to the specified output formats:
        
        Output Configuration:
        - Output Directory: {output_dir}
        - Formats: {output_config}
        - Data Available: {list(okg_data.keys())}
        
        EXPORT TASKS:
        
        1. JIRA EXPORT (if "jira" in outputs):
        File: out/jira.json
        Content: All tickets with complete lifecycle data
        Format: Single JSON file with array of Ticket objects
        
        Requirements:
        - Deterministic ordering by ticket_id
        - All fields populated according to schema
        - Proper datetime formatting (ISO 8601 with timezone)
        - Validate against JSON schema before export
        
        2. EMAIL EXPORT (if "email" in outputs):
        Files: out/mail_<person_id>.jsonl (one per person)
        Content: All email messages for each person
        Format: JSONL (one MailMessage object per line)
        
        Requirements:
        - One file per team member
        - Deterministic ordering by timestamp within each file
        - Proper datetime formatting
        - Handle special characters and encoding properly
        
        3. INDEX FILE:
        File: out/index.json
        Content: Metadata about the export
        
        Include:
        - generation_timestamp: When the export was created
        - configuration_hash: Hash of input configuration
        - file_manifest: List of all generated files with metadata
        - statistics: Counts and summaries
        - integrity_hash: SHA-256 hash for verification
        
        File Manifest Schema:
        {{
          "filename": "jira.json",
          "type": "jira_tickets",
          "record_count": 35,
          "file_size_bytes": 125840,
          "sha256_hash": "abc123...",
          "schema_version": "1.0"
        }}
        
        Statistics Schema:
        {{
          "total_persons": 8,
          "total_tickets": 35,
          "total_emails": 320,
          "tickets_by_type": {{"Story": 21, "Bug": 9, "Task": 4, "Spike": 1}},
          "tickets_by_priority": {{"Low": 11, "Medium": 17, "High": 5, "Critical": 2}},
          "emails_by_category": {{"work": 144, "managerial": 48, ...}},
          "emails_by_person": {{"PER-0001": 42, "PER-0002": 38, ...}}
        }}
        
        4. DATA INTEGRITY:
        - Generate SHA-256 hashes for all files
        - Verify JSON/JSONL format validity
        - Confirm all references are resolvable
        - Validate against provided schemas
        
        5. PRIVACY COMPLIANCE:
        - Ensure synthetic data markers are present
        - Apply redaction patterns if configured
        - No real personal information included
        - Production-like data handling
        
        6. FILE ORGANIZATION:
        Ensure clean output directory structure:
        - Remove any existing files
        - Create directory if it doesn't exist
        - Proper file permissions
        - Atomic writes (temp files then rename)
        
        ERROR HANDLING:
        - Validate all data before writing
        - Check disk space availability
        - Handle encoding issues gracefully
        - Provide detailed error messages
        
        OUTPUT VERIFICATION:
        After export, verify:
        - All expected files exist
        - File sizes are reasonable
        - JSON/JSONL parsing succeeds
        - Hash verification passes
        - Schema validation passes
        
        Return summary of export operation including:
        - Files created with paths and sizes
        - Record counts per file
        - Verification hashes
        - Any warnings or issues encountered
        """
        
        return Task(
            description=task_description,
            agent=self.agent,
            expected_output="Export summary with file manifest and verification data"
        )
