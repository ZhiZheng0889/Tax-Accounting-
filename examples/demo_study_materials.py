"""Small demo script for the study materials.

Run from the project root:

    python examples/demo_study_materials.py
"""

import argparse
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS_DIR = ROOT / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from study_materials import STUDY_TOPICS  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Small demo of the study topic definitions."
    )
    parser.add_argument(
        "--category",
        action="append",
        help="Filter to one or more categories (can repeat).",
    )
    args = parser.parse_args()

    topics = STUDY_TOPICS
    if args.category:
        allowed = {c.lower() for c in args.category}
        topics = [t for t in topics if t.category.lower() in allowed]

    if not topics:
        print("No topics match the provided filters.")
        return

    print(f"Total topics: {len(topics)}\n")

    categories: dict[str, int] = {}
    for topic in topics:
        categories[topic.category] = categories.get(topic.category, 0) + 1

    print("Topics by category:")
    for name, count in sorted(categories.items()):
        print(f"- {name}: {count}")

    print("\nRandom topic to review:")
    topic = random.choice(topics)
    print(f"- [{topic.category}] {topic.title}")
    print(f"  PDF: {topic.pdf_filename}")
    print(f"  Difficulty: {topic.difficulty}")
    print(f"\nDescription:\n{topic.description}")


if __name__ == "__main__":
    main()
