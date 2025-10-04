"""Tests for data models."""

import pytest

from anki_generator.models import AnkiCard, QAPair


class TestQAPair:
    """Tests for QAPair dataclass."""

    def test_creation(self) -> None:
        """Test creating a QAPair instance."""
        qa_pair = QAPair(question="What is Python?", answer="A programming language")

        assert qa_pair.question == "What is Python?"
        assert qa_pair.answer == "A programming language"

    def test_immutable(self) -> None:
        """Test that QAPair instances are immutable."""
        qa_pair = QAPair(question="Q", answer="A")

        with pytest.raises(AttributeError):
            qa_pair.question = "New Q"  # type: ignore[misc]

    def test_equality(self) -> None:
        """Test QAPair equality comparison."""
        qa1 = QAPair(question="Q", answer="A")
        qa2 = QAPair(question="Q", answer="A")
        qa3 = QAPair(question="Q", answer="B")

        assert qa1 == qa2
        assert qa1 != qa3


class TestAnkiCard:
    """Tests for AnkiCard dataclass."""

    def test_creation(self) -> None:
        """Test creating an AnkiCard instance."""
        card = AnkiCard(front="What is Python?", back="A programming language")

        assert card.front == "What is Python?"
        assert card.back == "A programming language"

    def test_immutable(self) -> None:
        """Test that AnkiCard instances are immutable."""
        card = AnkiCard(front="Q", back="A")

        with pytest.raises(AttributeError):
            card.front = "New Q"  # type: ignore[misc]

    def test_equality(self) -> None:
        """Test AnkiCard equality comparison."""
        card1 = AnkiCard(front="Q", back="A")
        card2 = AnkiCard(front="Q", back="A")
        card3 = AnkiCard(front="Q", back="B")

        assert card1 == card2
        assert card1 != card3
