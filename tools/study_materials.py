from typing import List

from study_base import StudyTopic


STUDY_TOPICS: List[StudyTopic] = [
    StudyTopic(
        id="tech_change_in_accounting",
        title="Embracing Technology Change in Accounting",
        category="Technology and Productivity",
        pdf_filename="HANDOUTS Embracing Technology Change in Accounting (10-30-2025).pdf",
        description=(
            "A big-picture look at how automation, AI, cloud platforms, and "
            "specialized apps reshape day-to-day accounting work, client "
            "expectations, and the skills practitioners need to stay relevant. "
            "Think about how your own workflows could change over the next "
            "3–5 years and what you can do now to prepare."
        ),
        focus_questions=[
            "What are the main technology trends affecting accounting today (automation, AI, cloud, data analytics)?",
            "Which of your current tasks are most likely to be automated, and how could you move up the value chain?",
            "How can firms evaluate which tools to adopt (cost, integration, security, staff skill level)?",
            "What risks (data, security, dependence on vendors) and opportunities (advisory services, efficiency) come with rapid technology change?",
            "If you had to pick one process in your work to re-design with technology, what would it be and why?"
        ],
    ),
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
            "Where in your own experience have you seen confusion between governmental and commercial accounting concepts?"
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
            "If you had to design a short year-end checklist for a small government, what would be on it?"
        ],
    ),
    StudyTopic(
        id="tax_updates_individuals_2025",
        title="2025 Tax Updates for Individuals",
        category="Individual Taxation",
        pdf_filename="handouts2025taxupdatesforindividuals111420251762457167904.pdf",
        description=(
            "Walks through the latest federal individual tax changes for 2025, "
            "including new brackets, inflation adjustments, credits, deductions, "
            "and planning opportunities or pitfalls. Focus on how these changes "
            "affect different types of clients (wage earners, retirees, investors, "
            "small business owners)."
        ),
        focus_questions=[
            "Which 2025 changes most affect middle-income taxpayers versus higher-income taxpayers?",
            "How did standard deductions, child-related credits, and common above-the-line deductions change?",
            "Which planning strategies help clients respond (timing of income/deductions, retirement contributions, charitable giving)?",
            "What new or expanded tax traps should you warn clients about (phaseouts, surtaxes, limitations)?",
            "How would you summarize the key 2025 changes in one page for a non-technical client?"
        ],
    ),
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
            "Think of a recent decision you or a manager made—how could better use of financial statements have improved that decision?"
        ],
    ),
    StudyTopic(
        id="technical_writing_fundamentals",
        title="Fundamentals of Technical Writing: Clarity and Readability",
        category="Communication and Writing",
        pdf_filename="handoutsfundamentalsoftechnicalwriting110420251761571939104.pdf",
        description=(
            "Covers the essentials of explaining complex ideas clearly: structuring "
            "documents, choosing precise language, using examples and visuals, and "
            "editing for clarity and readability. This is directly useful for memos, "
            "emails to clients, documentation, and training materials."
        ),
        focus_questions=[
            "What makes technical content clear rather than confusing (structure, word choice, assumptions about the reader)?",
            "How should you structure a technical explanation so that a busy reader can follow it quickly?",
            "Which editing steps (shortening sentences, replacing jargon, adding headings) improve readability the most?",
            "How can you use concrete examples or simple diagrams to make abstract concepts understandable?",
            "Pick one recent email or memo you wrote—how could you rewrite it using these principles?"
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
            "Choose one ratio you find confusing and write out, in words, what it tells you about a business."
        ],
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
            "What deadlines apply to post-death IRA distributions (10-year rules, life-expectancy payouts, etc.)?",
            "How did recent law changes (such as the SECURE Act and updates) affect inherited IRA planning?",
            "What common mistakes do beneficiaries and advisors make with inherited IRAs, and how can they be avoided?",
            "Imagine advising a beneficiary—what questions would you ask before recommending a distribution strategy?"
        ],
    ),
    StudyTopic(
        id="tax_efficient_portfolio_spenddown",
        title="Tax Efficient Portfolio Spenddown Techniques",
        category="Individual Taxation",
        pdf_filename="handoutstaxefficientportfolio102120251759861912134.pdf",
        description=(
            "Focuses on how to sequence withdrawals from taxable, tax-deferred, "
            "and tax-free accounts over a client’s lifetime to reduce overall "
            "taxes, manage brackets, and coordinate with Social Security, "
            "Medicare premiums, and estate planning goals."
        ),
        focus_questions=[
            "In what order should clients typically draw from taxable, traditional, and Roth accounts, and why might that order change?",
            "How can you smooth taxable income across retirement years to avoid bracket spikes and benefit cliffs?",
            "What role do capital gains, loss harvesting, and asset location play in a long-term spenddown plan?",
            "How do RMDs, Social Security start dates, and Medicare premium thresholds interact with spenddown decisions?",
            "Sketch a simple spenddown plan for a hypothetical client and note where tax planning has the biggest impact."
        ],
    ),
    StudyTopic(
        id="tax_practice_standards",
        title="Tax Practice Standards",
        category="Ethics and Practice Management",
        pdf_filename="handoutstaxpracticestandards103120251758634751069.pdf",
        description=(
            "Reviews the professional and ethical standards that govern tax "
            "practice, including due diligence requirements, documentation "
            "expectations, reliance on client information, and when disclosures "
            "or penalty protections apply. This is about protecting both you "
            "and your clients."
        ),
        focus_questions=[
            "What due diligence is required before signing a return or giving advice, and where do those standards come from?",
            "When must you disclose uncertain tax positions or advise a client about potential penalties?",
            "How should you document advice, client communications, and positions taken to protect both you and the client?",
            "How do you balance client advocacy with your ethical and legal responsibilities as a tax professional?",
            "Think of a grey-area scenario—how would these standards guide your response?"
        ],
    ),
    StudyTopic(
        id="ten_tech_productivity_hacks",
        title="Ten Tech Productivity Life Hacks to Save Time",
        category="Technology and Productivity",
        pdf_filename="handoutstentechproductivitylifehacks102820251760699229725.pdf",
        description=(
            "Presents concrete technology tips, shortcuts, and small workflow "
            "changes that can add up to significant time savings. The goal is "
            "to identify friction in your daily routine and systematically "
            "remove it using simple tools and habits."
        ),
        focus_questions=[
            "Which repetitive tasks in your day could be automated or batched, and what tools might help?",
            "What shortcuts, templates, or checklists would save you the most time over a month?",
            "How can you standardize workflows (folder structures, naming conventions, saved searches) to avoid rework and hunting for files?",
            "Where do you experience the most frustration or delay in your current tech setup, and what small change could improve it?",
            "Pick one hack from this session and write down exactly how you will implement it this week."
        ],
    ),
]
