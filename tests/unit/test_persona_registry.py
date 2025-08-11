"""Unit tests for persona registry."""

import pytest

from src.okg.models import Person
from src.personas.registry import PersonaRegistry
from src.personas.base import PersonaLevel
from src.personas.jr_engineer import JuniorEngineerPersona
from src.personas.sr_engineer import SeniorEngineerPersona
from src.personas.team_lead import TeamLeadPersona
from src.personas.manager import ManagerPersona


class TestPersonaRegistry:
    """Test persona registry functionality."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.registry = PersonaRegistry()

    def test_get_persona_junior(self) -> None:
        """Test getting junior engineer persona."""
        person = Person(
            person_id="PER-0001",
            name="Junior Dev",
            role="Software Engineer",
            level="Jr",
            team_id="TEAM-TEST",
            skills=["Python"],
            location="Bengaluru"
        )
        
        persona = self.registry.get_persona(person)
        assert isinstance(persona, JuniorEngineerPersona)
        assert persona.person == person

    def test_get_persona_senior(self) -> None:
        """Test getting senior engineer persona."""
        person = Person(
            person_id="PER-0002",
            name="Senior Dev",
            role="Software Engineer",
            level="Sr",
            team_id="TEAM-TEST",
            skills=["Python", "React"],
            location="Mumbai"
        )
        
        persona = self.registry.get_persona(person)
        assert isinstance(persona, SeniorEngineerPersona)

    def test_get_persona_team_lead(self) -> None:
        """Test getting team lead persona."""
        person = Person(
            person_id="PER-0003",
            name="Team Lead",
            role="Team Lead",
            level="TL",
            team_id="TEAM-TEST",
            skills=["Python", "Leadership"],
            location="Remote-IN"
        )
        
        persona = self.registry.get_persona(person)
        assert isinstance(persona, TeamLeadPersona)

    def test_get_persona_manager(self) -> None:
        """Test getting manager persona."""
        person = Person(
            person_id="PER-0004",
            name="Engineering Manager",
            role="Engineering Manager",
            level="Mgr",
            team_id="TEAM-TEST",
            skills=["Leadership", "Strategy"],
            location="Bengaluru"
        )
        
        persona = self.registry.get_persona(person)
        assert isinstance(persona, ManagerPersona)

    def test_get_persona_invalid_level(self) -> None:
        """Test error handling for invalid persona level."""
        person = Person(
            person_id="PER-0005",
            name="Invalid Level",
            role="Software Engineer",
            level="Invalid",
            team_id="TEAM-TEST",
            skills=["Python"],
            location="Bengaluru"
        )
        
        with pytest.raises(ValueError, match="Unknown persona level"):
            self.registry.get_persona(person)

    def test_get_available_levels(self) -> None:
        """Test getting available persona levels."""
        levels = self.registry.get_available_levels()
        expected_levels = ["Jr", "Sr", "TL", "Mgr"]
        
        assert set(levels) == set(expected_levels)

    def test_get_level_distribution(self) -> None:
        """Test level distribution."""
        distribution = self.registry.get_level_distribution()
        
        assert isinstance(distribution, dict)
        assert "Jr" in distribution
        assert "Sr" in distribution
        assert "TL" in distribution
        assert "Mgr" in distribution
        
        # Check that percentages sum to 1.0
        total = sum(distribution.values())
        assert abs(total - 1.0) < 0.01

    def test_get_role_mapping(self) -> None:
        """Test role mapping."""
        mapping = self.registry.get_role_mapping()
        
        assert mapping[PersonaLevel.JUNIOR] == "Software Engineer"
        assert mapping[PersonaLevel.SENIOR] == "Software Engineer"
        assert mapping[PersonaLevel.TEAM_LEAD] == "Team Lead"
        assert mapping[PersonaLevel.MANAGER] == "Engineering Manager"

    def test_validate_team_structure_valid(self) -> None:
        """Test validation of valid team structure."""
        team_members = [
            Person(
                person_id="PER-0001",
                name="Junior Dev",
                role="Software Engineer",
                level="Jr",
                team_id="TEAM-TEST",
                skills=["Python"],
                location="Bengaluru"
            ),
            Person(
                person_id="PER-0002",
                name="Senior Dev 1",
                role="Software Engineer",
                level="Sr",
                team_id="TEAM-TEST",
                skills=["Python", "React"],
                location="Mumbai"
            ),
            Person(
                person_id="PER-0003",
                name="Senior Dev 2",
                role="Software Engineer",
                level="Sr",
                team_id="TEAM-TEST",
                skills=["Java", "Spring"],
                location="Remote-IN"
            ),
            Person(
                person_id="PER-0004",
                name="Team Lead",
                role="Team Lead",
                level="TL",
                team_id="TEAM-TEST",
                skills=["Python", "Leadership"],
                location="Bengaluru"
            ),
            Person(
                person_id="PER-0005",
                name="Manager",
                role="Engineering Manager",
                level="Mgr",
                team_id="TEAM-TEST",
                skills=["Leadership", "Strategy"],
                location="Mumbai"
            ),
        ]
        
        errors = self.registry.validate_team_structure(team_members)
        assert len(errors) == 0

    def test_validate_team_structure_no_manager(self) -> None:
        """Test validation failure when no manager present."""
        team_members = [
            Person(
                person_id="PER-0001",
                name="Junior Dev",
                role="Software Engineer",
                level="Jr",
                team_id="TEAM-TEST",
                skills=["Python"],
                location="Bengaluru"
            ),
            Person(
                person_id="PER-0002",
                name="Senior Dev",
                role="Software Engineer",
                level="Sr",
                team_id="TEAM-TEST",
                skills=["Python", "React"],
                location="Mumbai"
            ),
        ]
        
        errors = self.registry.validate_team_structure(team_members)
        assert len(errors) == 1
        assert "must have at least one manager" in errors[0]

    def test_validate_team_structure_empty(self) -> None:
        """Test validation failure for empty team."""
        errors = self.registry.validate_team_structure([])
        assert len(errors) == 1
        assert "Team cannot be empty" in errors[0]

    def test_validate_team_structure_high_span(self) -> None:
        """Test validation warning for high manager span."""
        # Create a team with 1 manager and 10 reports (span of 10)
        team_members = [
            Person(
                person_id="PER-0001",
                name="Manager",
                role="Engineering Manager",
                level="Mgr",
                team_id="TEAM-TEST",
                skills=["Leadership"],
                location="Bengaluru"
            )
        ]
        
        # Add 10 engineers
        for i in range(2, 12):
            team_members.append(
                Person(
                    person_id=f"PER-{i:04d}",
                    name=f"Engineer {i}",
                    role="Software Engineer",
                    level="Sr",
                    team_id="TEAM-TEST",
                    skills=["Python"],
                    location="Bengaluru"
                )
            )
        
        errors = self.registry.validate_team_structure(team_members)
        assert len(errors) == 1
        assert "span of control too high" in errors[0]

    def test_register_custom_persona(self) -> None:
        """Test registering custom persona implementation."""
        class CustomPersona:
            def __init__(self, person):
                self.person = person
        
        self.registry.register_persona(PersonaLevel.JUNIOR, CustomPersona)
        
        person = Person(
            person_id="PER-0001",
            name="Junior Dev",
            role="Software Engineer",
            level="Jr",
            team_id="TEAM-TEST",
            skills=["Python"],
            location="Bengaluru"
        )
        
        persona = self.registry.get_persona(person)
        assert isinstance(persona, CustomPersona)
