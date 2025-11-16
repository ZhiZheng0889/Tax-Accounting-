"""Shared data structures for the study guide tools."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List


PDF_DIR = Path("PDF")


@dataclass(frozen=True)
class StudyTopic:
    """A single webinar or study resource.

    Attributes:
        id: Stable identifier used for persistence and lookups.
        title: Human-readable title of the topic.
        category: High-level grouping such as ``Individual Taxation``.
        pdf_filename: Name of the PDF file in the ``PDF`` directory.
        description: Short narrative description of what the topic covers.
        focus_questions: Prompts to guide active review of the material.
        difficulty: Rough difficulty rating on a small integer scale.
    """

    id: str
    title: str
    category: str
    pdf_filename: str
    description: str
    focus_questions: List[str]
    difficulty: int = field(default=1)

    @property
    def pdf_path(self) -> Path:
        """Return the full path to this topic's PDF file."""

        return PDF_DIR / self.pdf_filename
