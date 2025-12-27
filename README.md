Tax & Accounting Notes

This workspace is organized for capturing and organizing your tax and accounting knowledge, especially Word documents from note-taking and webinar handouts.

Structure
- `01-Tax`: Personal/business tax notes, planning, cases, summaries of IRS/state guidance.
- `02-Accounting`: Bookkeeping, financial statements, GAAP/IFRS topics, workflows.
- `03-References`: Authoritative references (IRS pubs, state regs), links, PDFs.
- `04-Templates`: Note templates, checklists, workpaper formats for reuse.

Suggested conventions
- File names: `YYYY-MM-DD Topic - Detail.docx` (e.g., `2025-11-12 Depreciation - MACRS basis.docx`).
- Keep short "index" docs in each folder to summarize what is inside (e.g., `Index.docx`).
- Drop working drafts in the right folder first; refine structure as content grows.

Notes
- You can rename or add subfolders anytime (e.g., `01-Tax/Personal`, `01-Tax/Business`).
- Consider storing key PDFs in `03-References` or `PDF` and linking to them from your notes.

Python tools
============

Full-stack (Angular + .NET)
===========================

This repo now includes a minimal full-stack sample to match common entry-level requirements (Angular SPA + C#/.NET Web API + unit/integration tests + CI).

- Backend: `backend/TaxAccounting.Api` (ASP.NET Core, .NET 8)
- Frontend: `frontend` (Angular)

Local run (2 terminals)
-----------------------

Backend:

```bash
dotnet run --project backend/TaxAccounting.Api
```

Frontend:

```bash
cd frontend
npm install
npm start
```

The Angular dev server proxies `/api/*` to `http://localhost:5206` via `frontend/proxy.conf.json`.

Notes
-----

- If you just installed the .NET SDK on Windows, you may need to restart your terminal/VS Code so `dotnet` is available on PATH.
- Node LTS is recommended for real projects (odd-numbered Node releases are not LTS).

Requirements
- Python 3.10+
- Dependencies in `requirements.txt` (currently just `pypdf` for PDF helpers).

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Payroll calculator (CLI)
------------------------

- Location: `tools/payroll_calculator.py`

Quick examples
- Hourly with overtime (flat FIT):
  `python tools/payroll_calculator.py --pay-type hourly --hourly-rate 30 --hours 40 --overtime-hours 5 --ytd-wages 50000 --withholding-method flat --federal-rate 12% --state-rate 5%`
- Hourly with daily-hours + CA daily OT:
  `python tools/payroll_calculator.py --pay-type hourly --hourly-rate 25 --daily-hours 8,9.5,10,7,12 --use-ca-daily-ot --ytd-wages 20000 --withholding-method flat --federal-rate 10%`
- Hourly with IRS percentage method and pre-tax:
  `python tools/payroll_calculator.py --pay-type hourly --hourly-rate 35 --hours 80 --withholding-method irs_percentage --filing-status married --pay-periods 26 --w4-step3 4000 --pretax-401k 200 --pretax-section125 150`
- Salary:
  `python tools/payroll_calculator.py --pay-type salary --salary 3500 --ytd-wages 120000 --withholding-method irs_percentage --filing-status single --pay-periods 24`

CLI output options
- `--json` prints JSON instead of text.
- `--explain` prints a step-by-step breakdown (with math and brackets).
- `--output-csv PATH` writes a one-line CSV of results.

What it does
- Computes Social Security (6.2%) up to the annual wage base (by year), considering YTD wages.
- Computes Medicare (1.45%) and Additional Medicare (0.9%) above $200,000 YTD.
- Optionally withholds federal and state income tax at a flat percentage you provide.
- For hourly pay, includes overtime by multiplying `overtime_hours` by the specified `overtime_multiplier` (default 1.5x).
- Optional double-time and daily-hours parsing (CA daily OT mode available).
- Pre-tax deductions: 401(k) reduces FIT; HSA and Section 125 reduce FIT and FICA.
- Employer cost view: shows employer Social Security and Medicare.
- IRS percentage-method withholding (approximate) with W-4 inputs for planning.

Notes
- YTD wages matter for capping Social Security and triggering Additional Medicare.
- `--federal-rate` and `--state-rate` accept `0.12`, `12` or `12%` formats.
- This is a simplified calculator (flat FIT/SIT rates). For exact withholding, use current IRS/state tables and W-4 details.
- The IRS percentage-method implementation here is a planning approximation using 2025 brackets and standard deductions; results may differ from exact Pub 15-T tables.

Overtime basics (U.S. FLSA)
- Most non-exempt employees earn overtime at 1.5x for hours over 40 in a workweek.
- Some states (e.g., California) impose daily overtime or double-time; this tool does not automatically apply those. Enter such hours as `--overtime-hours` with an appropriate `--overtime-multiplier` (e.g., 2.0 for double-time).

Overtime examples
- $20/hr, 45 hours in the week: Gross = 40 * $20 + 5 * $20 * 1.5 = $950.
- $30/hr, 50 hours: Gross = 40 * $30 + 10 * $30 * 1.5 = $1,650.

Study materials (CLI)
---------------------

Generate Markdown note shells from the topic definitions in `tools/study_materials.py`.

- Dry run to see what would be written: `python tools/study_materials.py --dry-run`
- Generate notes and the index under 01-Tax/02-Accounting/03-References: `python tools/study_materials.py`
- Overwrite previously generated files: `python tools/study_materials.py --overwrite`

Study guide (GUI)
-----------------

The study guide helps you track progress across webinar handouts stored in the `PDF` folder.

- Location: `tools/study_guide_gui.py`
- Launch from the project root:
  `python tools/study_guide_gui.py`

Features
- Categorized tree of topics (tax, accounting, technology, ethics, communication).
- One-click "Open PDF" for the selected topic (uses your OS default PDF viewer).
- Notes panel with per-topic notes saved to `~/.study_guide_progress.json`.
- Gamified score, streak counter, levels, and badges.
- Daily challenge topic and "Quiz Me" button using focus questions.
- "Export Notes" to `~/study_guide_notes.md` for review.

PDF helper
----------

`tools/_dump_pdf_headings.py` can scan PDFs and print headings or first-page text:

```bash
python tools/_dump_pdf_headings.py
```

This is useful for quickly seeing what a handout covers before creating notes or topics.

Testing
-------

Run the small test suite with:

```bash
python -m pytest
```

