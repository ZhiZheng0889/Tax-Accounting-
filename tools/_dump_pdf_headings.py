"""Utility for quickly inspecting PDF bookmark outlines or first-page headings."""

import argparse
import logging
from pathlib import Path

import pypdf


logger = logging.getLogger(__name__)


def dump_headings(pdf_dir: Path) -> None:
    """Print outlines or inferred headings for all PDFs in ``pdf_dir``."""

    files = sorted(pdf_dir.glob("*.pdf"))
    if not files:
        logger.info("No PDF files found in %s", pdf_dir)
        return

    for path in files:
        print(f"--- FILE: {path.name} ---")
        try:
            reader = pypdf.PdfReader(str(path))
            outline = getattr(reader, "outline", None) or getattr(
                reader, "outlines", None
            )
            if outline:
                from pypdf.generic import Destination

                def walk(items, indent: int = 0) -> None:
                    for item in items:
                        if isinstance(item, list):
                            walk(item, indent + 2)
                        else:
                            title = getattr(item, "title", None)
                            if not title and isinstance(item, dict):
                                title = item.get("/Title")
                            if title:
                                print(" " * indent + f"- {title}")

                print("Outline/bookmarks:")
                walk(outline)
            else:
                if reader.pages:
                    txt = reader.pages[0].extract_text() or ""
                    lines = [line.strip() for line in txt.splitlines() if line.strip()]
                    print("Inferred headings (first lines):")
                    for line in lines[:20]:
                        print(f"- {line}")
                else:
                    print("[No pages found]")
        except Exception as exc:
            logger.exception("Error reading PDF %s", path)
            print("[Error reading PDF]", exc)
        print()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    parser = argparse.ArgumentParser(
        description="Print outlines or first lines for PDFs in a directory."
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default="PDF",
        help="Folder to scan for PDF files (default: PDF).",
    )
    args = parser.parse_args()

    dump_headings(Path(args.directory))
