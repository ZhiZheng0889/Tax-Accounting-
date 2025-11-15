from typing import List

from study_base import StudyTopic


COMMUNICATION_TOPICS: List[StudyTopic] = [
    StudyTopic(
        id="technical_writing_fundamentals",
        title="Fundamentals of Technical Writing: Clarity and Readability",
        category="Communication and Writing",
        pdf_filename="handoutsfundamentalsoftechnicalwriting110420251761571939104.pdf",
        description=(
            "Covers the essentials of explaining complex ideas clearly: structuring "
            "documents, choosing precise language, using examples and visuals, and "
            "editing for clarity and readability. This is directly useful for memos, "
            "emails to clients, documentation, and training materials."
        ),
        focus_questions=[
            "What makes technical content clear rather than confusing (structure, word choice, assumptions about the reader)?",
            "How should you structure a technical explanation so that a busy reader can follow it quickly?",
            "Which editing steps (shortening sentences, replacing jargon, adding headings) improve readability the most?",
            "How can you use concrete examples or simple diagrams to make abstract concepts understandable?",
            "Pick one recent email or memo you wrote—how could you rewrite it using these principles?",
        ],
    ),
]

