from typing import List

from study_base import StudyTopic


TECH_TOPICS: List[StudyTopic] = [
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
            "3-5 years and what you can do now to prepare."
        ),
        focus_questions=[
            "What are the main technology trends affecting accounting today (automation, AI, cloud, data analytics)?",
            "Which of your current tasks are most likely to be automated, and how could you move up the value chain?",
            "How can firms evaluate which tools to adopt (cost, integration, security, staff skill level)?",
            "What risks (data, security, dependence on vendors) and opportunities (advisory services, efficiency) come with rapid technology change?",
            "If you had to pick one process in your work to re-design with technology, what would it be and why?",
        ],
        difficulty=3,
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
            "Pick one hack from this session and write down exactly how you will implement it this week.",
        ],
        difficulty=2,
    ),
]
