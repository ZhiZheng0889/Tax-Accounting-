from typing import List

from study_base import StudyTopic
from study_materials_accounting_analysis import ACCOUNTING_ANALYSIS_TOPICS
from study_materials_communication import COMMUNICATION_TOPICS
from study_materials_ethics import ETHICS_TOPICS
from study_materials_governmental import GOVERNMENTAL_TOPICS
from study_materials_individual_tax import INDIVIDUAL_TAX_TOPICS
from study_materials_technology import TECH_TOPICS


STUDY_TOPICS: List[StudyTopic] = (
    TECH_TOPICS
    + GOVERNMENTAL_TOPICS
    + INDIVIDUAL_TAX_TOPICS
    + ACCOUNTING_ANALYSIS_TOPICS
    + COMMUNICATION_TOPICS
    + ETHICS_TOPICS
)
