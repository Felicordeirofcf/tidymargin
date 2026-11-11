"""Reference implementation of the cleaning-job pricing math.

This module is the single source of truth for the formulas that are written
into the Excel / Google Sheets workbooks.  The workbook tests recalculate the
generated files with LibreOffice and compare every result against this code,
so any change here must be mirrored in ``build_workbooks.py`` (and vice versa).

Key definitions (all money in USD, percentages as fractions, e.g. 0.30):

* Labor hours  = (sqft / sqft_per_labor_hour + bedrooms*bed_hours
                  + bathrooms*bath_hours) * service_multiplier * property_multiplier
                  * condition_multiplier
                 (or the user's manual override)
* Labor cost   = labor hours * wage * (1 + payroll burden)
* Direct cost  = labor + supplies + travel (miles * cost per mile) + other direct
* Overhead     = monthly overhead / expected jobs per month
* Total cost   = direct cost + overhead
* Card fee     = (price + sales tax) * card fee %   -> grows with the price
* Price        = total cost / (1 - target margin - card fee % * (1 + tax %))
  so that   net profit / price == target margin   (MARGIN on revenue, not markup)
* Charged price = max(minimum job price, price rounded UP to the rounding step)

Markup vs. margin: a 30% *markup* on a $100 cost gives $130 (23.1% margin);
a 30% *margin* needs $142.86.  The kit always solves for margin.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

# --- Example defaults (clearly labelled as examples in the workbook) --------

SERVICE_TYPES = {  # name -> labor-time multiplier (EXAMPLE values, editable)
    "Standard Cleaning": 1.0,
    "Deep Cleaning": 1.75,
    "Move-In Cleaning": 1.75,
    "Move-Out Cleaning": 2.0,
    "Office Cleaning": 1.0,
    "Recurring Cleaning": 0.85,
}

PROPERTY_TYPES = {  # name -> labor-time multiplier (EXAMPLE values, editable)
    "House": 1.0,
    "Apartment / Condo": 1.0,
    "Townhouse": 1.0,
    "Office": 1.0,
    "Retail / Commercial": 1.0,
    "Other": 1.0,
}

CONDITIONS = {  # name -> labor-time multiplier (EXAMPLE values, editable)
    "Well kept": 1.0,
    "Average": 1.1,
    "Pets / heavy use": 1.2,
    "Needs extra work": 1.35,
}

FREQUENCIES = {  # name -> (discount, interval in days; 0 = not recurring)
    "One-time": (0.0, 0),
    "Weekly": (0.15, 7),
    "Every 2 weeks": (0.10, 14),
    "Every 4 weeks": (0.05, 28),
    "Monthly": (0.05, 30),
}


@dataclass
class Settings:
    wage: float = 18.0                 # $ per labor hour paid to cleaners
    payroll_burden: float = 0.12       # payroll taxes / workers comp etc.
    sqft_per_labor_hour: float = 1000  # production rate (EXAMPLE)
    hours_per_bedroom: float = 0.25
    hours_per_bathroom: float = 0.5
    cost_per_mile: float = 0.70        # vehicle cost per mile (EXAMPLE)
    monthly_overhead: float = 1200.0   # insurance, phone, software, marketing...
    jobs_per_month: float = 40
    card_fee: float = 0.029            # card processing % on amount collected
    target_margin: float = 0.30        # net profit / price
    sales_tax: float = 0.0             # only if your state taxes cleaning
    rounding: float = 5.0              # round price UP to this step
    minimum_price: float = 100.0
    service_types: dict = field(default_factory=lambda: dict(SERVICE_TYPES))
    property_types: dict = field(default_factory=lambda: dict(PROPERTY_TYPES))
    frequencies: dict = field(default_factory=lambda: dict(FREQUENCIES))
    conditions: dict = field(default_factory=lambda: dict(CONDITIONS))


@dataclass
class Job:
    property_type: str = "House"
    service_type: str = "Standard Cleaning"
    frequency: str = "One-time"
    sqft: float = 0.0
    bedrooms: float = 0.0
    bathrooms: float = 0.0
    crew: float = 1.0
    hours_override: float | None = None
    condition: str = ""                # blank = no adjustment (x1.0)
    supplies: float = 0.0
    miles: float = 0.0
    other_direct: float = 0.0
    extra_discount: float = 0.0
    wage_override: float | None = None
    margin_override: float | None = None
    tax_override: float | None = None


class PricingError(ValueError):
    """Raised for inputs the workbook would flag with a warning message."""


def round_up(value: float, step: float) -> float:
    """Mirror of Excel ROUNDUP(value/step, 0)*step (step <= 0 -> no rounding)."""
    if step <= 0:
        return value
    q = value / step
    # protect against float noise such as 145.00000000000003 / 5
    q_rounded = round(q, 9)
    return math.ceil(q_rounded) * step


def labor_hours(job: Job, s: Settings) -> float:
    if job.hours_override not in (None, ""):
        return float(job.hours_override)
    base = (
        (job.sqft / s.sqft_per_labor_hour if s.sqft_per_labor_hour else 0)
        + job.bedrooms * s.hours_per_bedroom
        + job.bathrooms * s.hours_per_bathroom
    )
    cond = s.conditions.get(job.condition, 1.0)
    return base * s.service_types[job.service_type] * s.property_types[job.property_type] * cond


def quote(job: Job, s: Settings) -> dict:
    for name in ("sqft", "bedrooms", "bathrooms", "supplies", "miles", "other_direct"):
        if getattr(job, name) < 0:
            raise PricingError(f"{name} cannot be negative")
    if job.crew <= 0:
        raise PricingError("crew must be at least 1")

    wage = s.wage if job.wage_override is None else job.wage_override
    margin = s.target_margin if job.margin_override is None else job.margin_override
    tax = s.sales_tax if job.tax_override is None else job.tax_override

    hours = labor_hours(job, s)
    labor = hours * wage * (1 + s.payroll_burden)
    travel = job.miles * s.cost_per_mile
    direct = labor + job.supplies + travel + job.other_direct
    overhead = s.monthly_overhead / s.jobs_per_month if s.jobs_per_month > 0 else 0.0
    total_cost = direct + overhead

    denominator = 1 - margin - s.card_fee * (1 + tax)
    if denominator <= 0:
        raise PricingError("target margin + card fees must be below 100%")
    raw_price = total_cost / denominator
    if total_cost <= 0 or hours <= 0:
        price = 0.0  # empty form -> no price (the workbook shows $0.00)
    else:
        price = max(s.minimum_price, round_up(raw_price, s.rounding))

    freq_disc = s.frequencies[job.frequency][0]
    total_disc = 1 - (1 - freq_disc) * (1 - job.extra_discount)
    regular_price = math.ceil(round(price / (1 - total_disc), 9)) if total_disc < 1 else price

    def pct(x: float) -> float:
        return x / price if price > 0 else 0.0

    sales_tax = price * tax
    customer_total = price + sales_tax
    fee = customer_total * s.card_fee
    gross_profit = price - (labor + job.supplies)
    contribution = price - (direct + fee)
    net_profit = contribution - overhead

    return {
        "labor_hours": hours,
        "onsite_hours": hours / job.crew,
        "labor_cost": labor,
        "supplies": job.supplies,
        "travel_cost": travel,
        "other_direct": job.other_direct,
        "direct_cost": direct,
        "overhead": overhead,
        "total_cost": total_cost,
        "raw_price": raw_price,
        "price": price,
        "total_discount": total_disc,
        "regular_price": regular_price,
        "discount_amount": regular_price - price,
        "sales_tax": sales_tax,
        "customer_total": customer_total,
        "card_fee": fee,
        "gross_profit": gross_profit,
        "gross_margin": pct(gross_profit),
        "contribution": contribution,
        "contribution_margin": pct(contribution),
        "net_profit": net_profit,
        "net_margin": pct(net_profit),
        "markup_on_cost": net_profit / total_cost if total_cost else 0.0,
        "price_per_labor_hour": price / hours if hours else 0.0,
        "price_per_sqft": price / job.sqft if job.sqft else 0.0,
    }


def check_price(job: Job, s: Settings, planned_price: float) -> dict:
    """Profit at a price the owner is considering (the 'Check my price' box)."""
    q = quote(job, s)
    tax = s.sales_tax if job.tax_override is None else job.tax_override
    fee = planned_price * (1 + tax) * s.card_fee
    net = planned_price - q["total_cost"] - fee
    return {
        "net_profit": net,
        "net_margin": net / planned_price if planned_price else 0.0,
        "loses_money": net < 0,
    }


def markup_to_margin(markup: float) -> float:
    return markup / (1 + markup)


def margin_to_markup(margin: float) -> float:
    if margin >= 1:
        raise PricingError("margin must be below 100%")
    return margin / (1 - margin)


# --- Premium planners ------------------------------------------------------

def break_even(fixed_costs: float, owner_pay: float, avg_price: float,
               variable_cost_pct: float) -> dict:
    contribution = avg_price * (1 - variable_cost_pct)
    if contribution <= 0:
        raise PricingError("variable costs eat the whole price")
    jobs_be = fixed_costs / contribution
    jobs_goal = (fixed_costs + owner_pay) / contribution
    return {
        "contribution_per_job": contribution,
        "break_even_jobs": jobs_be,
        "goal_jobs": jobs_goal,
        "goal_jobs_rounded": math.ceil(round(jobs_goal, 9)),
        "goal_revenue": math.ceil(round(jobs_goal, 9)) * avg_price,
    }


def commercial_bid(sqft: float, sqft_per_hour: float, visits_per_week: float,
                   wage: float, burden: float, supplies_per_visit: float,
                   overhead_per_month: float, margin: float, card_fee: float,
                   weeks_per_month: float = 52 / 12) -> dict:
    hours_per_visit = sqft / sqft_per_hour
    visits_month = visits_per_week * weeks_per_month
    labor_month = hours_per_visit * visits_month * wage * (1 + burden)
    supplies_month = supplies_per_visit * visits_month
    cost_month = labor_month + supplies_month + overhead_per_month
    denominator = 1 - margin - card_fee
    if denominator <= 0:
        raise PricingError("target margin + card fees must be below 100%")
    monthly_price = cost_month / denominator
    return {
        "hours_per_visit": hours_per_visit,
        "visits_per_month": visits_month,
        "labor_month": labor_month,
        "cost_month": cost_month,
        "monthly_price": monthly_price,
        "price_per_visit": monthly_price / visits_month,
        "price_per_sqft_month": monthly_price / sqft,
    }


def crew_cost(wage: float, burden: float, paid_hours_week: float,
              utilization: float, margin: float) -> dict:
    if not 0 < utilization <= 1:
        raise PricingError("utilization must be between 0% and 100%")
    loaded = wage * (1 + burden)
    billable = paid_hours_week * utilization
    cost_per_billable = loaded * paid_hours_week / billable
    return {
        "loaded_hourly": loaded,
        "weekly_cost": loaded * paid_hours_week,
        "billable_hours_week": billable,
        "cost_per_billable_hour": cost_per_billable,
        "min_rate_for_margin": cost_per_billable / (1 - margin),
    }
