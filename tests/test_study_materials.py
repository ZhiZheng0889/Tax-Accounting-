import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS_DIR = ROOT / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from study_materials import STUDY_TOPICS, StudyTopic  # noqa: E402
from study_materials import _filter_topics  # type: ignore  # noqa: E402


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


def test_filter_topics_by_category() -> None:
    topics = _filter_topics(["Technology and Productivity"])
    assert topics, "Expected at least one technology topic"
    assert all(t.category == "Technology and Productivity" for t in topics)


def test_filter_topics_unknown_category_empty() -> None:
    assert _filter_topics(["not-a-real-category"]) == []
