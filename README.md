Tax & Accounting Notes

This workspace is organized for capturing and organizing your tax and accounting knowledge, especially Word documents from note‑taking.

Structure
- 01-Tax: Personal/business tax notes, planning, cases, summaries of IRS/state guidance.
- 02-Accounting: Bookkeeping, financial statements, GAAP/IFRS topics, workflows.
- 03-References: Authoritative references (IRS pubs, state regs), links, PDFs.
- 04-Templates: Note templates, checklists, workpaper formats for reuse.

Suggested conventions
- File names: YYYY-MM-DD Topic – Detail.docx (e.g., 2025-11-12 Depreciation – MACRS basis.docx)
- Keep “index” docs in each folder to summarize what’s inside (e.g., Index.docx).
- Drop working drafts in the right folder first; refine structure as content grows.

Notes
- You can rename or add subfolders anytime (e.g., 01-Tax/Personal, 01-Tax/Business).
- Consider storing key PDFs in 03-References and linking to them from your notes.

Payroll Calculator
- Location: `tools/payroll_calculator.py`
- Requirements: Python 3.9+

Quick examples
- Hourly: `python tools/payroll_calculator.py --pay-type hourly --hourly-rate 30 --hours 80 --ytd-wages 50000 --federal-rate 12% --state-rate 5%`
- Salary: `python tools/payroll_calculator.py --pay-type salary --salary 3500 --ytd-wages 120000 --federal-rate 0.18 --state-rate 6`

What it does
- Computes Social Security (6.2%) up to the annual wage base (by year), considering YTD wages.
- Computes Medicare (1.45%) and Additional Medicare (0.9%) above $200,000 YTD.
- Optionally withholds federal and state income tax at a flat percentage you provide.

Notes
- YTD wages matter for capping Social Security and triggering Additional Medicare.
- `--federal-rate` and `--state-rate` accept `0.12`, `12` or `12%` formats.
- This is a simplified calculator (flat FIT/SIT rates). For exact withholding, use current IRS/state tables and W‑4 details.
