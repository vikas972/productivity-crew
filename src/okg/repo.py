"""Repository pattern for managing generated data."""

from typing import Dict, List, Optional, Any
from datetime import datetime

from .models import Person, Ticket, MailMessage, Team, Project, Epic, Sprint


class OKGRepository:
    """Central repository for all generated organizational knowledge graph data."""

    def __init__(self) -> None:
        """Initialize empty repository."""
        self.persons: Dict[str, Person] = {}
        self.tickets: Dict[str, Ticket] = {}
        self.mail_messages: Dict[str, List[MailMessage]] = {}
        self.teams: Dict[str, Team] = {}
        self.projects: Dict[str, Project] = {}
        self.epics: Dict[str, Epic] = {}
        self.sprints: Dict[str, Sprint] = {}
        
        # Metadata
        self.company_context: Dict[str, Any] = {}
        self.calendar_templates: List[Dict[str, Any]] = []
        self.integrity_report: Dict[str, Any] = {}

    def add_person(self, person: Person) -> None:
        """Add a person to the repository."""
        self.persons[person.person_id] = person

    def add_ticket(self, ticket: Ticket) -> None:
        """Add a ticket to the repository."""
        self.tickets[ticket.ticket_id] = ticket

    def add_mail_message(self, person_id: str, message: MailMessage) -> None:
        """Add a mail message to a person's mailbox."""
        if person_id not in self.mail_messages:
            self.mail_messages[person_id] = []
        self.mail_messages[person_id].append(message)

    def add_team(self, team: Team) -> None:
        """Add a team to the repository."""
        self.teams[team.team_id] = team

    def add_project(self, project: Project) -> None:
        """Add a project to the repository."""
        self.projects[project.project_id] = project

    def add_epic(self, epic: Epic) -> None:
        """Add an epic to the repository."""
        self.epics[epic.epic_id] = epic

    def add_sprint(self, sprint: Sprint) -> None:
        """Add a sprint to the repository."""
        self.sprints[sprint.sprint_id] = sprint

    def get_person(self, person_id: str) -> Optional[Person]:
        """Get a person by ID."""
        return self.persons.get(person_id)

    def get_ticket(self, ticket_id: str) -> Optional[Ticket]:
        """Get a ticket by ID."""
        return self.tickets.get(ticket_id)

    def get_person_mail(self, person_id: str) -> List[MailMessage]:
        """Get all mail messages for a person."""
        return self.mail_messages.get(person_id, [])

    def get_team_members(self, team_id: str) -> List[Person]:
        """Get all members of a team."""
        return [p for p in self.persons.values() if p.team_id == team_id]

    def get_project_tickets(self, project_id: str) -> List[Ticket]:
        """Get all tickets for a project."""
        project_key = project_id.split("-")[-1]  # PROJ-PAY -> PAY
        return [t for t in self.tickets.values() if t.ticket_id.startswith(project_key)]

    def get_epic_tickets(self, epic_id: str) -> List[Ticket]:
        """Get all tickets for an epic."""
        return [t for t in self.tickets.values() if t.epic_id == epic_id]

    def get_assignee_tickets(self, person_id: str) -> List[Ticket]:
        """Get all tickets assigned to a person."""
        return [t for t in self.tickets.values() if t.assignee_id == person_id]

    def get_tickets_by_status(self, status: str) -> List[Ticket]:
        """Get all tickets with a specific current status."""
        tickets = []
        for ticket in self.tickets.values():
            if ticket.status_timeline and ticket.status_timeline[-1].status == status:
                tickets.append(ticket)
        return tickets

    def get_tickets_in_timeframe(
        self, start: datetime, end: datetime
    ) -> List[Ticket]:
        """Get tickets that had activity in the given timeframe."""
        tickets = []
        for ticket in self.tickets.values():
            # Check if any status transition or comment is in timeframe
            for transition in ticket.status_timeline:
                if start <= transition.at <= end:
                    tickets.append(ticket)
                    break
            else:
                for comment in ticket.comments:
                    if start <= comment.at <= end:
                        tickets.append(ticket)
                        break
        return tickets

    def get_mail_in_timeframe(
        self, person_id: str, start: datetime, end: datetime
    ) -> List[MailMessage]:
        """Get mail messages for a person in the given timeframe."""
        messages = self.get_person_mail(person_id)
        return [m for m in messages if start <= m.timestamp <= end]

    def validate_references(self) -> List[str]:
        """Validate referential integrity and return list of errors."""
        errors = []
        
        # Check person manager references
        for person in self.persons.values():
            if person.manager_id and person.manager_id not in self.persons:
                errors.append(f"Person {person.person_id} has invalid manager_id {person.manager_id}")
        
        # Check ticket assignee/reporter references
        for ticket in self.tickets.values():
            if ticket.assignee_id not in self.persons:
                errors.append(f"Ticket {ticket.ticket_id} has invalid assignee_id {ticket.assignee_id}")
            if ticket.reporter_id not in self.persons:
                errors.append(f"Ticket {ticket.ticket_id} has invalid reporter_id {ticket.reporter_id}")
        
        # Check mail message ticket references
        for person_id, messages in self.mail_messages.items():
            for message in messages:
                for ticket_id in message.refs.ticket_ids:
                    if ticket_id not in self.tickets:
                        errors.append(f"Mail {message.msg_id} references invalid ticket {ticket_id}")
        
        return errors

    def get_statistics(self) -> Dict[str, Any]:
        """Get repository statistics."""
        return {
            "persons": len(self.persons),
            "tickets": len(self.tickets),
            "mail_messages": sum(len(msgs) for msgs in self.mail_messages.values()),
            "teams": len(self.teams),
            "projects": len(self.projects),
            "epics": len(self.epics),
            "sprints": len(self.sprints),
        }
