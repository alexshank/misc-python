"""QAPair model for question-answer pairs."""

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
