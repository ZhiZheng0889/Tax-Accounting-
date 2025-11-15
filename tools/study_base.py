from dataclasses import dataclass
from pathlib import Path
from typing import List


PDF_DIR = Path("PDF")


@dataclass(frozen=True)
class StudyTopic:
    id: str
    title: str
    category: str
    pdf_filename: str
    description: str
    focus_questions: List[str]

    @property
    def pdf_path(self) -> Path:
        return PDF_DIR / self.pdf_filename

