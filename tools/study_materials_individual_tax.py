from typing import List

from study_base import StudyTopic


INDIVIDUAL_TAX_TOPICS: List[StudyTopic] = [
    StudyTopic(
        id="tax_updates_individuals_2025",
        title="2025 Tax Updates for Individuals",
        category="Individual Taxation",
        pdf_filename="handouts2025taxupdatesforindividuals111420251762457167904.pdf",
        description=(
            "Walks through the latest federal individual tax changes for 2025, "
            "including new brackets, inflation adjustments, credits, deductions, "
            "and planning opportunities or pitfalls. Focus on how these changes "
            "affect different types of clients, such as wage earners, retirees, "
            "investors, and small business owners."
        ),
        focus_questions=[
            "Which 2025 changes most affect middle-income taxpayers versus higher-income taxpayers?",
            "How did standard deductions, child-related credits, and common above-the-line deductions change?",
            "Which planning strategies help clients respond (timing of income and deductions, retirement contributions, charitable giving)?",
            "What new or expanded tax traps should you warn clients about (phaseouts, surtaxes, limitations)?",
            "How would you summarize the key 2025 changes in one page for a non-technical client?",
        ],
        difficulty=2,
    ),
    StudyTopic(
        id="post_death_ira_transactions",
        title="Post Death IRA Transactions",
        category="Individual Taxation",
        pdf_filename="handoutspostdeathiratransactions102720251760472451493.pdf",
        description=(
            "Explores the rules for inherited IRAs after the account owner's "
            "death, including beneficiary categories, distribution requirements, "
            "timing rules, and planning options. Pay attention to how the rules "
            "differ for spouses versus non-spouses and how recent law changes "
            "alter common strategies."
        ),
        focus_questions=[
            "How do distribution rules differ for spouse, eligible designated, and non-designated beneficiaries?",
            "What deadlines apply to post-death IRA distributions (for example, ten-year rules or life-expectancy payouts)?",
            "How did recent law changes such as the SECURE Act and later updates affect inherited IRA planning?",
            "What common mistakes do beneficiaries and advisors make with inherited IRAs, and how can they be avoided?",
            "Imagine advising a beneficiary. What questions would you ask before recommending a distribution strategy?",
        ],
        difficulty=3,
    ),
    StudyTopic(
        id="tax_efficient_portfolio_spenddown",
        title="Tax Efficient Portfolio Spenddown Techniques",
        category="Individual Taxation",
        pdf_filename="handoutstaxefficientportfolio102120251759861912134.pdf",
        description=(
            "Focuses on how to sequence withdrawals from taxable, tax-deferred, "
            "and tax-free accounts over a client's lifetime to reduce overall "
            "taxes, manage brackets, and coordinate with Social Security, "
            "Medicare premiums, and estate planning goals."
        ),
        focus_questions=[
            "In what order should clients typically draw from taxable, traditional, and Roth accounts, and why might that order change?",
            "How can you smooth taxable income across retirement years to avoid bracket spikes and benefit cliffs?",
            "What role do capital gains, loss harvesting, and asset location play in a long-term spenddown plan?",
            "How do required minimum distributions, Social Security start dates, and Medicare premium thresholds interact with spenddown decisions?",
            "Sketch a simple spenddown plan for a hypothetical client and note where tax planning has the biggest impact.",
        ],
        difficulty=3,
    ),
]
