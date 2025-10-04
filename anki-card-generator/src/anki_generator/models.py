"""Data models for Anki Card Generator."""

from dataclasses import dataclass


@dataclass(frozen=True)
class QAPair:
    """Represents a question-answer pair generated from content.

    Attributes:
        question: The question text.
        answer: The answer text.
    """

    question: str
    answer: str


@dataclass(frozen=True)
class AnkiCard:
    """Represents an Anki flashcard in the proper format.

    Attributes:
        front: The front side of the card (question).
        back: The back side of the card (answer).
    """

    front: str
    back: str
