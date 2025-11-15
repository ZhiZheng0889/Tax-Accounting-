import json
import os
import random
import tkinter as tk
from datetime import date
from pathlib import Path
from typing import Dict, Set

from tkinter import ttk, messagebox

from study_materials import STUDY_TOPICS, StudyTopic


class StudyGuideApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Study Guide - Tax & Accounting Webinars")
        self.resizable(True, True)

        self._state_file = Path.home() / ".study_guide_progress.json"
        self._reviewed: Set[str] = set()
        self._notes: Dict[str, str] = {}
        self._points: int = 0
        self._streak: int = 0
        self._last_study_date: str | None = None
        self._daily_challenge_id: str | None = None
        self._daily_challenge_date: str | None = None
        self._current_level_name: str = ""

        self.selected_topic_id: str | None = None

        self._load_state()
        self._ensure_daily_challenge()
        self._build_ui()
        self._bind_shortcuts()

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=3)
        self.rowconfigure(0, weight=1)

        left = ttk.Frame(self)
        left.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        left.rowconfigure(1, weight=1)

        right = ttk.Frame(self)
        right.grid(row=0, column=1, sticky="nsew", padx=6, pady=6)
        right.rowconfigure(0, weight=0)
        right.rowconfigure(1, weight=0)
        right.rowconfigure(2, weight=1)
        right.rowconfigure(3, weight=1)
        right.rowconfigure(4, weight=0)
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
                label = f"* {label}"
            tree.insert(categories[topic.category], "end", iid=topic.id, text=label)

        tree.bind("<<TreeviewSelect>>", self._on_select_topic)

        stats_frame = ttk.Frame(right)
        stats_frame.grid(row=0, column=0, sticky="ew")
        stats_frame.columnconfigure(0, weight=1)
        stats_frame.columnconfigure(1, weight=1)
        stats_frame.columnconfigure(2, weight=1)

        self.lbl_score = ttk.Label(stats_frame, text="Score: 0")
        self.lbl_score.grid(row=0, column=0, sticky="w")

        self.lbl_streak = ttk.Label(stats_frame, text="Streak: 0 days")
        self.lbl_streak.grid(row=0, column=1, sticky="w")

        self.lbl_progress = ttk.Label(stats_frame, text="Progress: 0/0")
        self.lbl_progress.grid(row=0, column=2, sticky="e")

        self.progress_bar = ttk.Progressbar(
            stats_frame, orient="horizontal", mode="determinate"
        )
        self.progress_bar.grid(
            row=1, column=0, columnspan=3, sticky="ew", pady=(2, 0)
        )

        self.lbl_level = ttk.Label(stats_frame, text="Level: Beginner")
        self.lbl_level.grid(row=2, column=0, sticky="w")

        self.lbl_badge = ttk.Label(stats_frame, text="Badge: None yet")
        self.lbl_badge.grid(row=2, column=1, columnspan=2, sticky="w")

        self.lbl_daily = ttk.Label(stats_frame, text="Daily challenge: (not set)")
        self.lbl_daily.grid(row=3, column=0, columnspan=2, sticky="w", pady=(2, 0))

        self.btn_daily = ttk.Button(
            stats_frame, text="Go", width=6, command=self._jump_to_daily_challenge
        )
        self.btn_daily.grid(row=3, column=2, sticky="e", padx=(4, 0), pady=(2, 0))

        self.lbl_message = ttk.Label(stats_frame, text="")
        self.lbl_message.grid(row=4, column=0, columnspan=3, sticky="w")

        info_frame = ttk.Frame(right)
        info_frame.grid(row=1, column=0, sticky="ew")
        info_frame.columnconfigure(1, weight=1)

        ttk.Label(info_frame, text="Title:").grid(
            row=0, column=0, sticky="ne", padx=4
        )
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
        desc_frame.grid(row=2, column=0, sticky="nsew", pady=(8, 4))
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
        notes_frame.grid(row=3, column=0, sticky="nsew", pady=(4, 0))
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
        btn_frame.grid(row=4, column=0, sticky="ew", pady=(4, 0))
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

        self.btn_random = ttk.Button(
            btn_frame, text="Random Topic", command=self._jump_to_random_topic
        )
        self.btn_random.grid(row=1, column=0, sticky="ew", padx=2, pady=(2, 0))

        self.btn_next_unreviewed = ttk.Button(
            btn_frame,
            text="Next Unreviewed",
            command=self._jump_to_next_unreviewed,
        )
        self.btn_next_unreviewed.grid(row=1, column=1, sticky="ew", padx=2, pady=(2, 0))

        self.btn_quiz = ttk.Button(
            btn_frame, text="Quiz Me", command=self._quiz_on_current_topic
        )
        self.btn_quiz.grid(row=1, column=2, sticky="ew", padx=2, pady=(2, 0))

        self.btn_export_notes = ttk.Button(
            btn_frame, text="Export Notes", command=self._export_all_notes
        )
        self.btn_export_notes.grid(row=2, column=0, columnspan=3, sticky="ew", padx=2, pady=(4, 0))

        self._update_stats_labels()

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
        self._points = int(data.get("points", 0) or 0)
        self._streak = int(data.get("streak", 0) or 0)
        self._last_study_date = data.get("last_study_date")
        self._daily_challenge_id = data.get("daily_challenge_id")
        self._daily_challenge_date = data.get("daily_challenge_date")

    def _persist_state(self) -> None:
        data = {
            "reviewed_ids": sorted(self._reviewed),
            "notes": self._notes,
            "points": self._points,
            "streak": self._streak,
            "last_study_date": self._last_study_date,
            "daily_challenge_id": self._daily_challenge_id,
            "daily_challenge_date": self._daily_challenge_date,
        }
        try:
            self._state_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception:
            messagebox.showwarning(
                "Save Error", "Could not save study progress to disk."
            )

    def _ensure_daily_challenge(self) -> None:
        if not STUDY_TOPICS:
            self._daily_challenge_id = None
            self._daily_challenge_date = None
            return
        today = date.today().isoformat()
        if self._daily_challenge_date == today and self._daily_challenge_id:
            return
        topic = random.choice(STUDY_TOPICS)
        self._daily_challenge_id = topic.id
        self._daily_challenge_date = today
        self._persist_state()

    def _set_message(self, text: str) -> None:
        self.lbl_message.config(text=text)

    def _compute_level(self) -> str:
        if self._points >= 300:
            return "Master"
        if self._points >= 150:
            return "Pro"
        if self._points >= 50:
            return "Learner"
        return "Beginner"

    def _compute_badge(self) -> str:
        total = len(STUDY_TOPICS)
        reviewed = len(self._reviewed)
        if total and reviewed == total:
            return "Completed All Topics"
        if self._streak >= 14:
            return "Two-Week Streak"
        if self._streak >= 7:
            return "Streak Champion"
        if self._points >= 100:
            return "Century Scorer"
        return "None yet"

    def _update_stats_labels(self) -> None:
        total = len(STUDY_TOPICS)
        reviewed = len(self._reviewed)
        self.lbl_score.config(text=f"Score: {self._points}")
        if self._streak <= 0:
            streak_text = "Streak: 0 days"
        elif self._streak == 1:
            streak_text = "Streak: 1 day"
        else:
            streak_text = f"Streak: {self._streak} days"
        self.lbl_streak.config(text=streak_text)
        self.lbl_progress.config(text=f"Progress: {reviewed}/{total}")

        self.progress_bar["maximum"] = max(total, 1)
        self.progress_bar["value"] = reviewed

        level = self._compute_level()
        self.lbl_level.config(text=f"Level: {level}")
        self._current_level_name = level

        badge = self._compute_badge()
        self.lbl_badge.config(text=f"Badge: {badge}")

        daily_topic = self._get_daily_challenge_topic()
        if daily_topic is None:
            self.lbl_daily.config(text="Daily challenge: (not set)")
        else:
            self.lbl_daily.config(
                text=f"Daily challenge: {daily_topic.title}"
            )

    def _record_study_event(self, points: int = 0) -> None:
        today = date.today()
        today_str = today.isoformat()

        old_streak = self._streak
        old_level = self._compute_level()

        if self._last_study_date is None:
            self._streak = 1
        else:
            try:
                last = date.fromisoformat(self._last_study_date)
                delta = (today - last).days
                if delta == 0:
                    pass
                elif delta == 1:
                    self._streak += 1
                else:
                    self._streak = 1
            except ValueError:
                self._streak = 1
        self._last_study_date = today_str
        if points > 0:
            self._points += points

        self._update_stats_labels()

        new_level = self._compute_level()
        messages: list[str] = []
        if points > 0:
            messages.append(f"+{points} points earned.")
        if self._streak > old_streak:
            if self._streak == 1:
                messages.append("New study streak started.")
            elif self._streak >= 5:
                messages.append("Streak on fire!")
            else:
                messages.append("Streak extended.")
        if new_level != old_level:
            messages.append(f"Level up! You are now {new_level}.")
        if messages:
            self._set_message(" ".join(messages))

        self._persist_state()

    def _get_daily_challenge_topic(self) -> StudyTopic | None:
        if not self._daily_challenge_id:
            return None
        return self._find_topic(self._daily_challenge_id)

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
                desc_lines.append(f"- {q}")

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

    def _bind_shortcuts(self) -> None:
        self.bind("<Control-r>", lambda _event: self._toggle_reviewed())
        self.bind("<Control-n>", lambda _event: self._jump_to_next_unreviewed())
        self.bind("<Control-q>", lambda _event: self._quiz_on_current_topic())
        self.bind("<Control-e>", lambda _event: self._export_all_notes())
        self.bind("<Control-l>", lambda _event: self._jump_to_random_topic())

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
            if current.startswith("* "):
                self.tree.item(topic.id, text=current[2:])
            self.btn_mark_reviewed.config(text="Mark Reviewed")
            self._persist_state()
            self._update_stats_labels()
        else:
            self._reviewed.add(topic.id)
            current = self.tree.item(topic.id, "text")
            if not current.startswith("* "):
                self.tree.item(topic.id, text=f"* {current}")
            self.btn_mark_reviewed.config(text="Mark Unreviewed")
            self._record_study_event(points=10)

    def _save_current_notes(self) -> None:
        if not self.selected_topic_id:
            return
        content = self.txt_notes.get("1.0", tk.END).strip()
        if content:
            self._notes[self.selected_topic_id] = content
            self._record_study_event(points=3)
        else:
            if self.selected_topic_id in self._notes:
                self._notes.pop(self.selected_topic_id, None)
            self._persist_state()
            self._update_stats_labels()
        messagebox.showinfo("Notes", "Notes saved.")

    def _export_all_notes(self) -> None:
        if not self._notes:
            messagebox.showinfo("Export Notes", "You have no notes to export yet.")
            return
        output_path = Path.home() / "study_guide_notes.md"
        lines: list[str] = []
        for topic in STUDY_TOPICS:
            notes = self._notes.get(topic.id, "").strip()
            if not notes:
                continue
            lines.append(f"# {topic.title}")
            lines.append(f"*Category:* {topic.category}")
            lines.append(f"*PDF:* {topic.pdf_filename}")
            lines.append("")
            lines.append(notes)
            lines.append("")
        try:
            output_path.write_text("\n".join(lines), encoding="utf-8")
        except Exception as exc:
            messagebox.showerror(
                "Export Notes", f"Could not export notes:\n{exc}"
            )
            return
        self._record_study_event(points=5)
        messagebox.showinfo(
            "Export Notes",
            f"Notes exported to:\n{output_path}",
        )

    def _jump_to_random_topic(self) -> None:
        if not STUDY_TOPICS:
            return
        topic = random.choice(STUDY_TOPICS)
        self.selected_topic_id = topic.id
        self.tree.selection_set(topic.id)
        self.tree.see(topic.id)
        self._update_detail_view(topic)

    def _jump_to_next_unreviewed(self) -> None:
        if not STUDY_TOPICS:
            return
        unreviewed = [t for t in STUDY_TOPICS if t.id not in self._reviewed]
        if not unreviewed:
            messagebox.showinfo("Next Unreviewed", "All topics are marked reviewed.")
            return
        topic = unreviewed[0]
        self.selected_topic_id = topic.id
        self.tree.selection_set(topic.id)
        self.tree.see(topic.id)
        self._update_detail_view(topic)

    def _quiz_on_current_topic(self) -> None:
        if not self.selected_topic_id:
            messagebox.showinfo("Quiz Me", "Select a topic first.")
            return
        topic = self._find_topic(self.selected_topic_id)
        if topic is None or not topic.focus_questions:
            messagebox.showinfo(
                "Quiz Me",
                "No focus questions are defined for this topic.",
            )
            return
        question = random.choice(topic.focus_questions)
        messagebox.showinfo(
            "Quiz Me",
            f"Take 1-2 minutes to answer this question out loud or in your notes:\n\n{question}",
        )
        self._record_study_event(points=2)

    def _jump_to_daily_challenge(self) -> None:
        topic = self._get_daily_challenge_topic()
        if topic is None:
            messagebox.showinfo(
                "Daily Challenge", "No daily challenge is set for today."
            )
            return
        self.selected_topic_id = topic.id
        self.tree.selection_set(topic.id)
        self.tree.see(topic.id)
        self._update_detail_view(topic)


def main() -> None:
    app = StudyGuideApp()
    app.mainloop()


if __name__ == "__main__":
    main()
