"""Unit tests for business rule validators."""

import pytest
from datetime import datetime, timezone

from src.okg.models import Person, Ticket, MailMessage, StatusTransition, Comment, MailRefs
from src.okg.repo import OKGRepository
from src.okg.validators import BusinessRuleValidator


class TestBusinessRuleValidator:
    """Test business rule validation functionality."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.repo = OKGRepository()
        self.validator = BusinessRuleValidator(self.repo)
        
        # Add test person
        self.person = Person(
            person_id="PER-0001",
            name="Test User",
            role="Software Engineer",
            level="Sr",
            team_id="TEAM-TEST",
            skills=["Python", "React"],
            location="Bengaluru"
        )
        self.repo.add_person(self.person)

    def test_ticket_mentions_in_subject_valid(self) -> None:
        """Test valid ticket mentions in email subjects."""
        # Create ticket
        ticket = Ticket(
            ticket_id="PAY-1401",
            project_id="PROJ-PAY",
            type="Story",
            title="Test ticket",
            description="Test description",
            priority="Medium",
            reporter_id="PER-0001",
            assignee_id="PER-0001",
            status_timeline=[],
            comments=[],
            attachments=[]
        )
        self.repo.add_ticket(ticket)
        
        # Create valid email
        email = MailMessage(
            msg_id="MSG-001",
            thread_id="MAIL-TH-001",
            subject="Re: [PAY-1401] Test ticket discussion",
            from_="test@example.com",
            to=["user@example.com"],
            timestamp=datetime.now(timezone.utc),
            body_md="Test content",
            category="work",
            refs=MailRefs(ticket_ids=["PAY-1401"])
        )
        
        errors = self.validator.validate_ticket_mentions_in_subject(email)
        assert len(errors) == 0

    def test_ticket_mentions_in_subject_invalid(self) -> None:
        """Test invalid ticket mentions in email subjects."""
        # Create ticket
        ticket = Ticket(
            ticket_id="PAY-1401",
            project_id="PROJ-PAY",
            type="Story",
            title="Test ticket",
            description="Test description",
            priority="Medium",
            reporter_id="PER-0001",
            assignee_id="PER-0001",
            status_timeline=[],
            comments=[],
            attachments=[]
        )
        self.repo.add_ticket(ticket)
        
        # Create invalid email (references ticket but no [PAY-1401] in subject)
        email = MailMessage(
            msg_id="MSG-001",
            thread_id="MAIL-TH-001",
            subject="Discussion about payment issue",
            from_="test@example.com",
            to=["user@example.com"],
            timestamp=datetime.now(timezone.utc),
            body_md="Test content",
            category="work",
            refs=MailRefs(ticket_ids=["PAY-1401"])
        )
        
        errors = self.validator.validate_ticket_mentions_in_subject(email)
        assert len(errors) == 1
        assert "subject doesn't contain [PAY-1401]" in errors[0]

    def test_done_tickets_have_code_review_valid(self) -> None:
        """Test that Done tickets with code review pass validation."""
        ticket = Ticket(
            ticket_id="PAY-1401",
            project_id="PROJ-PAY",
            type="Story",
            title="Test ticket",
            description="Test description",
            priority="Medium",
            reporter_id="PER-0001",
            assignee_id="PER-0001",
            status_timeline=[
                StatusTransition(status="To Do", at=datetime.now(timezone.utc)),
                StatusTransition(status="Done", at=datetime.now(timezone.utc))
            ],
            comments=[
                Comment(
                    author_id="PER-0001",
                    at=datetime.now(timezone.utc),
                    body="Code looks good to me. LGTM!"
                )
            ],
            attachments=[]
        )
        self.repo.add_ticket(ticket)
        
        errors = self.validator.validate_done_tickets_have_code_review()
        assert len(errors) == 0

    def test_done_tickets_have_code_review_invalid(self) -> None:
        """Test that Done tickets without code review fail validation."""
        ticket = Ticket(
            ticket_id="PAY-1401",
            project_id="PROJ-PAY",
            type="Story",
            title="Test ticket",
            description="Test description",
            priority="Medium",
            reporter_id="PER-0001",
            assignee_id="PER-0001",
            status_timeline=[
                StatusTransition(status="To Do", at=datetime.now(timezone.utc)),
                StatusTransition(status="Done", at=datetime.now(timezone.utc))
            ],
            comments=[
                Comment(
                    author_id="PER-0001",
                    at=datetime.now(timezone.utc),
                    body="Working on this task"
                )
            ],
            attachments=[]
        )
        self.repo.add_ticket(ticket)
        
        errors = self.validator.validate_done_tickets_have_code_review()
        assert len(errors) == 1
        assert "Done but has no code review comment" in errors[0]

    def test_ticket_references_exist_valid(self) -> None:
        """Test that valid ticket references pass validation."""
        # Create ticket
        ticket = Ticket(
            ticket_id="PAY-1401",
            project_id="PROJ-PAY",
            type="Story",
            title="Test ticket",
            description="Test description",
            priority="Medium",
            reporter_id="PER-0001",
            assignee_id="PER-0001",
            status_timeline=[],
            comments=[],
            attachments=[]
        )
        self.repo.add_ticket(ticket)
        
        # Create email referencing existing ticket
        email = MailMessage(
            msg_id="MSG-001",
            thread_id="MAIL-TH-001",
            subject="Test email",
            from_="test@example.com",
            to=["user@example.com"],
            timestamp=datetime.now(timezone.utc),
            body_md="Test content",
            category="work",
            refs=MailRefs(ticket_ids=["PAY-1401"])
        )
        self.repo.add_mail_message("PER-0001", email)
        
        errors = self.validator.validate_ticket_references_exist()
        assert len(errors) == 0

    def test_ticket_references_exist_invalid(self) -> None:
        """Test that invalid ticket references fail validation."""
        # Create email referencing non-existent ticket
        email = MailMessage(
            msg_id="MSG-001",
            thread_id="MAIL-TH-001",
            subject="Test email",
            from_="test@example.com",
            to=["user@example.com"],
            timestamp=datetime.now(timezone.utc),
            body_md="Test content",
            category="work",
            refs=MailRefs(ticket_ids=["PAY-9999"])  # Non-existent ticket
        )
        self.repo.add_mail_message("PER-0001", email)
        
        errors = self.validator.validate_ticket_references_exist()
        assert len(errors) == 1
        assert "references non-existent ticket PAY-9999" in errors[0]

    def test_manager_inbox_diversity_valid(self) -> None:
        """Test that manager inbox with sufficient diversity passes."""
        # Create manager
        manager = Person(
            person_id="PER-0002",
            name="Test Manager",
            role="Engineering Manager",
            level="Mgr",
            team_id="TEAM-TEST",
            skills=["Leadership"],
            location="Mumbai"
        )
        self.repo.add_person(manager)
        
        # Add diverse emails (25% non-project)
        emails = [
            # 3 work emails (75%)
            MailMessage(
                msg_id="MSG-001",
                thread_id="MAIL-TH-001",
                subject="Work email 1",
                from_="test@example.com",
                to=["manager@example.com"],
                timestamp=datetime.now(timezone.utc),
                body_md="Work content",
                category="work"
            ),
            MailMessage(
                msg_id="MSG-002",
                thread_id="MAIL-TH-002",
                subject="Work email 2",
                from_="test@example.com",
                to=["manager@example.com"],
                timestamp=datetime.now(timezone.utc),
                body_md="Work content",
                category="work"
            ),
            MailMessage(
                msg_id="MSG-003",
                thread_id="MAIL-TH-003",
                subject="Work email 3",
                from_="test@example.com",
                to=["manager@example.com"],
                timestamp=datetime.now(timezone.utc),
                body_md="Work content",
                category="work"
            ),
            # 1 corporate email (25%)
            MailMessage(
                msg_id="MSG-004",
                thread_id="MAIL-TH-004",
                subject="Corporate update",
                from_="corp@example.com",
                to=["manager@example.com"],
                timestamp=datetime.now(timezone.utc),
                body_md="Corporate content",
                category="corporate"
            ),
        ]
        
        for email in emails:
            self.repo.add_mail_message("PER-0002", email)
        
        errors = self.validator.validate_manager_inbox_diversity()
        assert len(errors) == 0

    def test_manager_inbox_diversity_invalid(self) -> None:
        """Test that manager inbox without sufficient diversity fails."""
        # Create manager
        manager = Person(
            person_id="PER-0002",
            name="Test Manager",
            role="Engineering Manager",
            level="Mgr",
            team_id="TEAM-TEST",
            skills=["Leadership"],
            location="Mumbai"
        )
        self.repo.add_person(manager)
        
        # Add only work emails (0% non-project)
        emails = [
            MailMessage(
                msg_id=f"MSG-{i:03d}",
                thread_id=f"MAIL-TH-{i:03d}",
                subject=f"Work email {i}",
                from_="test@example.com",
                to=["manager@example.com"],
                timestamp=datetime.now(timezone.utc),
                body_md="Work content",
                category="work"
            )
            for i in range(1, 6)  # 5 work emails
        ]
        
        for email in emails:
            self.repo.add_mail_message("PER-0002", email)
        
        errors = self.validator.validate_manager_inbox_diversity()
        assert len(errors) == 1
        assert "should be ≥20%" in errors[0]

    def test_validation_summary(self) -> None:
        """Test validation summary generation."""
        summary = self.validator.get_validation_summary()
        
        assert "passed" in summary
        assert "total_errors" in summary
        assert "errors_by_category" in summary
        assert "detailed_errors" in summary
        
        assert isinstance(summary["passed"], bool)
        assert isinstance(summary["total_errors"], int)
        assert isinstance(summary["errors_by_category"], dict)
        assert isinstance(summary["detailed_errors"], dict)
