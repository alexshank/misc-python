"""QAPair model for question-answer pairs."""

from dataclasses import dataclass


@dataclass(frozen=True)
class QAPair:
    """Represents a question-answer pair generated from content.

    Attributes:
        question: The question text.
        answer: The answer text.
        aws_service: The AWS service name (e.g., 'IAM', 'S3', 'EC2').
        source_markdown: The original markdown content used to generate this Q&A.
        section_header: The section header from the markdown (first ## line).
        source_file: The filename of the source section file.
    """

    question: str
    answer: str
    aws_service: str
    source_markdown: str
    section_header: str
    source_file: str
