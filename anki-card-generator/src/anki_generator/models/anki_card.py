"""AnkiCard model for Anki flashcards."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class AnkiCard:
    """Represents an Anki flashcard in the proper format.

    Attributes:
        front: The front side of the card (question).
        back: The back side of the card (answer).
        tags: List of tags for the card (e.g., ["aws_service:EC2", "section:Compute"]).
    """

    front: str
    back: str
    tags: list[str] = field(default_factory=list)

    def to_tsv_line(self) -> str:
        """Convert the card to a tab-separated line for Anki import.

        Returns:
            Tab-separated string: front\tback\ttags (space-separated).

        Example:
            >>> card = AnkiCard("Q?", "A", ["tag1", "tag2"])
            >>> card.to_tsv_line()
            'Q?\tA\ttag1 tag2'
        """
        tags_str = " ".join(self.tags) if self.tags else ""
        return f"{self.front}\t{self.back}\t{tags_str}"
