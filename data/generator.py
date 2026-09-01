"""Deterministic demo transaction generator.

Produces ``demo_transactions.csv``: exactly 600 expenses across the twelve
months from 2023-07 through 2024-06 and the eight seeded categories. Every
amount is stored as a positive integer count of US cents — no floats touch
money in this project.

Run from the project root:

    python3 -m data.generator

The output is fully reproducible for a fixed seed, so re-running is safe and
idempotent (it simply rewrites the same file).
"""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

import numpy as np

from .catalog import CATEGORIES

SEED = 20240612
MONTHS = [date(2023, 7, 1), date(2024, 6, 1)]
OUT_PATH = Path(__file__).with_name("demo_transactions.csv")

# Category -> (merchants, amount band in cents). Multiple bands are used for
# merchants that genuinely have different price ranges (a rent check vs. an
# HOA fee), which keeps the seed varied rather than uniformly random.
CATEGORY_MERCHANTS = {
    "Food": [
        "Whole Foods Market", "Trader Joe's", "Blue Bottle Coffee", "Chipotle",
        "Seamless", "Sweetgreen", "Levain Bakery", "Corner Deli", "Shake Shack",
        "Local Farmers Market",
    ],
    "Housing": ["Meridian Property Mgmt", "Harbor Rentals", "Eastside Apartments", "Homeshield Insurance"],
    "Transportation": ["Shell", "Metro Transit", "Uber", "Lyft", "ParkMobile", "Zipcar", "Exxon"],
    "Entertainment": ["Netflix", "AMC Theatres", "Spotify", "Steam", "Live Nation", "Powell's Books"],
    "Utilities": ["ConEdison", "Comcast", "Verizon Wireless", "City Water Board", "Green Mountain Energy"],
    "Shopping": ["Amazon", "Target", "Uniqlo", "IKEA", "Best Buy", "Sephora", "REI"],
    "Healthcare": ["CVS Pharmacy", "CityMed Urgent Care", "Dental Studio", "Optical Center", "Wellness Pharmacy"],
    "Travel": ["Delta Air Lines", "Marriott", "Airbnb", "Amtrak", "Hertz", "Airport Parking"],
}

# (minimum cents, maximum cents) inclusive. Housing carries the big-ticket
# rent check; Travel carries flights; Food mixes a $4 coffee with a $160 stock-up.
AMOUNT_BANDS = {
    "Food": [(450, 1400), (1800, 9000), (4500, 16000)],
    "Housing": [(5000, 12000), (155000, 195000)],
    "Transportation": [(250, 600), (1200, 4500), (2500, 8000), (300, 2200)],
    "Entertainment": [(899, 2100), (1200, 6000), (2000, 7000), (3500, 12000)],
    "Utilities": [(3000, 7000), (5000, 9500), (6500, 9000), (6000, 16000)],
    "Shopping": [(1500, 35000)],
    "Healthcare": [(1200, 8000), (8000, 32000), (9000, 28000), (6000, 20000)],
    "Travel": [(1200, 3500), (2500, 12000), (7000, 25000), (9000, 45000), (12000, 90000)],
}

# Counts per month per category, summing to exactly 50 rows/month -> 600 rows.
MONTHLY_COUNTS = {
    "Food": 14,
    "Housing": 2,
    "Transportation": 8,
    "Entertainment": 6,
    "Utilities": 4,
    "Shopping": 6,
    "Healthcare": 4,
    "Travel": 6,
}

ACCOUNTS = ["Everyday Checking", "Sapphire Card", "Amex Platinum", "High-Yield Savings"]
METHODS = ["Debit Card", "Credit Card", "ACH Transfer", "Cash"]

NOTES = [
    "",
    "",
    "",
    "",
    "",
    "",
    "Weekly groceries",
    "Split with Maya",
    "Reimbursed by work",
    "Monthly subscription",
    "Date night",
    "Family visit",
    "Home office",
    "Gift for Sam",
    "Renewal",
]


def _month_iter():
    """Yield each month start date from 2023-07 through 2024-06."""
    current = MONTHS[0]
    end = MONTHS[1]
    while current <= end:
        yield current
        if current.month == 12:
            current = date(current.year + 1, 1, 1)
        else:
            current = date(current.year, current.month + 1, 1)


def _category_color_map():
    return {c["name"]: c["color"] for c in CATEGORIES}


def generate() -> list[dict]:
    """Generate the full deterministic transaction list (already date-sorted)."""
    rng = np.random.default_rng(SEED)
    rows: list[dict] = []
    next_id = 1

    color_map = _category_color_map()

    for month_start in _month_iter():
        month_rows: list[dict] = []
        for category_name, count in MONTHLY_COUNTS.items():
            merchants = CATEGORY_MERCHANTS[category_name]
            bands = AMOUNT_BANDS[category_name]
            for _ in range(count):
                merchant = str(rng.choice(merchants))
                low, high = bands[int(rng.integers(0, len(bands)))]
                amount_cents = int(rng.integers(low, high + 1))
                day = int(rng.integers(1, 29))  # 1..28 keeps every row inside its month
                txn_date = date(month_start.year, month_start.month, day)

                note = str(rng.choice(NOTES))
                # Make sure the seeded note pool is not all-empty so the data
                # feels real; about a third of rows carry a note.
                if note == "" and int(rng.integers(0, 3)) == 0:
                    note = "Split payment"

                month_rows.append(
                    {
                        "id": next_id,
                        "date": txn_date.isoformat(),
                        "merchant": merchant,
                        "category": category_name,
                        "category_color": color_map[category_name],
                        "account": str(rng.choice(ACCOUNTS)),
                        "method": str(rng.choice(METHODS)),
                        "amount_cents": amount_cents,
                        "currency": "USD",
                        "notes": note,
                    }
                )
                next_id += 1

        # Keep each month internally ordered by date so the CSV reads naturally.
        month_rows.sort(key=lambda r: (r["date"], r["id"]))
        rows.extend(month_rows)

    return rows


def write_csv(rows: list[dict], path: Path = OUT_PATH) -> None:
    """Write rows to the CSV file using a stable column order."""
    columns = [
        "id",
        "date",
        "merchant",
        "category",
        "category_color",
        "account",
        "method",
        "amount_cents",
        "currency",
        "notes",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    rows = generate()
    write_csv(rows)
    print(f"Wrote {len(rows)} transactions to {OUT_PATH}")


if __name__ == "__main__":
    main()
