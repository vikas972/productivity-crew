"""Jira source generator for ticket data."""

import json
from typing import Any, Dict, List
from pathlib import Path

from ..base import BaseSourceGenerator
from ...okg.models import Ticket
from ...utils.hashing import DeterministicHasher


class JiraGenerator(BaseSourceGenerator):
    """Generator for Jira ticket export format."""

    def generate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate jira.json from ticket data."""
        self.log_generation_start("jira")
        
        tickets = data.get("tickets", [])
        if not tickets:
            raise ValueError("No tickets available for Jira generation")
        
        # Ensure output directory exists
        self.ensure_output_dir()
        
        # Sort tickets deterministically by ticket_id
        sorted_tickets = sorted(tickets, key=lambda t: t.ticket_id)
        
        # Convert to dictionaries for JSON serialization
        ticket_dicts = []
        for ticket in sorted_tickets:
            if isinstance(ticket, Ticket):
                ticket_dict = ticket.model_dump()
                # Handle the alias for 'from' field if needed
                ticket_dicts.append(ticket_dict)
            else:
                ticket_dicts.append(ticket)
        
        # Write to jira.json
        output_file = self.output_dir / "jira.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(ticket_dicts, f, indent=2, default=str, ensure_ascii=False)
        
        # Generate metadata
        file_size = output_file.stat().st_size
        content_hash = DeterministicHasher.batch_fingerprint(ticket_dicts)
        
        result = {
            "file_path": str(output_file),
            "ticket_count": len(ticket_dicts),
            "file_size_bytes": file_size,
            "content_hash": content_hash,
            "tickets_by_type": self._count_by_field(ticket_dicts, "type"),
            "tickets_by_priority": self._count_by_field(ticket_dicts, "priority"),
            "tickets_by_status": self._count_current_status(ticket_dicts),
        }
        
        self.log_generation_complete("jira", result)
        return result

    def validate_output(self, output: Dict[str, Any]) -> List[str]:
        """Validate Jira output."""
        errors = []
        
        file_path = Path(output.get("file_path", ""))
        if not file_path.exists():
            errors.append(f"Jira output file does not exist: {file_path}")
            return errors
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                errors.append("Jira JSON should be an array of tickets")
                return errors
            
            # Validate each ticket has required fields
            required_fields = ["ticket_id", "project_id", "type", "title", "description", "priority"]
            for i, ticket in enumerate(data):
                for field in required_fields:
                    if field not in ticket:
                        errors.append(f"Ticket {i} missing required field: {field}")
                
                # Validate ticket_id format
                if not ticket.get("ticket_id", "").match(r"^[A-Z]+-\d+$"):
                    errors.append(f"Ticket {i} has invalid ticket_id format: {ticket.get('ticket_id')}")
        
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON in Jira output: {e}")
        except Exception as e:
            errors.append(f"Error validating Jira output: {e}")
        
        return errors

    def _count_by_field(self, tickets: List[Dict[str, Any]], field: str) -> Dict[str, int]:
        """Count tickets by a specific field."""
        counts: Dict[str, int] = {}
        for ticket in tickets:
            value = ticket.get(field, "Unknown")
            counts[value] = counts.get(value, 0) + 1
        return counts

    def _count_current_status(self, tickets: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count tickets by current status (last status in timeline)."""
        counts: Dict[str, int] = {}
        for ticket in tickets:
            status_timeline = ticket.get("status_timeline", [])
            if status_timeline:
                current_status = status_timeline[-1].get("status", "Unknown")
                counts[current_status] = counts.get(current_status, 0) + 1
            else:
                counts["No Status"] = counts.get("No Status", 0) + 1
        return counts
