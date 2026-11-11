"""Fictional sample data for the EXAMPLE workbooks.

All people, companies, phone numbers (555-01xx is reserved for fiction) and
emails (example.com is reserved by RFC 2606) are invented.
"""
import datetime as dt

D = dt.datetime

BUSINESS = {
    "name": "Brightway Cleaning Co. (example)",
    "owner": "Alex Rivera",
    "phone": "(555) 010-0100",
    "email": "hello@example.com",
    "address": "Austin, TX",
    "web": "brightway.example.com",
    "pay_methods": "Card, Zelle, Venmo or check",
}

CALC_EXAMPLE = {
    "client": "Sample: Jordan Lee", "property": "House", "service": "Deep Cleaning",
    "frequency": "One-time", "sqft": 2200, "bedrooms": 3, "bathrooms": 2, "crew": 2,
    "supplies": 18, "miles": 14, "other_direct": 0, "extra_discount": 0,
    "planned_price": 300,
}

# A..M of the Quote Table
QUOTE_ROWS = [
    ("Sample: Jordan Lee", "House", "Deep Cleaning", "One-time", 2200, 3, 2, 2, None, 18, 14, 0, 0),
    ("Sample: Priya Shah", "Apartment / Condo", "Standard Cleaning", "Every 2 weeks", 950, 2, 1, 1, None, 6, 8, 0, 0),
    ("Sample: Chen family", "House", "Recurring Cleaning", "Weekly", 2600, 4, 3, 2, None, 10, 10, 0, 0),
    ("Sample: Oakridge Realty", "Townhouse", "Move-Out Cleaning", "One-time", 1700, 3, 2.5, 2, None, 25, 20, 15, 0.1),
    ("Sample: Maple Dental", "Office", "Office Cleaning", "Weekly", 3000, 0, 2, 2, None, 12, 12, 0, 0),
    ("Sample: Ortiz home", "House", "Move-In Cleaning", "One-time", 1800, 3, 2, 2, 7.5, 20, 16, 0, 0),
]

# B..K of Clients: name, company, phone, email, address, service, frequency, price, status, notes
CLIENTS = [
    ("Jordan Lee", "", "(555) 010-0111", "jordan@example.com", "12 Elm St, Austin, TX", "Standard Cleaning", "Every 2 weeks", 165, "Active", "Dog (friendly). Key under mat."),
    ("Priya Shah", "", "(555) 010-0112", "priya@example.com", "88 Lake Ave #4, Austin, TX", "Standard Cleaning", "Every 2 weeks", 120, "Active", "Gate code 4821"),
    ("Chen family", "", "(555) 010-0113", "chen@example.com", "301 Hill Rd, Round Rock, TX", "Recurring Cleaning", "Weekly", 190, "Active", "Fragrance-free products"),
    ("Morgan Price", "", "(555) 010-0114", "morgan@example.com", "45 Pine Ct, Austin, TX", "Deep Cleaning", "Every 4 weeks", 260, "Active", ""),
    ("Sam Patel", "Oakridge Realty", "(555) 010-0115", "sam@example.com", "Various listings", "Move-Out Cleaning", "One-time", 340, "Active", "Invoice the office"),
    ("Dana Brooks", "Maple Dental", "(555) 010-0116", "office@example.com", "900 Maple Blvd, Austin, TX", "Office Cleaning", "Weekly", 210, "Active", "After 6 pm only"),
    ("Riley Ortiz", "", "(555) 010-0117", "riley@example.com", "17 Cedar Ln, Pflugerville, TX", "Move-In Cleaning", "One-time", 300, "Former", ""),
    ("Taylor Kim", "", "(555) 010-0118", "taylor@example.com", "5 Brook Dr, Austin, TX", "Standard Cleaning", "Monthly", 150, "Paused", "Traveling until spring"),
]

STAFF = ["Alex", "Maria", "Jo"]
_visits = {  # client -> (interval days, first date, price, hours, service)
    "Jordan Lee": (14, D(2026, 1, 6), 165, 4.0, "Standard Cleaning"),
    "Priya Shah": (14, D(2026, 1, 8), 120, 2.5, "Standard Cleaning"),
    "Chen family": (7, D(2026, 1, 5), 190, 5.0, "Recurring Cleaning"),
    "Morgan Price": (28, D(2026, 1, 15), 260, 7.0, "Deep Cleaning"),
    "Dana Brooks": (7, D(2026, 1, 9), 210, 4.5, "Office Cleaning"),
}
_CUTOFF = D(2026, 11, 10)


def _schedule():
    rows = []
    for client, (step, first, price, hours, svc) in _visits.items():
        d = first
        n = 0
        while d <= D(2026, 12, 18):
            n += 1
            if d <= _CUTOFF:
                status = "Cancelled" if n % 11 == 0 else "Completed"
            else:
                status = "Confirmed" if d <= D(2026, 11, 20) else "Scheduled"
            staff = STAFF[n % len(STAFF)]
            rows.append((d, dt.time(9 if n % 2 else 13, 0), client, svc, price, hours, staff, status, ""))
            d += dt.timedelta(days=step)
    rows.append((D(2026, 3, 2), dt.time(10, 0), "Sam Patel", "Move-Out Cleaning", 340, 8.0, "Alex", "Completed", "Unit 12B"))
    rows.append((D(2026, 6, 20), dt.time(10, 0), "Sam Patel", "Move-Out Cleaning", 340, 8.0, "Maria", "Completed", "Unit 3A"))
    rows.append((D(2026, 4, 11), dt.time(9, 0), "Riley Ortiz", "Move-In Cleaning", 300, 7.5, "Jo", "Completed", ""))
    rows.append((D(2026, 2, 21), dt.time(9, 0), "Taylor Kim", "Standard Cleaning", 150, 3.5, "Maria", "Completed", ""))
    rows.sort(key=lambda r: (r[0], r[1]))
    return rows


SCHEDULE = _schedule()


def _transactions():
    tx = []
    for d, _t, client, svc, price, hours, staff, status, _n in SCHEDULE:
        if status != "Completed":
            continue
        pay = "Pending" if d >= D(2026, 11, 3) else "Received"
        tx.append((d, "Cleaning revenue", f"{svc} visit", client, svc, price, pay))
    for m in range(1, 12):
        month_end = D(2026, m, 28)
        month_hours = sum(r[5] for r in SCHEDULE if r[0].month == m and r[7] == "Completed")
        wages = round(month_hours * 18, 2)
        tx += [
            (month_end, "Wages & contractor pay", "Crew pay", "", "", wages, "Paid"),
            (month_end, "Payroll taxes & workers comp", "Payroll taxes", "", "", round(wages * 0.12, 2), "Paid"),
            (D(2026, m, 3), "Cleaning supplies", "Supplies restock", "", "", 140 + (m % 3) * 25, "Paid"),
            (D(2026, m, 25), "Fuel & mileage", "Fuel", "", "", 210 + (m % 4) * 15, "Paid"),
            (D(2026, m, 1), "Insurance & bonding", "General liability + bond", "", "", 145, "Paid"),
            (D(2026, m, 1), "Phone, internet & software", "Phone + scheduling app", "", "", 65, "Paid"),
            (D(2026, m, 10), "Marketing & advertising", "Flyers / local listings", "", "", 60 if m % 2 else 0, "Paid"),
            (D(2026, m, 15), "Taxes paid / set aside", "Set aside for income tax", "", "", 450, "Paid"),
        ]
        if m in (3, 9):
            tx.append((D(2026, m, 12), "Equipment & tools", "Vacuum replacement", "", "", 289, "Paid"))
    # expenses dated after the example "today" are still unpaid
    tx = [t[:6] + ("Pending",) if t[0] > _CUTOFF and t[6] == "Paid" else t for t in tx]
    tx = [t for t in tx if t[5] != 0]
    tx.sort(key=lambda r: r[0])
    return tx


TRANSACTIONS = _transactions()

ESTIMATE = {
    "number": "EST-1042", "date": D(2026, 11, 2), "client": "Morgan Price",
    "service_date": D(2026, 11, 14), "frequency": "One-time",
    "items": [("Deep cleaning — 3 bed / 2 bath, 2,200 sq ft", 1, 365),
              ("Inside oven", 1, 35), ("Inside refrigerator", 1, 35)],
    "discount": 0.05, "tax": None,
    "notes": "Includes all supplies and equipment. Two cleaners, about 4 hours on site. "
             "Final price may change if the home's condition differs from what was described.",
}
INVOICE = {
    "number": "INV-2087", "date": D(2026, 11, 3), "client": "Dana Brooks",
    "service_date": D(2026, 10, 30), "frequency": "Weekly",
    "items": [("Weekly office cleaning — October visits", 5, 210)],
    "discount": 0, "tax": None, "paid": 630,
    "notes": "Thank you! Partial payment received 10/20.",
}

CHECKLISTS = [
    ("STANDARD CLEAN", [
        "# Kitchen", "Wipe counters and backsplash", "Clean outside of appliances", "Clean stovetop",
        "Clean microwave inside and out", "Scrub and shine sink", "Empty trash, replace liner",
        "Sweep and mop floor",
        "# Bathrooms", "Clean and disinfect toilet", "Clean tub / shower", "Clean sink and counter",
        "Clean mirrors", "Replace towels if left out", "Sweep and mop floor",
        "# Bedrooms & living areas", "Dust reachable surfaces", "Make beds (linens if left out)",
        "Dust furniture and electronics", "Vacuum carpets and rugs", "Mop hard floors", "Empty trash bins",
        "# Before leaving", "Walkthrough with checklist", "Lights off, doors locked",
    ]),
    ("DEEP CLEAN (adds)", [
        "# Everything in Standard, plus", "Baseboards hand-wiped", "Door frames and doors",
        "Light switches and outlets", "Window sills and tracks", "Ceiling fans and light fixtures",
        "Inside cabinets (if empty)", "Behind and under movable furniture", "Detailed grout scrub",
        "Vent covers dusted", "Blinds dusted",
        "# Optional add-ons (quote separately)", "Inside oven", "Inside refrigerator",
        "Interior windows", "Laundry fold", "Wall spot cleaning",
    ]),
    ("MOVE-IN / MOVE-OUT", [
        "# Kitchen", "Inside all cabinets and drawers", "Inside and behind oven / fridge (if pulled)",
        "Range hood and filter", "Dishwasher interior wipe", "Sink, faucet, disposal area",
        "# Bathrooms", "Inside vanities and medicine cabinet", "Descale shower glass and fixtures",
        "Toilet base and behind toilet", "Exhaust fan cover",
        "# Whole home", "Closets: shelves and rods", "All baseboards and doors", "Windows sills and tracks",
        "Light fixtures and switches", "Floors vacuumed and mopped", "Garage swept (if included)",
        "# Final", "Photos for the landlord / agent", "Report damage found (photos)", "Return keys",
    ]),
]
