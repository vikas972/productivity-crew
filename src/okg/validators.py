"""Validation utilities for business rules and data integrity."""

from datetime import datetime
from typing import List, Dict, Any
import re

from .models import Ticket, MailMessage, Person
from .repo import OKGRepository


class BusinessRuleValidator:
    """Validates business rules and data integrity constraints."""

    def __init__(self, repo: OKGRepository) -> None:
        """Initialize with repository reference."""
        self.repo = repo

    def validate_ticket_mentions_in_subject(self, message: MailMessage) -> List[str]:
        """Validate that ticket mentions in email subjects follow [KEY-####] format."""
        errors = []
        
        # Check if ticket IDs are referenced in refs
        if message.refs.ticket_ids:
            # Subject should contain ticket references in proper format
            for ticket_id in message.refs.ticket_ids:
                pattern = f"\\[{ticket_id}\\]"
                if not re.search(pattern, message.subject):
                    errors.append(
                        f"Mail {message.msg_id} references {ticket_id} but subject doesn't contain [{ticket_id}]"
                    )
        
        return errors

    def validate_done_tickets_have_code_review(self) -> List[str]:
        """Validate that Done tickets have code review comments."""
        errors = []
        
        for ticket in self.repo.tickets.values():
            # Check if ticket is in Done status
            if ticket.status_timeline and ticket.status_timeline[-1].status == "Done":
                # Look for code review comments
                has_code_review = False
                code_review_keywords = ["code review", "lgtm", "approved", "looks good", "reviewed"]
                
                for comment in ticket.comments:
                    comment_lower = comment.body.lower()
                    if any(keyword in comment_lower for keyword in code_review_keywords):
                        has_code_review = True
                        break
                
                if not has_code_review:
                    errors.append(
                        f"Ticket {ticket.ticket_id} is Done but has no code review comment"
                    )
        
        return errors

    def validate_ticket_references_exist(self) -> List[str]:
        """Validate that all ticket references in emails point to real tickets."""
        errors = []
        
        for person_id, messages in self.repo.mail_messages.items():
            for message in messages:
                for ticket_id in message.refs.ticket_ids:
                    if ticket_id not in self.repo.tickets:
                        errors.append(
                            f"Mail {message.msg_id} references non-existent ticket {ticket_id}"
                        )
        
        return errors

    def validate_manager_inbox_diversity(self) -> List[str]:
        """Validate that manager inboxes have sufficient non-project email diversity."""
        errors = []
        
        # Find managers
        managers = [p for p in self.repo.persons.values() if p.level == "Mgr"]
        
        for manager in managers:
            messages = self.repo.get_person_mail(manager.person_id)
            if not messages:
                continue
            
            # Count non-project categories
            non_project_categories = [
                "corporate", "hr", "vendor", "security", "event", "facilities", "spam", "phishing_sim"
            ]
            
            non_project_count = sum(
                1 for msg in messages if msg.category in non_project_categories
            )
            
            total_messages = len(messages)
            non_project_ratio = non_project_count / total_messages if total_messages > 0 else 0
            
            if non_project_ratio < 0.2:  # Less than 20%
                errors.append(
                    f"Manager {manager.person_id} has only {non_project_ratio:.1%} non-project emails (should be ≥20%)"
                )
        
        return errors

    def validate_business_hours_realism(self) -> List[str]:
        """Validate that most emails are sent during business hours."""
        errors = []
        
        for person_id, messages in self.repo.mail_messages.items():
            if not messages:
                continue
            
            # Count messages outside business hours (9 AM - 6 PM IST)
            outside_hours = 0
            for message in messages:
                hour = message.timestamp.hour
                if hour < 9 or hour > 18:
                    outside_hours += 1
            
            total_messages = len(messages)
            outside_ratio = outside_hours / total_messages if total_messages > 0 else 0
            
            # Allow up to 15% outside business hours
            if outside_ratio > 0.15:
                errors.append(
                    f"Person {person_id} has {outside_ratio:.1%} emails outside business hours (should be ≤15%)"
                )
        
        return errors

    def validate_spam_limits(self) -> List[str]:
        """Validate spam email limits are respected."""
        errors = []
        
        for person_id, messages in self.repo.mail_messages.items():
            if not messages:
                continue
            
            spam_count = sum(1 for msg in messages if msg.category == "spam")
            total_messages = len(messages)
            spam_ratio = spam_count / total_messages if total_messages > 0 else 0
            
            # Spam should be ≤5%
            if spam_ratio > 0.05:
                errors.append(
                    f"Person {person_id} has {spam_ratio:.1%} spam emails (should be ≤5%)"
                )
        
        return errors

    def validate_deterministic_ordering(self) -> List[str]:
        """Validate that exports are deterministically ordered."""
        errors = []
        
        # Check tickets are ordered by ID
        ticket_ids = list(self.repo.tickets.keys())
        sorted_ticket_ids = sorted(ticket_ids)
        if ticket_ids != sorted_ticket_ids:
            errors.append("Tickets are not deterministically ordered by ID")
        
        # Check mail messages are ordered by timestamp within each person
        for person_id, messages in self.repo.mail_messages.items():
            timestamps = [msg.timestamp for msg in messages]
            sorted_timestamps = sorted(timestamps)
            if timestamps != sorted_timestamps:
                errors.append(f"Mail messages for {person_id} are not ordered by timestamp")
        
        return errors

    def validate_all_rules(self) -> Dict[str, List[str]]:
        """Run all validation rules and return categorized errors."""
        validation_results = {
            "ticket_subject_mentions": [],
            "done_tickets_code_review": [],
            "ticket_references": [],
            "manager_inbox_diversity": [],
            "business_hours": [],
            "spam_limits": [],
            "deterministic_ordering": [],
        }
        
        # Run all validations
        for person_id, messages in self.repo.mail_messages.items():
            for message in messages:
                validation_results["ticket_subject_mentions"].extend(
                    self.validate_ticket_mentions_in_subject(message)
                )
        
        validation_results["done_tickets_code_review"] = self.validate_done_tickets_have_code_review()
        validation_results["ticket_references"] = self.validate_ticket_references_exist()
        validation_results["manager_inbox_diversity"] = self.validate_manager_inbox_diversity()
        validation_results["business_hours"] = self.validate_business_hours_realism()
        validation_results["spam_limits"] = self.validate_spam_limits()
        validation_results["deterministic_ordering"] = self.validate_deterministic_ordering()
        
        return validation_results

    def get_validation_summary(self) -> Dict[str, Any]:
        """Get a summary of validation results."""
        results = self.validate_all_rules()
        
        total_errors = sum(len(errors) for errors in results.values())
        passed = total_errors == 0
        
        return {
            "passed": passed,
            "total_errors": total_errors,
            "errors_by_category": {k: len(v) for k, v in results.items()},
            "detailed_errors": results
        }
