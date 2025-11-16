import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS_DIR = ROOT / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from payroll_calculator import gross_pay, social_security, medicare  # noqa: E402


def test_gross_pay_hourly_basic() -> None:
    assert gross_pay("hourly", hourly_rate=20.0, hours=40.0) == 800.0


def test_gross_pay_salary_basic() -> None:
    assert gross_pay("salary", salary=3500.0) == 3500.0


def test_social_security_caps_at_wage_base() -> None:
    amount = social_security(10_000.0, year=2025, ytd_wages=180_000.0)
    assert amount == 0.0


def test_medicare_additional_tax_triggers_above_threshold() -> None:
    base_only = medicare(1_000.0, ytd_wages=0.0)
    with_additional = medicare(1_000.0, ytd_wages=200_000.0)
    assert with_additional > base_only

