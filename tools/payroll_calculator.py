import argparse
import json
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
    ytd_wages: float = 0.0  # Year-to-date Medicare/SS taxable wages before this paycheck (FICA taxable)
    # Withholding mode
    withholding_method: str = "flat"  # 'flat' or 'irs_percentage'
    federal_rate: Optional[float] = None  # used when withholding_method == 'flat'
    state_rate: Optional[float] = None  # simple state flat rate
    # W-4 style inputs for percentage method
    filing_status: str = "single"  # single|married|head
    pay_periods_per_year: int = 26
    w4_step2: bool = False
    w4_step3_dependents_credit: float = 0.0  # annual credit amount
    w4_step4a_other_income: float = 0.0      # annual
    w4_step4b_deductions: float = 0.0        # annual, in excess of standard deduction
    w4_step4c_extra_withholding: float = 0.0 # per period extra withholding
    # Pre-tax deductions per period
    pretax_401k: float = 0.0            # reduces FIT only (traditional 401k)
    pretax_hsa: float = 0.0             # reduces FIT and FICA when via cafeteria plan
    pretax_section125: float = 0.0      # reduces FIT and FICA (e.g., health premiums)


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


def employer_medicare(employee_gross: float, *, ytd_wages: float, rate: float = 0.0145) -> float:
    """
    Employer Medicare portion is 1.45% on all wages. There is no employer-paid Additional Medicare tax.
    """
    return round(employee_gross * rate, 2)


# 2025 standard deductions (approx; for planning)
STANDARD_DEDUCTION_2025 = {
    "single": 14600.0,
    "married": 29200.0,
    "head": 21900.0,
}

# 2025 tax brackets (approximate) for percentage method (annualized)
# Each is list of tuples: (threshold, rate)
IRS_2025_BRACKETS = {
    "single": [
        (0, 0.10), (11600, 0.12), (47150, 0.22), (100525, 0.24), (191950, 0.32), (243725, 0.35), (609350, 0.37)
    ],
    "married": [
        (0, 0.10), (23200, 0.12), (94300, 0.22), (201050, 0.24), (383900, 0.32), (487450, 0.35), (731200, 0.37)
    ],
    "head": [
        (0, 0.10), (16550, 0.12), (63100, 0.22), (100500, 0.24), (191950, 0.32), (243700, 0.35), (609350, 0.37)
    ],
}


def _progressive_tax_annual(taxable_annual: float, filing_status: str) -> float:
    brackets = IRS_2025_BRACKETS.get(filing_status, IRS_2025_BRACKETS["single"])
    tax = 0.0
    last_threshold = 0.0
    last_rate = 0.0
    for i, (thr, rate) in enumerate(brackets):
        if i == 0:
            last_threshold = thr
            last_rate = rate
            continue
        if taxable_annual > thr:
            tax += (thr - last_threshold) * last_rate
            last_threshold = thr
            last_rate = rate
        else:
            break
    # Remaining amount
    tax += max(taxable_annual - last_threshold, 0) * last_rate
    return max(tax, 0.0)


def federal_withholding_percentage_method(
    fit_taxable_period: float,
    *,
    filing_status: str,
    pay_periods_per_year: int,
    w4_step2: bool,
    w4_step3_dependents_credit: float,
    w4_step4a_other_income: float,
    w4_step4b_deductions: float,
    w4_step4c_extra_withholding: float,
) -> float:
    """
    Simplified implementation of IRS Pub 15-T percentage-method withholding using annualization.
    This is an approximation for planning and may differ from exact IRS tables.
    """
    # Annualize wages
    annual_wages = fit_taxable_period * pay_periods_per_year
    if w4_step2:
        # Approximate Step 2 checkbox (multiple jobs): annualize as if two equal jobs
        annual_wages *= 2

    # Apply other income and deductions (Step 4)
    annual_taxable_income = max(annual_wages + (w4_step4a_other_income or 0.0) - (w4_step4b_deductions or 0.0), 0.0)

    # Subtract approximate standard deduction
    standard = STANDARD_DEDUCTION_2025.get(filing_status, STANDARD_DEDUCTION_2025["single"])
    annual_taxable_income = max(annual_taxable_income - standard, 0.0)

    # Compute annual tax
    annual_tax = _progressive_tax_annual(annual_taxable_income, filing_status)

    # Reduce by dependents credit (Step 3)
    annual_tax = max(annual_tax - (w4_step3_dependents_credit or 0.0), 0.0)

    # Convert to per-period
    per_period_tax = annual_tax / pay_periods_per_year

    # Add extra withholding per period (Step 4c)
    per_period_tax += (w4_step4c_extra_withholding or 0.0)

    return round(per_period_tax, 2)


def federal_withholding_percentage_details(
    fit_taxable_period: float,
    *,
    filing_status: str,
    pay_periods_per_year: int,
    w4_step2: bool,
    w4_step3_dependents_credit: float,
    w4_step4a_other_income: float,
    w4_step4b_deductions: float,
    w4_step4c_extra_withholding: float,
):
    # Annualize wages
    annual_wages = fit_taxable_period * pay_periods_per_year
    step2_multiplier = 2 if w4_step2 else 1
    annual_wages_adj = annual_wages * step2_multiplier

    # Apply other income and deductions (Step 4)
    annual_taxable_income_pre_std = max(annual_wages_adj + (w4_step4a_other_income or 0.0) - (w4_step4b_deductions or 0.0), 0.0)

    # Subtract approximate standard deduction
    standard = STANDARD_DEDUCTION_2025.get(filing_status, STANDARD_DEDUCTION_2025["single"])
    annual_taxable_income = max(annual_taxable_income_pre_std - standard, 0.0)

    # Compute annual tax with bracket steps
    brackets = IRS_2025_BRACKETS.get(filing_status, IRS_2025_BRACKETS["single"])
    remaining = annual_taxable_income
    steps = []
    tax = 0.0
    for i, (thr, rate) in enumerate(brackets):
        upper = brackets[i + 1][0] if i + 1 < len(brackets) else None
        if upper is None:
            amount = max(remaining - thr, 0)
        else:
            amount = max(min(annual_taxable_income, upper) - thr, 0)
        if amount > 0:
            step_tax = amount * rate
            steps.append({
                "lower": thr,
                "upper": upper,
                "rate": rate,
                "amount": round(amount, 2),
                "tax": round(step_tax, 2),
            })
            tax += step_tax
    tax = max(tax, 0.0)

    # Reduce by dependents credit (Step 3)
    credit = (w4_step3_dependents_credit or 0.0)
    annual_tax_after_credit = max(tax - credit, 0.0)

    # Convert to per-period
    per_period_tax = annual_tax_after_credit / pay_periods_per_year

    # Add extra withholding per period (Step 4c)
    extra = (w4_step4c_extra_withholding or 0.0)
    per_period_tax += extra

    details = {
        "annualized_wages": round(annual_wages, 2),
        "step2_multiplier": step2_multiplier,
        "annual_wages_after_step2": round(annual_wages_adj, 2),
        "other_income": round(w4_step4a_other_income or 0.0, 2),
        "deductions": round(w4_step4b_deductions or 0.0, 2),
        "pre_standard_taxable": round(annual_taxable_income_pre_std, 2),
        "standard_deduction": round(standard, 2),
        "annual_taxable": round(annual_taxable_income, 2),
        "bracket_steps": steps,
        "annual_tax_before_credit": round(tax, 2),
        "dependents_credit": round(credit, 2),
        "annual_tax_after_credit": round(annual_tax_after_credit, 2),
        "per_period_tax_before_extra": round(annual_tax_after_credit / pay_periods_per_year, 2),
        "extra_withholding": round(extra, 2),
    }
    return round(per_period_tax, 2), details


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


def _hours_from_daily(daily_hours: Optional[str], use_ca_daily_ot: bool) -> Dict[str, float]:
    """
    Parse comma-separated daily hours and compute breakdown.
    If use_ca_daily_ot is True: OT over 8 up to 12 (1.5x), DT over 12 (2.0x) per day. Weekly thresholds not layered here.
    Else: Weekly OT over 40 hours (1.5x), no double time.
    Returns dict with keys: regular_hours, overtime_hours, doubletime_hours.
    """
    if not daily_hours:
        return {"regular_hours": 0.0, "overtime_hours": 0.0, "doubletime_hours": 0.0}
    parts = [p.strip() for p in daily_hours.split(",") if p.strip()]
    hours_list = [float(p) for p in parts]
    reg = ot = dt = 0.0
    if use_ca_daily_ot:
        for h in hours_list:
            if h <= 8:
                reg += h
            elif h <= 12:
                reg += 8
                ot += (h - 8)
            else:
                reg += 8
                ot += 4
                dt += (h - 12)
    else:
        total = sum(hours_list)
        if total <= 40:
            reg = total
        else:
            reg = 40.0
            ot = total - 40.0
    return {"regular_hours": reg, "overtime_hours": ot, "doubletime_hours": dt}


def gross_pay(
    pay_type: str,
    *,
    hourly_rate: Optional[float] = None,
    hours: Optional[float] = None,
    overtime_hours: float = 0.0,
    overtime_multiplier: float = 1.5,
    doubletime_hours: float = 0.0,
    doubletime_multiplier: float = 2.0,
    daily_hours: Optional[str] = None,
    use_ca_daily_ot: bool = False,
    salary: Optional[float] = None,
) -> float:
    if pay_type == "hourly":
        if hourly_rate is None:
            raise ValueError("Hourly pay requires --hourly-rate")
        if daily_hours:
            br = _hours_from_daily(daily_hours, use_ca_daily_ot)
            reg_hours = br["regular_hours"]
            ot_hours = br["overtime_hours"]
            dt_hours = br["doubletime_hours"]
        else:
            reg_hours = float(hours) if hours is not None else 0.0
            ot_hours = float(overtime_hours or 0.0)
            dt_hours = float(doubletime_hours or 0.0)
        if reg_hours <= 0 and ot_hours <= 0 and dt_hours <= 0:
            raise ValueError("Provide hours via --hours/--overtime-hours or --daily-hours for hourly pay")
        gross = (
            (hourly_rate * reg_hours)
            + (hourly_rate * ot_hours * (overtime_multiplier or 1.0))
            + (hourly_rate * dt_hours * (doubletime_multiplier or 2.0))
        )
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
                     doubletime_hours: float = 0.0,
                     doubletime_multiplier: float = 2.0,
                     daily_hours: Optional[str] = None,
                     use_ca_daily_ot: bool = False,
                     salary: Optional[float] = None,
                     config: PayrollConfig) -> Dict[str, float]:
    g = gross_pay(
        pay_type,
        hourly_rate=hourly_rate,
        hours=hours,
        overtime_hours=overtime_hours,
        overtime_multiplier=overtime_multiplier,
        doubletime_hours=doubletime_hours,
        doubletime_multiplier=doubletime_multiplier,
        daily_hours=daily_hours,
        use_ca_daily_ot=use_ca_daily_ot,
        salary=salary,
    )

    # Pre-tax adjustments
    pretax_fit_only = max(config.pretax_401k, 0.0)
    pretax_fit_fica = max(config.pretax_hsa, 0.0) + max(config.pretax_section125, 0.0)

    fica_taxable = max(g - pretax_fit_fica, 0.0)
    fit_taxable = max(g - pretax_fit_only - pretax_fit_fica, 0.0)

    # Employee FICA
    ss = social_security(fica_taxable, year=config.year, ytd_wages=config.ytd_wages)
    medi = medicare(fica_taxable, ytd_wages=config.ytd_wages)

    # Federal withholding
    if config.withholding_method == "irs_percentage":
        fit = federal_withholding_percentage_method(
            fit_taxable,
            filing_status=config.filing_status,
            pay_periods_per_year=config.pay_periods_per_year,
            w4_step2=config.w4_step2,
            w4_step3_dependents_credit=config.w4_step3_dependents_credit,
            w4_step4a_other_income=config.w4_step4a_other_income,
            w4_step4b_deductions=config.w4_step4b_deductions,
            w4_step4c_extra_withholding=config.w4_step4c_extra_withholding,
        )
    else:
        fit = federal_income_tax(fit_taxable, config.federal_rate)

    # State withholding (still flat, applied to FIT taxable wages)
    sit = state_income_tax(fit_taxable, config.state_rate)

    total_deductions = round(ss + medi + fit + sit, 2)
    net = round(g - total_deductions, 2)

    # Employer costs
    employer_ss = social_security(fica_taxable, year=config.year, ytd_wages=config.ytd_wages)
    employer_medi_amt = employer_medicare(fica_taxable, ytd_wages=config.ytd_wages)
    employer_total = round(employer_ss + employer_medi_amt, 2)

    return {
        "gross": g,
        "taxable_wages_fica": round(fica_taxable, 2),
        "taxable_wages_fit": round(fit_taxable, 2),
        "social_security": ss,
        "medicare": medi,
        "federal_income_tax": fit,
        "state_income_tax": sit,
        "total_deductions": total_deductions,
        "net": net,
        "employer_social_security": round(employer_ss, 2),
        "employer_medicare": round(employer_medi_amt, 2),
        "employer_total": employer_total,
    }


def build_explanation_text(
    pay_type: str,
    *,
    hourly_rate: Optional[float] = None,
    hours: Optional[float] = None,
    overtime_hours: float = 0.0,
    overtime_multiplier: float = 1.5,
    doubletime_hours: float = 0.0,
    doubletime_multiplier: float = 2.0,
    daily_hours: Optional[str] = None,
    use_ca_daily_ot: bool = False,
    salary: Optional[float] = None,
    config: PayrollConfig,
) -> str:
    # Recompute components needed for explanation
    if pay_type == "hourly":
        if daily_hours:
            br = _hours_from_daily(daily_hours, use_ca_daily_ot)
            reg_hours = br["regular_hours"]
            ot_hours = br["overtime_hours"]
            dt_hours = br["doubletime_hours"]
        else:
            reg_hours = float(hours) if hours is not None else 0.0
            ot_hours = float(overtime_hours or 0.0)
            dt_hours = float(doubletime_hours or 0.0)
        gross = (
            (hourly_rate * reg_hours)
            + (hourly_rate * ot_hours * (overtime_multiplier or 1.0))
            + (hourly_rate * dt_hours * (doubletime_multiplier or 2.0))
        )
    else:
        reg_hours = ot_hours = dt_hours = 0.0
        gross = float(salary or 0.0)

    pretax_fit_only = max(config.pretax_401k, 0.0)
    pretax_fit_fica = max(config.pretax_hsa, 0.0) + max(config.pretax_section125, 0.0)
    fica_taxable = max(gross - pretax_fit_fica, 0.0)
    fit_taxable = max(gross - pretax_fit_only - pretax_fit_fica, 0.0)

    # Social Security details
    base = SSA_WAGE_BASE_BY_YEAR.get(config.year, max(SSA_WAGE_BASE_BY_YEAR.values()))
    already = min(config.ytd_wages, base)
    remaining = max(base - already, 0)
    ss_taxable_this = _clamp(fica_taxable, 0, remaining)
    ss_tax = round(ss_taxable_this * 0.062, 2)

    # Medicare details
    addl_threshold = 200000.0
    pre = config.ytd_wages
    post = config.ytd_wages + fica_taxable
    base_medi = round(fica_taxable * 0.0145, 2)
    addl_medi_taxable = 0.0
    if post > addl_threshold:
        crossed_from = max(addl_threshold - pre, 0)
        addl_medi_taxable = max(fica_taxable - crossed_from, 0)
    addl_medi = round(addl_medi_taxable * 0.009, 2)

    lines = []
    lines.append("Earnings:")
    if pay_type == "hourly":
        if reg_hours:
            lines.append(f"- Regular: {reg_hours:.2f}h x ${hourly_rate:.2f} = ${hourly_rate*reg_hours:.2f}")
        if ot_hours:
            lines.append(f"- Overtime: {ot_hours:.2f}h x ${hourly_rate:.2f} x {overtime_multiplier:.2f} = ${hourly_rate*ot_hours*overtime_multiplier:.2f}")
        if dt_hours:
            lines.append(f"- Double-time: {dt_hours:.2f}h x ${hourly_rate:.2f} x {doubletime_multiplier:.2f} = ${hourly_rate*dt_hours*doubletime_multiplier:.2f}")
    else:
        lines.append(f"- Salary per period = ${gross:.2f}")
    lines.append(f"Gross = ${gross:.2f}")

    if pretax_fit_only or pretax_fit_fica:
        lines.append("Pre-tax deductions:")
        if pretax_fit_only:
            lines.append(f"- 401(k) (FIT only): ${pretax_fit_only:.2f}")
        if pretax_fit_fica:
            lines.append(f"- HSA/Section125 (FIT+FICA): ${pretax_fit_fica:.2f}")
        lines.append(f"FICA taxable wages = Gross - FIT+FICA pretax = ${fica_taxable:.2f}")
        lines.append(f"FIT taxable wages = Gross - all applicable pretax = ${fit_taxable:.2f}")

    lines.append("Social Security (6.2% up to wage base):")
    lines.append(f"- Year {config.year} wage base: ${base:,.0f}; YTD counted: ${already:,.2f}; remaining room: ${remaining:,.2f}")
    lines.append(f"- This period SS-taxable: ${ss_taxable_this:.2f} -> Tax: ${ss_tax:.2f}")

    lines.append("Medicare (1.45% on all; +0.9% over $200k YTD):")
    lines.append(f"- Base Medicare on ${fica_taxable:.2f} = ${base_medi:.2f}")
    if addl_medi_taxable > 0:
        lines.append(f"- Additional Medicare on ${addl_medi_taxable:.2f} = ${addl_medi:.2f}")
    lines.append(f"- Total Medicare = ${base_medi + addl_medi:.2f}")

    if config.withholding_method == "irs_percentage":
        tax, det = federal_withholding_percentage_details(
            fit_taxable,
            filing_status=config.filing_status,
            pay_periods_per_year=config.pay_periods_per_year,
            w4_step2=config.w4_step2,
            w4_step3_dependents_credit=config.w4_step3_dependents_credit,
            w4_step4a_other_income=config.w4_step4a_other_income,
            w4_step4b_deductions=config.w4_step4b_deductions,
            w4_step4c_extra_withholding=config.w4_step4c_extra_withholding,
        )
        lines.append("Federal Income Tax (IRS percentage method, per period):")
        lines.append(f"- Annualized wages: ${det['annualized_wages']:.2f} x Step2 = ${det['annual_wages_after_step2']:.2f}")
        lines.append(f"- +Other income ${det['other_income']:.2f} - Deductions ${det['deductions']:.2f} = Pre-standard ${det['pre_standard_taxable']:.2f}")
        lines.append(f"- Standard deduction ${det['standard_deduction']:.2f} -> Annual taxable ${det['annual_taxable']:.2f}")
        if det['bracket_steps']:
            lines.append("- Brackets:")
            for s in det['bracket_steps']:
                up = f"{s['upper']:,}" if s['upper'] is not None else "inf"
                lines.append(f"  {s['lower']:,}-{up} @ {s['rate']*100:.1f}% on ${s['amount']:.2f} = ${s['tax']:.2f}")
        lines.append(f"- Annual tax before credits: ${det['annual_tax_before_credit']:.2f}")
        lines.append(f"- Dependents credit: -${det['dependents_credit']:.2f}")
        lines.append(f"- Per-period tax before extra: ${det['per_period_tax_before_extra']:.2f}")
        lines.append(f"- Extra withholding: +${det['extra_withholding']:.2f}")
        lines.append(f"- Federal withholding this period: ${tax:.2f}")
    else:
        if config.federal_rate:
            lines.append(f"Federal Income Tax (flat {config.federal_rate*100:.2f}% on FIT taxable ${fit_taxable:.2f})")
            lines.append(f"- Federal withholding: ${round(fit_taxable * config.federal_rate, 2):.2f}")
        else:
            lines.append("Federal Income Tax: (not withheld)")

    if config.state_rate:
        lines.append(f"State Income Tax (flat {config.state_rate*100:.2f}% on FIT taxable ${fit_taxable:.2f})")
        lines.append(f"- State withholding: ${round(fit_taxable * config.state_rate, 2):.2f}")

    result = compute_paycheck(
        pay_type,
        hourly_rate=hourly_rate,
        hours=hours,
        overtime_hours=overtime_hours,
        overtime_multiplier=overtime_multiplier,
        doubletime_hours=doubletime_hours,
        doubletime_multiplier=doubletime_multiplier,
        daily_hours=daily_hours,
        use_ca_daily_ot=use_ca_daily_ot,
        salary=salary,
        config=config,
    )
    lines.append("")
    lines.append(f"Total deductions = ${result['total_deductions']:.2f}")
    lines.append(f"Net pay = Gross - deductions = ${result['net']:.2f}")
    return "\n".join(lines)


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
    p.add_argument("--doubletime-hours", type=float, default=0.0, help="Double-time hours this period (default 0)")
    p.add_argument("--doubletime-multiplier", type=float, default=2.0, help="Double-time multiplier (default 2.0x)")
    p.add_argument("--daily-hours", type=str, help="Comma-separated daily hours (e.g., 8,9,10,6,7) to auto-calc OT")
    p.add_argument("--use-ca-daily-ot", action="store_true", help="Apply CA daily OT rules to --daily-hours (OT >8, DT >12)")
    p.add_argument("--salary", type=float, help="Salary amount per pay period (for salary pay)")

    p.add_argument("--year", type=int, default=2025, help="Tax year (for SSA wage base)")
    p.add_argument("--ytd-wages", type=float, default=0.0, help="Year-to-date taxable wages before this paycheck")
    p.add_argument("--withholding-method", choices=["flat", "irs_percentage"], default="flat", help="Federal withholding method: flat rate or IRS percentage method")
    p.add_argument("--federal-rate", type=str, default=None, help="Flat federal rate (e.g., 12 or 0.12 or 12%) if --withholding-method flat")
    p.add_argument("--state-rate", type=str, default=None, help="Optional state withholding rate (e.g., 5 or 0.05 or 5%)")

    # W-4 inputs (percentage method)
    p.add_argument("--filing-status", choices=["single", "married", "head"], default="single")
    p.add_argument("--pay-periods", type=int, default=26, help="Pay periods per year (e.g., 52 weekly, 26 biweekly, 24 semi-monthly)")
    p.add_argument("--w4-step2", action="store_true", help="W-4 Step 2 checkbox (multiple jobs)")
    p.add_argument("--w4-step3", type=float, default=0.0, help="W-4 Step 3 annual credit amount (e.g., 2000 per qualifying child)")
    p.add_argument("--w4-step4a", type=float, default=0.0, help="W-4 Step 4(a) other annual income")
    p.add_argument("--w4-step4b", type=float, default=0.0, help="W-4 Step 4(b) deductions (annual, beyond standard)")
    p.add_argument("--w4-step4c", type=float, default=0.0, help="W-4 Step 4(c) extra withholding per period")

    # Pre-tax deductions (per period)
    p.add_argument("--pretax-401k", type=float, default=0.0, help="Traditional 401(k) deferral amount per period (reduces FIT only)")
    p.add_argument("--pretax-hsa", type=float, default=0.0, help="HSA contribution per period (reduces FIT and FICA if via cafeteria plan)")
    p.add_argument("--pretax-section125", type=float, default=0.0, help="Section 125 premiums per period (reduces FIT and FICA)")

    # Output / UX
    p.add_argument("--json", action="store_true", help="Output JSON instead of text")
    p.add_argument("--explain", action="store_true", help="Print a detailed step-by-step explanation")
    p.add_argument("--output-csv", type=str, default=None, help="Write a one-line CSV of results to this path")

    args = p.parse_args()

    config = PayrollConfig(
        year=args.year,
        ytd_wages=args.ytd_wages,
        withholding_method=args.withholding_method,
        federal_rate=_parse_rate(args.federal_rate),
        state_rate=_parse_rate(args.state_rate),
        filing_status=args.filing_status,
        pay_periods_per_year=args.pay_periods,
        w4_step2=args.w4_step2,
        w4_step3_dependents_credit=args.w4_step3,
        w4_step4a_other_income=args.w4_step4a,
        w4_step4b_deductions=args.w4_step4b,
        w4_step4c_extra_withholding=args.w4_step4c,
        pretax_401k=args.pretax_401k,
        pretax_hsa=args.pretax_hsa,
        pretax_section125=args.pretax_section125,
    )

    result = compute_paycheck(
        args.pay_type,
        hourly_rate=args.hourly_rate,
        hours=args.hours,
        overtime_hours=args.overtime_hours,
        overtime_multiplier=args.overtime_multiplier,
        doubletime_hours=args.doubletime_hours,
        doubletime_multiplier=args.doubletime_multiplier,
        daily_hours=args.daily_hours,
        use_ca_daily_ot=args.use_ca_daily_ot,
        salary=args.salary,
        config=config,
    )

    # Output handling
    if args.output_csv:
        import csv
        with open(args.output_csv, "w", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "gross","taxable_wages_fica","taxable_wages_fit","social_security","medicare",
                    "federal_income_tax","state_income_tax","total_deductions","net",
                    "employer_social_security","employer_medicare","employer_total"
                ],
            )
            writer.writeheader()
            writer.writerow(result)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        # Pretty print
        print("Gross:", f"${result['gross']:.2f}")
        print("FICA Taxable Wages:", f"${result['taxable_wages_fica']:.2f}")
        print("FIT Taxable Wages:", f"${result['taxable_wages_fit']:.2f}")
        print("- Social Security:", f"${result['social_security']:.2f}")
        print("- Medicare:", f"${result['medicare']:.2f}")
        if config.withholding_method == "flat" and config.federal_rate:
            print("- Federal Income Tax:", f"${result['federal_income_tax']:.2f}")
        elif config.withholding_method == "irs_percentage":
            print("- Federal Income Tax (IRS % method):", f"${result['federal_income_tax']:.2f}")
        if config.state_rate:
            print("- State Income Tax:", f"${result['state_income_tax']:.2f}")
        print("Total Deductions:", f"${result['total_deductions']:.2f}")
        print("Net Pay:", f"${result['net']:.2f}")
        print("Employer Social Security:", f"${result['employer_social_security']:.2f}")
        print("Employer Medicare:", f"${result['employer_medicare']:.2f}")
        print("Employer Total Payroll Taxes:", f"${result['employer_total']:.2f}")
        if args.explain:
            print()
            print(build_explanation_text(
                args.pay_type,
                hourly_rate=args.hourly_rate,
                hours=args.hours,
                overtime_hours=args.overtime_hours,
                overtime_multiplier=args.overtime_multiplier,
                doubletime_hours=args.doubletime_hours if 'doubletime_hours' in args else 0.0,
                doubletime_multiplier=args.doubletime_multiplier if 'doubletime_multiplier' in args else 2.0,
                daily_hours=args.daily_hours if 'daily_hours' in args else None,
                use_ca_daily_ot=args.use_ca_daily_ot if 'use_ca_daily_ot' in args else False,
                salary=args.salary,
                config=config,
            ))


if __name__ == "__main__":
    main()
