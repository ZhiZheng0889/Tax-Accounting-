from typing import List

from study_base import StudyTopic


ACCOUNTING_ANALYSIS_TOPICS: List[StudyTopic] = [
    StudyTopic(
        id="accounting_for_managers",
        title="Accounting for Managers",
        category="Accounting and Analysis",
        pdf_filename="handoutsaccountingformanagers091720251757409796755.pdf",
        description=(
            "Introduces non-accountant managers to the language of accounting: "
            "how transactions become numbers, how those numbers flow into the "
            "income statement, balance sheet, and cash flow statement, and how "
            "to use this information to make better operational decisions."
        ),
        focus_questions=[
            "What do managers need to understand about the income statement to interpret performance (revenue quality, margins, trends)?",
            "How do accruals, deferrals, and estimates (like bad debts or depreciation) affect reported results and decision-making?",
            "Which simple ratios (margin, turnover, leverage) are most useful for non-financial managers, and how should they interpret them?",
            "How can managers link key performance indicators (KPIs) back to the underlying accounting data?",
            "Think of a recent decision you or a manager made—how could better use of financial statements have improved that decision?",
        ],
    ),
    StudyTopic(
        id="analyzing_financial_statements",
        title="How to Analyze Financial Statements",
        category="Accounting and Analysis",
        pdf_filename="handoutshowtoanalyzefinancialstatements091220251755276924865.pdf",
        description=(
            "Provides a toolkit for reading the balance sheet, income statement, "
            "and cash flow statement together, using horizontal and vertical "
            "analysis plus key ratios to understand performance, risk, and cash "
            "generation over time."
        ),
        focus_questions=[
            "How do profitability, liquidity, activity, and leverage ratios work together to give a full picture of a business?",
            "What can you learn from the cash flow statement that the income statement does not show (quality of earnings, cash sufficiency)?",
            "Which trends in financial statements signal increasing risk (e.g., leverage, declining margins, deteriorating liquidity)?",
            "How would you approach analyzing a new company you have never seen before using these statements?",
            "Choose one ratio you find confusing and write out, in words, what it tells you about a business.",
        ],
    ),
]

