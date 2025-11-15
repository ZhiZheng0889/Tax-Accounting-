from pathlib import Path

import pypdf


def dump_headings(pdf_dir: Path) -> None:
    files = sorted(pdf_dir.glob("*.pdf"))
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
            print("[Error reading PDF]", exc)
        print()


if __name__ == "__main__":
    dump_headings(Path("PDF"))
