import json
import os
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from typing import Dict, Set

from study_materials import STUDY_TOPICS, StudyTopic


class StudyGuideApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Study Guide – Tax & Accounting Webinars")
        self.resizable(True, True)

        self._state_file = Path.home() / ".study_guide_progress.json"
        self._reviewed: Set[str] = set()
        self._notes: Dict[str, str] = {}

        self.selected_topic_id: str | None = None

        self._load_state()
        self._build_ui()

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=3)
        self.rowconfigure(0, weight=1)

        left = ttk.Frame(self)
        left.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        left.rowconfigure(1, weight=1)
        right = ttk.Frame(self)
        right.grid(row=0, column=1, sticky="nsew", padx=6, pady=6)
        right.rowconfigure(2, weight=1)
        right.columnconfigure(0, weight=1)

        ttk.Label(left, text="Topics").grid(row=0, column=0, sticky="w")

        tree = ttk.Treeview(left, show="tree", selectmode="browse", height=20)
        tree.grid(row=1, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(left, orient="vertical", command=tree.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        tree.configure(yscrollcommand=scrollbar.set)
        self.tree = tree

        categories: Dict[str, str] = {}
        for topic in STUDY_TOPICS:
            if topic.category not in categories:
                categories[topic.category] = tree.insert(
                    "", "end", text=topic.category, open=True
                )
            label = topic.title
            if topic.id in self._reviewed:
                label = f"✓ {label}"
            tree.insert(categories[topic.category], "end", iid=topic.id, text=label)

        tree.bind("<<TreeviewSelect>>", self._on_select_topic)

        info_frame = ttk.Frame(right)
        info_frame.grid(row=0, column=0, sticky="ew")
        info_frame.columnconfigure(1, weight=1)

        ttk.Label(info_frame, text="Title:").grid(row=0, column=0, sticky="ne", padx=4)
        self.lbl_title = ttk.Label(info_frame, text="", wraplength=500, justify="left")
        self.lbl_title.grid(row=0, column=1, sticky="w")

        ttk.Label(info_frame, text="Category:").grid(
            row=1, column=0, sticky="ne", padx=4
        )
        self.lbl_category = ttk.Label(info_frame, text="")
        self.lbl_category.grid(row=1, column=1, sticky="w")

        ttk.Label(info_frame, text="PDF file:").grid(
            row=2, column=0, sticky="ne", padx=4
        )
        self.lbl_pdf = ttk.Label(info_frame, text="")
        self.lbl_pdf.grid(row=2, column=1, sticky="w")

        desc_frame = ttk.LabelFrame(right, text="Description and Focus Questions")
        desc_frame.grid(row=1, column=0, sticky="nsew", pady=(8, 4))
        desc_frame.columnconfigure(0, weight=1)
        desc_frame.rowconfigure(0, weight=1)

        self.txt_desc = tk.Text(
            desc_frame, height=10, wrap="word", state="disabled", bg=self.cget("bg")
        )
        self.txt_desc.grid(row=0, column=0, sticky="nsew")
        desc_scroll = ttk.Scrollbar(
            desc_frame, orient="vertical", command=self.txt_desc.yview
        )
        desc_scroll.grid(row=0, column=1, sticky="ns")
        self.txt_desc.configure(yscrollcommand=desc_scroll.set)

        notes_frame = ttk.LabelFrame(right, text="Your Notes")
        notes_frame.grid(row=2, column=0, sticky="nsew", pady=(4, 0))
        notes_frame.columnconfigure(0, weight=1)
        notes_frame.rowconfigure(0, weight=1)

        self.txt_notes = tk.Text(notes_frame, wrap="word")
        self.txt_notes.grid(row=0, column=0, sticky="nsew")
        notes_scroll = ttk.Scrollbar(
            notes_frame, orient="vertical", command=self.txt_notes.yview
        )
        notes_scroll.grid(row=0, column=1, sticky="ns")
        self.txt_notes.configure(yscrollcommand=notes_scroll.set)

        btn_frame = ttk.Frame(right)
        btn_frame.grid(row=3, column=0, sticky="ew", pady=(4, 0))
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)
        btn_frame.columnconfigure(2, weight=1)

        self.btn_open = ttk.Button(
            btn_frame, text="Open PDF", command=self._open_selected_pdf
        )
        self.btn_open.grid(row=0, column=0, sticky="ew", padx=2)

        self.btn_mark_reviewed = ttk.Button(
            btn_frame, text="Mark Reviewed", command=self._toggle_reviewed
        )
        self.btn_mark_reviewed.grid(row=0, column=1, sticky="ew", padx=2)

        self.btn_save_notes = ttk.Button(
            btn_frame, text="Save Notes", command=self._save_current_notes
        )
        self.btn_save_notes.grid(row=0, column=2, sticky="ew", padx=2)

    def _load_state(self) -> None:
        if not self._state_file.exists():
            return
        try:
            data = json.loads(self._state_file.read_text(encoding="utf-8"))
        except Exception:
            return
        reviewed = data.get("reviewed_ids", [])
        notes = data.get("notes", {})
        self._reviewed = set(reviewed)
        self._notes = {k: str(v) for k, v in notes.items()}

    def _persist_state(self) -> None:
        data = {
            "reviewed_ids": sorted(self._reviewed),
            "notes": self._notes,
        }
        try:
            self._state_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception:
            messagebox.showwarning(
                "Save Error", "Could not save study progress to disk."
            )

    def _find_topic(self, topic_id: str) -> StudyTopic | None:
        for topic in STUDY_TOPICS:
            if topic.id == topic_id:
                return topic
        return None

    def _on_select_topic(self, event: object) -> None:
        selection = self.tree.selection()
        if not selection:
            return
        topic_id = selection[0]
        topic = self._find_topic(topic_id)
        if topic is None:
            return
        self.selected_topic_id = topic.id
        self._update_detail_view(topic)

    def _update_detail_view(self, topic: StudyTopic) -> None:
        self.lbl_title.config(text=topic.title)
        self.lbl_category.config(text=topic.category)
        self.lbl_pdf.config(text=topic.pdf_filename)

        desc_lines = [topic.description, ""]
        if topic.focus_questions:
            desc_lines.append("Focus questions:")
            for q in topic.focus_questions:
                desc_lines.append(f"• {q}")

        self.txt_desc.configure(state="normal")
        self.txt_desc.delete("1.0", tk.END)
        self.txt_desc.insert("1.0", "\n".join(desc_lines))
        self.txt_desc.configure(state="disabled")

        existing_notes = self._notes.get(topic.id, "")
        self.txt_notes.delete("1.0", tk.END)
        self.txt_notes.insert("1.0", existing_notes)

        if topic.id in self._reviewed:
            self.btn_mark_reviewed.config(text="Mark Unreviewed")
        else:
            self.btn_mark_reviewed.config(text="Mark Reviewed")

    def _open_selected_pdf(self) -> None:
        if not self.selected_topic_id:
            messagebox.showinfo("Open PDF", "Select a topic first.")
            return
        topic = self._find_topic(self.selected_topic_id)
        if topic is None:
            messagebox.showerror("Open PDF", "Selected topic not found.")
            return
        path = topic.pdf_path
        if not path.exists():
            messagebox.showerror(
                "Open PDF", f"PDF file not found:\n{path.resolve()}"
            )
            return
        try:
            if os.name == "nt":
                os.startfile(path)  # type: ignore[attr-defined]
            else:
                self._open_file_non_windows(path)
        except Exception as exc:
            messagebox.showerror("Open PDF", f"Could not open PDF:\n{exc}")

    def _open_file_non_windows(self, path: Path) -> None:
        import subprocess
        import sys

        if sys.platform == "darwin":
            subprocess.Popen(["open", str(path)])
        else:
            subprocess.Popen(["xdg-open", str(path)])

    def _toggle_reviewed(self) -> None:
        if not self.selected_topic_id:
            return
        topic = self._find_topic(self.selected_topic_id)
        if topic is None:
            return
        if topic.id in self._reviewed:
            self._reviewed.remove(topic.id)
            current = self.tree.item(topic.id, "text")
            if current.startswith("✓ "):
                self.tree.item(topic.id, text=current[2:])
            self.btn_mark_reviewed.config(text="Mark Reviewed")
        else:
            self._reviewed.add(topic.id)
            current = self.tree.item(topic.id, "text")
            if not current.startswith("✓ "):
                self.tree.item(topic.id, text=f"✓ {current}")
            self.btn_mark_reviewed.config(text="Mark Unreviewed")
        self._persist_state()

    def _save_current_notes(self) -> None:
        if not self.selected_topic_id:
            return
        content = self.txt_notes.get("1.0", tk.END).strip()
        if content:
            self._notes[self.selected_topic_id] = content
        elif self.selected_topic_id in self._notes:
            self._notes.pop(self.selected_topic_id, None)
        self._persist_state()
        messagebox.showinfo("Notes", "Notes saved.")


def main() -> None:
    app = StudyGuideApp()
    app.mainloop()


if __name__ == "__main__":
    main()

