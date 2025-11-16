"""Small demo script for the study materials.

Run from the project root:

    python examples/demo_study_materials.py
"""

import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS_DIR = ROOT / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from study_materials import STUDY_TOPICS  # noqa: E402


def main() -> None:
    print(f"Total topics: {len(STUDY_TOPICS)}\n")

    categories: dict[str, int] = {}
    for topic in STUDY_TOPICS:
        categories[topic.category] = categories.get(topic.category, 0) + 1

    print("Topics by category:")
    for name, count in sorted(categories.items()):
        print(f"- {name}: {count}")

    print("\nRandom topic to review:")
    topic = random.choice(STUDY_TOPICS)
    print(f"- [{topic.category}] {topic.title}")
    print(f"  PDF: {topic.pdf_filename}")
    print(f"  Difficulty: {topic.difficulty}")
    print(f"\nDescription:\n{topic.description}")


if __name__ == "__main__":
    main()

