import argparse
from dataclasses import dataclass
from typing import Optional, Dict


# 2025 Social Security wage base (edit as needed in future years)
SSA_WAGE_BASE_BY_YEAR = {
    2023: 160200,
    2024: 168600,
    2025: 174000,
}


@dataclass
class PayrollConfig:
    year: int = 2025
    ytd_wages: float = 0.0  # Year-to-date Medicare/SS taxable wages before this paycheck
    federal_rate: Optional[float] = None  # e.g., 0.12 for 12%; None or 0 to skip
    state_rate: Optional[float] = None  # e.g., 0.05 for 5%; None or 0 to skip


def _clamp(val: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, val))


def social_security(employee_gross: float, *, year: int, ytd_wages: float, rate: float = 0.062) -> float:
    """
    Employee Social Security (OASDI) at 6.2% up to wage base.
    Considers YTD wages for proper capping within the year.
    """
    base = SSA_WAGE_BASE_BY_YEAR.get(year)
    if base is None:
        # Default to most recent known base if year not found
        base = max(SSA_WAGE_BASE_BY_YEAR.values())

    # Taxable portion this period is the part that remains under the wage base
    already_counted = min(ytd_wages, base)
    remaining_room = max(base - already_counted, 0)
    taxable_this_period = _clamp(employee_gross, 0, remaining_room)
    return round(taxable_this_period * rate, 2)


def medicare(employee_gross: float, *, ytd_wages: float, rate: float = 0.0145, addl_threshold: float = 200000.0, addl_rate: float = 0.009) -> float:
    """
    Employee Medicare at 1.45% on all wages + Additional Medicare 0.9% on wages over $200,000.
    Considers YTD wages for when the additional rate kicks in.
    """
    # Base Medicare on all current wages
    base_part = employee_gross * rate

    # Additional Medicare applies only to wages above the threshold
    pre = ytd_wages
    post = ytd_wages + employee_gross
    addl_taxable = 0.0
    if post > addl_threshold:
        # Portion of this period that crosses the threshold
        crossed_from = max(addl_threshold - pre, 0)
        addl_taxable = max(employee_gross - crossed_from, 0)

    addl_part = addl_taxable * addl_rate
    return round(base_part + addl_part, 2)


def federal_income_tax(employee_gross: float, federal_rate: Optional[float]) -> float:
    """
    Simplified federal withholding: flat percentage if provided. If None/0, returns 0.
    Users can supply an effective rate that reflects their W-4/withholding strategy.
    """
    if not federal_rate or federal_rate <= 0:
        return 0.0
    return round(employee_gross * federal_rate, 2)


def state_income_tax(employee_gross: float, state_rate: Optional[float]) -> float:
    if not state_rate or state_rate <= 0:
        return 0.0
    return round(employee_gross * state_rate, 2)


def gross_pay(
    pay_type: str,
    *,
    hourly_rate: Optional[float] = None,
    hours: Optional[float] = None,
    overtime_hours: float = 0.0,
    overtime_multiplier: float = 1.5,
    salary: Optional[float] = None,
) -> float:
    if pay_type == "hourly":
        if hourly_rate is None:
            raise ValueError("Hourly pay requires --hourly-rate")
        reg_hours = float(hours) if hours is not None else 0.0
        ot_hours = float(overtime_hours or 0.0)
        if reg_hours <= 0 and ot_hours <= 0:
            raise ValueError("Provide --hours and/or --overtime-hours for hourly pay")
        gross = (hourly_rate * reg_hours) + (hourly_rate * ot_hours * (overtime_multiplier or 1.0))
        return round(gross, 2)
    elif pay_type == "salary":
        if salary is None:
            raise ValueError("Salary pay requires --salary (per pay period)")
        return round(salary, 2)
    else:
        raise ValueError("pay_type must be 'hourly' or 'salary'")


def compute_paycheck(pay_type: str,
                     *,
                     hourly_rate: Optional[float] = None,
                     hours: Optional[float] = None,
                     overtime_hours: float = 0.0,
                     overtime_multiplier: float = 1.5,
                     salary: Optional[float] = None,
                     config: PayrollConfig) -> Dict[str, float]:
    g = gross_pay(
        pay_type,
        hourly_rate=hourly_rate,
        hours=hours,
        overtime_hours=overtime_hours,
        overtime_multiplier=overtime_multiplier,
        salary=salary,
    )

    ss = social_security(g, year=config.year, ytd_wages=config.ytd_wages)
    medi = medicare(g, ytd_wages=config.ytd_wages)
    fit = federal_income_tax(g, config.federal_rate)
    sit = state_income_tax(g, config.state_rate)

    total_deductions = round(ss + medi + fit + sit, 2)
    net = round(g - total_deductions, 2)

    return {
        "gross": g,
        "social_security": ss,
        "medicare": medi,
        "federal_income_tax": fit,
        "state_income_tax": sit,
        "total_deductions": total_deductions,
        "net": net,
    }


def _parse_rate(val: Optional[str]) -> Optional[float]:
    if val is None:
        return None
    s = val.strip().replace("%", "")
    if not s:
        return None
    num = float(s)
    # If user passed 12 or 12%, treat as 0.12
    return num / 100.0 if num > 1 else num


def main():
    p = argparse.ArgumentParser(description="Payroll calculator for Social Security, Medicare, and optional Fed/State withholding.")
    p.add_argument("--pay-type", choices=["hourly", "salary"], required=True, help="Pay type for this paycheck")
    p.add_argument("--hourly-rate", type=float, help="Hourly rate (for hourly pay)")
    p.add_argument("--hours", type=float, help="Regular hours in this pay period (for hourly pay)")
    p.add_argument("--overtime-hours", type=float, default=0.0, help="Overtime hours this period (default 0). Typical FLSA weekly OT is hours over 40.")
    p.add_argument(
        "--overtime-multiplier",
        type=float,
        default=1.5,
        help="Overtime rate multiplier (default 1.5x). Use 2.0 for double-time scenarios.",
    )
    p.add_argument("--salary", type=float, help="Salary amount per pay period (for salary pay)")

    p.add_argument("--year", type=int, default=2025, help="Tax year (for SSA wage base)")
    p.add_argument("--ytd-wages", type=float, default=0.0, help="Year-to-date taxable wages before this paycheck")
    p.add_argument("--federal-rate", type=str, default=None, help="Optional federal withholding rate (e.g., 12 or 0.12 or 12%)")
    p.add_argument("--state-rate", type=str, default=None, help="Optional state withholding rate (e.g., 5 or 0.05 or 5%)")

    args = p.parse_args()

    config = PayrollConfig(
        year=args.year,
        ytd_wages=args.ytd_wages,
        federal_rate=_parse_rate(args.federal_rate),
        state_rate=_parse_rate(args.state_rate),
    )

    result = compute_paycheck(
        args.pay_type,
        hourly_rate=args.hourly_rate,
        hours=args.hours,
        overtime_hours=args.overtime_hours,
        overtime_multiplier=args.overtime_multiplier,
        salary=args.salary,
        config=config,
    )

    # Pretty print
    print("Gross:", f"${result['gross']:.2f}")
    print("- Social Security:", f"${result['social_security']:.2f}")
    print("- Medicare:", f"${result['medicare']:.2f}")
    if config.federal_rate:
        print("- Federal Income Tax:", f"${result['federal_income_tax']:.2f}")
    if config.state_rate:
        print("- State Income Tax:", f"${result['state_income_tax']:.2f}")
    print("Total Deductions:", f"${result['total_deductions']:.2f}")
    print("Net Pay:", f"${result['net']:.2f}")


if __name__ == "__main__":
    main()
