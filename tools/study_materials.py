"""Aggregate study topics across all webinar categories.

This module pulls together all of the category-specific topic lists into a
single ``STUDY_TOPICS`` sequence that the GUI and other tooling can use.

It also provides a small helper CLI that can populate the top-level
note folders (``01-Tax``, ``02-Accounting``, ``03-References``, and
``04-Templates``) with Markdown note files and indexes based on the
defined study topics.
"""

from __future__ import annotations

from pathlib import Path
import re
import textwrap
from typing import Dict, List, Optional

from study_base import StudyTopic
from study_materials_accounting_analysis import ACCOUNTING_ANALYSIS_TOPICS
from study_materials_communication import COMMUNICATION_TOPICS
from study_materials_ethics import ETHICS_TOPICS
from study_materials_governmental import GOVERNMENTAL_TOPICS
from study_materials_individual_tax import INDIVIDUAL_TAX_TOPICS
from study_materials_technology import TECH_TOPICS


__all__ = ["StudyTopic", "STUDY_TOPICS", "populate_folders"]


STUDY_TOPICS: List[StudyTopic] = (
    TECH_TOPICS
    + GOVERNMENTAL_TOPICS
    + INDIVIDUAL_TAX_TOPICS
    + ACCOUNTING_ANALYSIS_TOPICS
    + COMMUNICATION_TOPICS
    + ETHICS_TOPICS
)


def _guess_root_dir(category: str) -> Path:
    """Map a topic category to a top-level folder.

    This is intentionally simple and heuristic-based so that new categories
    degrade gracefully into ``03-References`` if they do not clearly match.
    """

    cat = category.lower()
    if "tax" in cat or "ethic" in cat or "practice" in cat:
        return Path("01-Tax")
    if (
        "account" in cat
        or "analysis" in cat
        or "governmental" in cat
        or "technology" in cat
        or "productivity" in cat
        or "communication" in cat
        or "writing" in cat
    ):
        return Path("02-Accounting")
    return Path("03-References")


def _sanitize_filename(name: str) -> str:
    """Return a filesystem-safe filename stem for Windows/macOS/Linux."""

    # Replace characters that are invalid or awkward in filenames.
    cleaned = re.sub(r'[<>:\"/\\|?*]+', " ", name).strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    # Keep filenames a reasonable length.
    if len(cleaned) > 80:
        cleaned = cleaned[:80].rstrip()
    return cleaned or "topic"


def _note_path(project_root: Path, topic: StudyTopic) -> Path:
    """Return the target Markdown note path for a topic.

    Notes are stored under a top-level folder (01-Tax, 02-Accounting, or
    03-References) and then grouped by the topic's category to keep
    related webinars together.
    """

    root_dir = _guess_root_dir(topic.category)
    category_dir_name = _sanitize_filename(topic.category)
    target_dir = project_root / root_dir / category_dir_name
    target_dir.mkdir(parents=True, exist_ok=True)

    stem = _sanitize_filename(topic.title)
    filename = f"{stem}.md"
    return target_dir / filename


def generate_note_markdown(topic: StudyTopic) -> str:
    """Generate a Markdown note template for a topic."""

    lines: List[str] = []
    lines.append(f"# {topic.title}")
    lines.append("")
    lines.append(f"**Category:** {topic.category}")
    lines.append(f"**PDF:** {topic.pdf_path}")
    lines.append("")

    lines.append("## Description / context")
    lines.append("")
    wrapped_desc = textwrap.fill(topic.description, width=88)
    lines.append(wrapped_desc)
    lines.append("")

    if topic.focus_questions:
        lines.append("## Focus questions")
        lines.append("")
        for q in topic.focus_questions:
            lines.append(f"- {q}")
        lines.append("")

    lines.append("## Your summary")
    lines.append("")
    lines.append(
        "Summarize the main ideas, rules, examples, and any numbers or thresholds "
        "you want to remember, in your own words."
    )
    lines.append("")

    lines.append("## Key takeaways")
    lines.append("")
    lines.append("- ")
    lines.append("- ")
    lines.append("- ")
    lines.append("")

    lines.append("## Follow-up actions")
    lines.append("")
    lines.append("- ")

    return "\n".join(lines)


def _create_reference_index(project_root: Path, overwrite: bool) -> None:
    """Create or update a Markdown index of all study topics."""

    ref_dir = project_root / "03-References"
    ref_dir.mkdir(parents=True, exist_ok=True)
    index_path = ref_dir / "Study Webinars Index.md"

    if index_path.exists() and not overwrite:
        return

    by_category: Dict[str, List[StudyTopic]] = {}
    for topic in STUDY_TOPICS:
        by_category.setdefault(topic.category, []).append(topic)

    lines: List[str] = []
    lines.append("# Study webinars index")
    lines.append("")
    lines.append(
        "This index was generated from the Python study topic definitions. "
        "Each entry links the webinar handout PDF and the suggested notes file."
    )
    lines.append("")

    for category in sorted(by_category.keys()):
        lines.append(f"## {category}")
        lines.append("")
        for topic in sorted(by_category[category], key=lambda t: t.title.lower()):
            note_path = _note_path(project_root, topic)
            try:
                note_rel = note_path.relative_to(project_root)
            except ValueError:
                note_rel = note_path
            lines.append(
                f"- **{topic.title}** - PDF: `{topic.pdf_path}`; Notes: `{note_rel}`"
            )
        lines.append("")

    index_path.write_text("\n".join(lines), encoding="utf-8")


def _create_templates(project_root: Path, overwrite: bool) -> None:
    """Create a generic webinar notes template in 04-Templates."""

    tmpl_dir = project_root / "04-Templates"
    tmpl_dir.mkdir(parents=True, exist_ok=True)
    tmpl_path = tmpl_dir / "Webinar Notes Template.md"

    if tmpl_path.exists() and not overwrite:
        return

    content = """# Webinar Notes Template

**Title:**  
**Date:**  
**Category:**  
**Speaker:**  
**Source / PDF:**  

## Why this matters

Briefly note why this topic is important for your work or clients.

## Key concepts

- 
- 
- 

## Examples / cases

- 
- 

## Planning ideas or checklists

- 
- 

## Open questions

- 
- 
"""

    tmpl_path.write_text(content, encoding="utf-8")


def populate_folders(
    base_dir: Optional[Path] = None,
    *,
    overwrite: bool = False,
    dry_run: bool = False,
) -> None:
    """Populate the top-level note folders based on the study topics.

    This creates Markdown note files for each webinar topic and a simple
    index in ``03-References``. Existing files are left untouched unless
    ``overwrite=True`` is passed.
    """

    project_root = base_dir or Path(__file__).resolve().parents[1]

    for topic in STUDY_TOPICS:
        note_path = _note_path(project_root, topic)
        rel_path = note_path.relative_to(project_root)

        if note_path.exists() and not overwrite:
            print(f"Skipping existing note: {rel_path}")
            continue

        if dry_run:
            print(f"[DRY RUN] Would write {rel_path}")
            continue

        content = generate_note_markdown(topic)
        note_path.write_text(content, encoding="utf-8")
        print(f"Wrote {rel_path}")

    if not dry_run:
        _create_reference_index(project_root, overwrite=overwrite)
        _create_templates(project_root, overwrite=overwrite)


if __name__ == "__main__":
    # Simple CLI: run `python tools/study_materials.py` from the project root
    # to populate the note folders. Pass `--dry-run` to see what would be
    # created without writing any files.
    import argparse

    parser = argparse.ArgumentParser(
        description=(
            "Populate the 01-Tax/02-Accounting/03-References/04-Templates "
            "folders with Markdown note files derived from the study topics."
        )
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing generated Markdown files.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned actions without writing any files.",
    )
    args = parser.parse_args()

    populate_folders(overwrite=args.overwrite, dry_run=args.dry_run)
