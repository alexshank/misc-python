"""AnkiCard model for Anki flashcards."""

from dataclasses import dataclass


@dataclass(frozen=True)
class AnkiCard:
    """Represents an Anki flashcard in the proper format.

    Attributes:
        front: The front side of the card (question).
        back: The back side of the card (answer).
    """

    front: str
    back: str
