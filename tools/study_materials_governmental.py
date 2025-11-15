from typing import List

from study_base import StudyTopic


GOVERNMENTAL_TOPICS: List[StudyTopic] = [
    StudyTopic(
        id="gov_accounting_101",
        title="Governmental Accounting 101",
        category="Governmental Accounting",
        pdf_filename="HANDOUTS Governmental Accounting 101 (10-07-2025).pdf",
        description=(
            "Foundational overview of how governments keep their books, with an "
            "emphasis on fund structures, the measurement focus and basis of "
            "accounting, and the unique reporting objectives of public-sector "
            "entities. Use this to build a mental map before diving into more "
            "advanced governmental topics."
        ),
        focus_questions=[
            "How does governmental accounting differ from commercial GAAP in terms of objectives and users of the information?",
            "What are the main types of governmental, proprietary, and fiduciary funds, and what is the purpose of each?",
            "Which financial statements are unique to governments (e.g., government-wide vs. fund statements)?",
            "How do measurement focus and basis of accounting differ between government-wide and fund-level reporting?",
            "Where in your own experience have you seen confusion between governmental and commercial accounting concepts?",
        ],
    ),
    StudyTopic(
        id="gov_accounting_auditing_update",
        title="Governmental Accounting and Auditing Update: Year-End Planning",
        category="Governmental Accounting",
        pdf_filename="HANDOUTS Governmental Accounting and Auditing (11-07-2025).pdf",
        description=(
            "A current snapshot of new and upcoming standards, hot disclosure "
            "areas, and practical considerations for year-end close and audit "
            "planning in the governmental environment. This is about translating "
            "technical changes into concrete year-end checklists and talking "
            "points with clients or management."
        ),
        focus_questions=[
            "Which recent or upcoming standards have the biggest impact on governmental financial statements?",
            "What are the key steps in an effective governmental year-end close (schedules, reconciliations, communication)?",
            "Which disclosures and audit areas are currently considered high risk, and why?",
            "How can you proactively communicate year-end issues to governing boards or audit committees?",
            "If you had to design a short year-end checklist for a small government, what would be on it?",
        ],
    ),
]

