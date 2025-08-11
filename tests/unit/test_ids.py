"""Unit tests for ID generation utilities."""

import pytest

from src.okg.ids import IDGenerator


class TestIDGenerator:
    """Test ID generation functionality."""

    def test_deterministic_generation(self) -> None:
        """Test that ID generation is deterministic with same seed."""
        gen1 = IDGenerator(seed=42)
        gen2 = IDGenerator(seed=42)
        
        # Generate some IDs
        ids1 = [gen1.person_id() for _ in range(5)]
        ids2 = [gen2.person_id() for _ in range(5)]
        
        assert ids1 == ids2

    def test_person_id_format(self) -> None:
        """Test person ID format."""
        gen = IDGenerator()
        person_id = gen.person_id()
        
        assert person_id.startswith("PER-")
        assert len(person_id) == 8  # PER- + 4 digits
        assert person_id[4:].isdigit()

    def test_team_id_format(self) -> None:
        """Test team ID format."""
        gen = IDGenerator()
        team_id = gen.team_id("Payments Core")
        
        assert team_id == "TEAM-PAY"

    def test_project_id_format(self) -> None:
        """Test project ID format."""
        gen = IDGenerator()
        project_id = gen.project_id("PAY")
        
        assert project_id == "PROJ-PAY"

    def test_epic_id_format(self) -> None:
        """Test epic ID format."""
        gen = IDGenerator()
        epic_id = gen.epic_id("PAY")
        
        assert epic_id == "EPIC-PAY-01"
        
        # Second epic should increment
        epic_id2 = gen.epic_id("PAY")
        assert epic_id2 == "EPIC-PAY-02"

    def test_ticket_id_format(self) -> None:
        """Test ticket ID format."""
        gen = IDGenerator()
        ticket_id = gen.ticket_id("PAY")
        
        assert ticket_id.startswith("PAY-")
        assert ticket_id.split("-")[1].isdigit()
        assert int(ticket_id.split("-")[1]) >= 1400  # Realistic starting number

    def test_thread_id_format(self) -> None:
        """Test thread ID format."""
        gen = IDGenerator()
        thread_id = gen.thread_id()
        
        assert thread_id.startswith("MAIL-TH-")
        assert len(thread_id) == 12  # MAIL-TH- + 3 digits

    def test_message_id_format(self) -> None:
        """Test message ID format."""
        gen = IDGenerator()
        msg_id = gen.message_id()
        
        assert msg_id.startswith("MSG-")
        assert len(msg_id) == 7  # MSG- + 3 digits

    def test_counter_independence(self) -> None:
        """Test that different ID types have independent counters."""
        gen = IDGenerator()
        
        # Generate some IDs
        person1 = gen.person_id()
        ticket1 = gen.ticket_id("PAY")
        person2 = gen.person_id()
        ticket2 = gen.ticket_id("PAY")
        
        assert person1 == "PER-0001"
        assert person2 == "PER-0002"
        assert ticket1 == "PAY-1401"
        assert ticket2 == "PAY-1402"

    def test_reset_counters(self) -> None:
        """Test counter reset functionality."""
        gen = IDGenerator()
        
        # Generate some IDs
        gen.person_id()
        gen.ticket_id("PAY")
        
        # Reset and verify counters start over
        gen.reset_counters()
        
        assert gen.person_id() == "PER-0001"
        assert gen.ticket_id("PAY") == "PAY-1401"

    def test_deterministic_hash(self) -> None:
        """Test deterministic hash generation."""
        gen = IDGenerator(seed=42)
        
        data = {"test": "data", "number": 123}
        hash1 = gen.deterministic_hash(data)
        hash2 = gen.deterministic_hash(data)
        
        assert hash1 == hash2
        assert len(hash1) == 8
        
        # Different data should produce different hash
        different_data = {"test": "different", "number": 456}
        hash3 = gen.deterministic_hash(different_data)
        assert hash1 != hash3
