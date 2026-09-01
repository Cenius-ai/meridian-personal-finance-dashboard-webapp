"""Read-only data access layer for the seeded transaction CSV.

The Dash callbacks and the Flask JSON endpoints both call these functions, so
there is exactly one source of truth for filtering and aggregation logic.
Money stays in integer cents everywhere until a display formatter converts it.
"""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from .catalog import CATEGORIES, CATEGORY_BY_NAME, CATEGORY_NAMES

log = logging.getLogger("meridian.repository")

CSV_PATH = Path(__file__).with_name("demo_transactions.csv")

# All of the month buckets present in the seed (deterministic, so safe to
# derive once at import time).
ALL_MONTHS = [
    "2023-07", "2023-08", "2023-09", "2023-10", "2023-11", "2023-12",
    "2024-01", "2024-02", "2024-03", "2024-04", "2024-05", "2024-06",
]

_df: pd.DataFrame | None = None


def _ensure_csv() -> None:
    """Self-heal on first use so a bare start always has seeded data."""
    if not CSV_PATH.exists():
        from .generator import generate, write_csv

        write_csv(generate())
        log.info("regenerated missing demo CSV at %s", CSV_PATH)


def _load_df() -> pd.DataFrame:
    global _df
    if _df is None:
        _ensure_csv()
        df = pd.read_csv(CSV_PATH)
        df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")
        df["month"] = df["date"].dt.strftime("%Y-%m")
        df = df.sort_values(["date", "id"], ascending=[True, True]).reset_index(drop=True)
        _df = df
    return _df


def format_cents(cents: int) -> str:
    """Format integer cents as a USD string without floating point arithmetic."""
    sign = "-" if cents < 0 else ""
    cents = abs(int(cents))
    return f"{sign}${cents // 100:,}.{cents % 100:02d}"


def list_categories() -> list[dict]:
    """Return the full category catalog (id, name, color, description)."""
    return [dict(c) for c in CATEGORIES]


def available_months() -> list[str]:
    """Return month buckets, newest first."""
    return list(reversed(ALL_MONTHS))


def _record(row: pd.Series) -> dict:
    return {
        "id": int(row["id"]),
        "date": row["date"].strftime("%Y-%m-%d"),
        "month": str(row["month"]),
        "merchant": str(row["merchant"]),
        "category": str(row["category"]),
        "category_color": str(row["category_color"]),
        "account": str(row["account"]),
        "method": str(row["method"]),
        "amount_cents": int(row["amount_cents"]),
        "amount": format_cents(int(row["amount_cents"])),
        "currency": "USD",
        "notes": "" if pd.isna(row["notes"]) else str(row["notes"]),
    }


def transactions_query(
    month: str | None = None,
    category: str | None = None,
    search: str | None = None,
    sort_by: str = "date",
    sort_order: str = "desc",
) -> pd.DataFrame:
    """Return filtered, sorted transactions as a DataFrame."""
    df = _load_df()

    if month and month != "all":
        df = df[df["month"] == month]
    if category and category != "all":
        df = df[df["category"] == category]
    if search and search.strip():
        needle = search.strip().casefold()
        haystack = df["merchant"].str.casefold()
        notes = df["notes"].fillna("").str.casefold()
        df = df[haystack.str.contains(needle, regex=False) | notes.str.contains(needle, regex=False)]

    sort_columns = {
        "date": "date",
        "amount": "amount_cents",
    }
    column = sort_columns.get(sort_by, "date")
    ascending = sort_order != "desc"
    return df.sort_values([column, "id"], ascending=[ascending, True])


def list_transactions(
    month: str | None = None,
    category: str | None = None,
    search: str | None = None,
    sort_by: str = "date",
    sort_order: str = "desc",
    page: int | None = None,
    page_size: int = 25,
) -> dict:
    """Return transactions, optionally paginated.

    When ``page`` is ``None`` the full filtered result is returned (used by the
    client-side DataTable). When a page is supplied, the API pagination shape
    is returned with metadata.
    """
    df = transactions_query(month, category, search, sort_by, sort_order)
    total = int(len(df))

    if page is None:
        records = [_record(row) for _, row in df.iterrows()]
        return {"data": records, "page": {"total": total, "page": 1, "page_size": total or 1, "total_pages": 1}}

    page = max(1, int(page))
    page_size = max(1, min(int(page_size), 200))
    total_pages = (total + page_size - 1) // page_size
    start = (page - 1) * page_size
    page_df = df.iloc[start : start + page_size]
    records = [_record(row) for _, row in page_df.iterrows()]

    return {
        "data": records,
        "page": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages,
            "has_more": page < total_pages,
        },
    }


def spending_by_category(month: str) -> list[dict]:
    """Aggregate monthly spend per category, sorted descending by total."""
    df = transactions_query(month=month)
    if df.empty:
        return []

    grouped = (
        df.groupby("category")
        .agg(total_cents=("amount_cents", "sum"), count=("id", "count"))
        .reset_index()
    )
    grouped["average_cents"] = (grouped["total_cents"] / grouped["count"]).round().astype(int)
    grouped = grouped.sort_values("total_cents", ascending=False)

    rows = []
    for _, row in grouped.iterrows():
        cat = CATEGORY_BY_NAME.get(row["category"], {})
        rows.append(
            {
                "category": str(row["category"]),
                "color": cat.get("color", "#ed7940"),
                "total_cents": int(row["total_cents"]),
                "count": int(row["count"]),
                "average_cents": int(row["average_cents"]),
            }
        )
    return rows


def category_trend(category: str, months: int = 12) -> list[dict]:
    """Monthly totals for one category, filling missing months with zero."""
    months = max(1, min(int(months), 12))
    buckets = ALL_MONTHS[-months:]  # oldest -> newest

    df = transactions_query(category=category)
    if df.empty:
        totals = {bucket: 0 for bucket in buckets}
        counts = {bucket: 0 for bucket in buckets}
    else:
        grouped = (
            df.groupby("month")
            .agg(total_cents=("amount_cents", "sum"), count=("id", "count"))
        )
        totals = {bucket: int(grouped.loc[bucket, "total_cents"]) if bucket in grouped.index else 0 for bucket in buckets}
        counts = {bucket: int(grouped.loc[bucket, "count"]) if bucket in grouped.index else 0 for bucket in buckets}

    return [
        {"month": bucket, "total_cents": totals[bucket], "count": counts[bucket]}
        for bucket in buckets
    ]
