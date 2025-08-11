"""Persona registry for mapping levels to implementations."""

from typing import Dict, Type

from .base import BasePersona, PersonaLevel
from .jr_engineer import JuniorEngineerPersona
from .sr_engineer import SeniorEngineerPersona
from .team_lead import TeamLeadPersona
from .manager import ManagerPersona
from ..okg.models import Person


class PersonaRegistry:
    """Registry for managing persona implementations."""

    def __init__(self) -> None:
        """Initialize persona mappings."""
        self._persona_map: Dict[PersonaLevel, Type[BasePersona]] = {
            PersonaLevel.JUNIOR: JuniorEngineerPersona,
            PersonaLevel.SENIOR: SeniorEngineerPersona,
            PersonaLevel.TEAM_LEAD: TeamLeadPersona,
            PersonaLevel.MANAGER: ManagerPersona,
        }

    def get_persona(self, person: Person) -> BasePersona:
        """Get appropriate persona instance for a person."""
        try:
            level = PersonaLevel(person.level)
        except ValueError:
            raise ValueError(f"Unknown persona level: {person.level}")
        
        persona_class = self._persona_map[level]
        return persona_class(person)

    def get_available_levels(self) -> list[str]:
        """Get list of available persona levels."""
        return [level.value for level in PersonaLevel]

    def register_persona(self, level: PersonaLevel, persona_class: Type[BasePersona]) -> None:
        """Register a custom persona implementation."""
        self._persona_map[level] = persona_class

    def get_level_distribution(self) -> Dict[str, float]:
        """Get typical organizational level distribution."""
        return {
            PersonaLevel.JUNIOR.value: 0.3,      # 30% junior engineers
            PersonaLevel.SENIOR.value: 0.45,     # 45% senior engineers
            PersonaLevel.TEAM_LEAD.value: 0.2,   # 20% team leads
            PersonaLevel.MANAGER.value: 0.05,    # 5% managers
        }

    def get_role_mapping(self) -> Dict[PersonaLevel, str]:
        """Get mapping from persona levels to role titles."""
        return {
            PersonaLevel.JUNIOR: "Software Engineer",
            PersonaLevel.SENIOR: "Software Engineer",
            PersonaLevel.TEAM_LEAD: "Team Lead",
            PersonaLevel.MANAGER: "Engineering Manager",
        }

    def validate_team_structure(self, team_members: list[Person]) -> list[str]:
        """Validate that team has appropriate structure."""
        errors = []
        
        if not team_members:
            errors.append("Team cannot be empty")
            return errors
        
        # Count levels
        level_counts = {}
        for person in team_members:
            level_counts[person.level] = level_counts.get(person.level, 0) + 1
        
        # Must have at least one manager
        if level_counts.get("Mgr", 0) == 0:
            errors.append("Team must have at least one manager")
        
        # Should have some senior engineers
        if level_counts.get("Sr", 0) == 0 and len(team_members) > 3:
            errors.append("Team should have at least one senior engineer")
        
        # Manager span of control
        manager_count = level_counts.get("Mgr", 0)
        non_manager_count = len(team_members) - manager_count
        
        if manager_count > 0:
            span_per_manager = non_manager_count / manager_count
            if span_per_manager > 8:
                errors.append(f"Manager span of control too high: {span_per_manager:.1f} (should be ≤8)")
            elif span_per_manager < 3:
                errors.append(f"Manager span of control too low: {span_per_manager:.1f} (should be ≥3)")
        
        return errors
