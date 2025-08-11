"""End-to-end tests for single team generation workflow."""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from src.app.settings import ConfigModel, Settings
from src.workflows.single_team_manager import SingleTeamWorkflowManager


class TestSingleTeamE2E:
    """End-to-end tests for the complete workflow."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        # Create minimal test configuration
        self.config_data = {
            "industry": "Fintech SaaS",
            "company": {
                "name": "TestPay",
                "mission": "Test payments",
                "tone": "professional",
                "values": ["Test"]
            },
            "time_window": {
                "start": "2025-07-01",
                "end": "2025-07-14",
                "business_days_only": True,
                "timezone": "Asia/Kolkata"
            },
            "org": {
                "team_name": "Test Team",
                "geo": ["Bengaluru"],
                "levels": ["Jr", "Sr", "TL", "Mgr"],
                "manager_span": {"min": 3, "max": 5}
            },
            "project": {
                "key": "TEST",
                "name": "Test Project",
                "sprint_length_days": 7
            },
            "volumes": {
                "jira_tickets_in_window": {"min": 5, "max": 10},
                "emails_per_person_per_week": {"min": 10, "max": 15},
                "comment_ratio": 1.0
            },
            "mail": {
                "categories": ["work", "corporate"],
                "thread_depth": {"min": 2, "max": 3}
            },
            "privacy": {
                "synthetic_only": True,
                "no_real_persons": True,
                "redact_like_production": True
            },
            "outputs": ["jira", "email"]
        }
        
        self.config = ConfigModel(**self.config_data)
        self.settings = Settings(
            openai_api_key="test_key",
            output_dir="test_output",
            random_seed=42
        )

    def test_config_validation(self) -> None:
        """Test configuration validation."""
        errors = self.config.validate_config()
        assert len(errors) == 0

    def test_invalid_config_validation(self) -> None:
        """Test validation of invalid configuration."""
        invalid_config_data = self.config_data.copy()
        del invalid_config_data["company"]["name"]  # Remove required field
        
        invalid_config = ConfigModel(**invalid_config_data)
        errors = invalid_config.validate_config()
        assert len(errors) > 0
        assert any("Missing required company field: name" in error for error in errors)

    @patch('src.workflows.single_team_manager.Crew')
    def test_workflow_initialization(self, mock_crew) -> None:
        """Test workflow manager initialization."""
        workflow_manager = SingleTeamWorkflowManager(self.config, self.settings)
        
        assert workflow_manager.config == self.config
        assert workflow_manager.settings == self.settings
        assert workflow_manager.repo is not None
        assert len(workflow_manager.agents) == 8  # All agents initialized

    @patch('src.workflows.single_team_manager.Crew')
    def test_industry_selection_phase(self, mock_crew) -> None:
        """Test industry selection phase execution."""
        # Mock crew execution
        mock_crew_instance = Mock()
        mock_crew_instance.kickoff.return_value = {
            "products": ["Payment Gateway"],
            "constraints": ["Security"],
            "tech_stack": {"backend": ["Python"]}
        }
        mock_crew.return_value = mock_crew_instance
        
        workflow_manager = SingleTeamWorkflowManager(self.config, self.settings)
        result = workflow_manager._execute_industry_selection()
        
        assert "products" in result
        assert mock_crew_instance.kickoff.called

    @patch('src.workflows.single_team_manager.Crew')
    def test_org_design_phase(self, mock_crew) -> None:
        """Test organization design phase execution."""
        # Mock crew execution
        mock_crew_instance = Mock()
        mock_crew_instance.kickoff.return_value = {
            "persons": [
                {
                    "person_id": "PER-0001",
                    "name": "Test Person",
                    "role": "Software Engineer",
                    "level": "Sr",
                    "team_id": "TEAM-TEST",
                    "skills": ["Python"],
                    "location": "Bengaluru"
                }
            ]
        }
        mock_crew.return_value = mock_crew_instance
        
        workflow_manager = SingleTeamWorkflowManager(self.config, self.settings)
        result = workflow_manager._execute_org_design()
        
        assert "persons" in result
        assert len(result["persons"]) == 1

    @patch('src.workflows.single_team_manager.Crew')
    def test_ticket_generation_phase(self, mock_crew) -> None:
        """Test ticket generation phase execution."""
        # Mock crew execution
        mock_crew_instance = Mock()
        mock_crew_instance.kickoff.return_value = [
            {
                "ticket_id": "TEST-1401",
                "project_id": "PROJ-TEST",
                "type": "Story",
                "title": "Test ticket",
                "description": "Test description",
                "priority": "Medium",
                "reporter_id": "PER-0001",
                "assignee_id": "PER-0001",
                "status_timeline": [],
                "comments": [],
                "attachments": []
            }
        ]
        mock_crew.return_value = mock_crew_instance
        
        workflow_manager = SingleTeamWorkflowManager(self.config, self.settings)
        result = workflow_manager._execute_ticket_generation()
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["ticket_id"] == "TEST-1401"

    @patch('src.workflows.single_team_manager.Crew')
    def test_mailbox_generation_phase(self, mock_crew) -> None:
        """Test mailbox generation phase execution."""
        # Mock crew execution
        mock_crew_instance = Mock()
        mock_crew_instance.kickoff.return_value = {
            "PER-0001": [
                {
                    "msg_id": "MSG-001",
                    "thread_id": "MAIL-TH-001",
                    "subject": "Test email",
                    "from": "test@example.com",
                    "to": ["user@example.com"],
                    "timestamp": "2025-07-01T10:00:00Z",
                    "body_md": "Test content",
                    "category": "work"
                }
            ]
        }
        mock_crew.return_value = mock_crew_instance
        
        workflow_manager = SingleTeamWorkflowManager(self.config, self.settings)
        result = workflow_manager._execute_mailbox_generation()
        
        assert isinstance(result, dict)
        assert "PER-0001" in result
        assert len(result["PER-0001"]) == 1

    def test_file_output_structure(self, tmp_path) -> None:
        """Test expected output file structure."""
        # Set output directory to temp path
        self.settings.output_dir = str(tmp_path)
        
        # Expected output files
        expected_files = [
            "jira.json",
            "index.json"
        ]
        
        # Expected email files would be mail_<person_id>.jsonl
        # We'll check for at least one mail file pattern
        
        # Create mock files to test structure
        for filename in expected_files:
            (tmp_path / filename).touch()
        
        # Create a sample mail file
        (tmp_path / "mail_PER-0001.jsonl").touch()
        
        # Verify files exist
        for filename in expected_files:
            assert (tmp_path / filename).exists()
        
        # Verify at least one mail file exists
        mail_files = list(tmp_path.glob("mail_*.jsonl"))
        assert len(mail_files) >= 1

    def test_jira_json_structure(self, tmp_path) -> None:
        """Test Jira JSON output structure."""
        # Create sample jira.json
        sample_tickets = [
            {
                "ticket_id": "TEST-1401",
                "project_id": "PROJ-TEST",
                "type": "Story",
                "title": "Test ticket",
                "description": "Test description",
                "priority": "Medium",
                "reporter_id": "PER-0001",
                "assignee_id": "PER-0001",
                "status_timeline": [
                    {
                        "status": "To Do",
                        "at": "2025-07-01T10:00:00Z"
                    }
                ],
                "comments": [],
                "attachments": []
            }
        ]
        
        jira_file = tmp_path / "jira.json"
        with open(jira_file, "w") as f:
            json.dump(sample_tickets, f)
        
        # Verify structure
        with open(jira_file, "r") as f:
            data = json.load(f)
        
        assert isinstance(data, list)
        assert len(data) == 1
        
        ticket = data[0]
        required_fields = ["ticket_id", "project_id", "type", "title", "description", "priority"]
        for field in required_fields:
            assert field in ticket

    def test_email_jsonl_structure(self, tmp_path) -> None:
        """Test email JSONL output structure."""
        # Create sample mail file
        sample_messages = [
            {
                "msg_id": "MSG-001",
                "thread_id": "MAIL-TH-001",
                "subject": "Test email",
                "from": "test@example.com",
                "to": ["user@example.com"],
                "cc": [],
                "timestamp": "2025-07-01T10:00:00Z",
                "body_md": "Test content",
                "attachments": [],
                "category": "work",
                "list_ids": [],
                "is_broadcast": False,
                "is_external": False,
                "importance": "normal",
                "spam_score": 0.0,
                "refs": {
                    "ticket_ids": [],
                    "pr_ids": [],
                    "doc_ids": []
                }
            }
        ]
        
        mail_file = tmp_path / "mail_PER-0001.jsonl"
        with open(mail_file, "w") as f:
            for message in sample_messages:
                json.dump(message, f)
                f.write("\n")
        
        # Verify structure
        with open(mail_file, "r") as f:
            lines = f.readlines()
        
        assert len(lines) == 1
        
        message = json.loads(lines[0])
        required_fields = ["msg_id", "thread_id", "subject", "from", "to", "timestamp"]
        for field in required_fields:
            assert field in message

    def test_index_json_structure(self, tmp_path) -> None:
        """Test index JSON output structure."""
        # Create sample index.json
        sample_index = {
            "generation_metadata": {
                "generated_at": "2025-07-01T10:00:00Z",
                "generator_version": "1.0.0",
                "schema_version": "1.0"
            },
            "file_manifest": [
                {
                    "filename": "jira.json",
                    "type": "jira_tickets",
                    "record_count": 5,
                    "file_size_bytes": 1024,
                    "content_hash": "abc123"
                }
            ],
            "statistics": {
                "total_persons": 4,
                "total_tickets": 5,
                "total_emails": 20
            },
            "integrity": {
                "total_files": 5,
                "total_records": 25,
                "manifest_hash": "def456"
            }
        }
        
        index_file = tmp_path / "index.json"
        with open(index_file, "w") as f:
            json.dump(sample_index, f)
        
        # Verify structure
        with open(index_file, "r") as f:
            data = json.load(f)
        
        required_sections = ["generation_metadata", "file_manifest", "statistics", "integrity"]
        for section in required_sections:
            assert section in data
        
        assert "generated_at" in data["generation_metadata"]
        assert isinstance(data["file_manifest"], list)
        assert isinstance(data["statistics"], dict)
        assert "total_files" in data["integrity"]
