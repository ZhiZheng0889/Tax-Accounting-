import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS_DIR = ROOT / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from study_materials import STUDY_TOPICS, StudyTopic  # noqa: E402


def test_study_topics_non_empty() -> None:
    assert isinstance(STUDY_TOPICS, list)
    assert STUDY_TOPICS, "Expected at least one study topic"


def test_study_topic_fields_are_populated() -> None:
    topic = STUDY_TOPICS[0]
    assert isinstance(topic, StudyTopic)
    assert topic.id
    assert topic.title
    assert topic.category
    assert topic.pdf_filename.lower().endswith(".pdf")

