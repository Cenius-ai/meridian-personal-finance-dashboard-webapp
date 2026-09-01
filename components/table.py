"""Dash DataTable builder with the Meridian dark theme applied."""

from __future__ import annotations

from dash import dash_table
from dash.dash_table import FormatTemplate

from data.catalog import CATEGORIES

# Native sortable columns; amounts arrive as dollars for display-only sorting
# (the authoritative integer cents stay in the API and CSV).
COLUMNS = [
    {"name": "Date", "id": "date", "type": "text"},
    {"name": "Merchant", "id": "merchant", "type": "text"},
    {"name": "Category", "id": "category", "type": "text"},
    {"name": "Account", "id": "account", "type": "text"},
    {"name": "Amount", "id": "amount", "type": "numeric", "format": FormatTemplate.money(2)},
]

_STYLE_HEADER = {
    "backgroundColor": "#15171c",
    "color": "#9b9fa5",
    "fontWeight": "700",
    "fontSize": "12px",
    "textTransform": "uppercase",
    "letterSpacing": "0.06em",
    "border": "none",
    "borderBottom": "1px solid #2b2e33",
    "padding": "11px 12px",
}

_STYLE_CELL = {
    "backgroundColor": "#15171c",
    "color": "#eef0f4",
    "fontSize": "14px",
    "border": "none",
    "borderBottom": "1px solid rgba(255,255,255,0.05)",
    "padding": "11px 12px",
    "minWidth": "0",
}


def transaction_row(record: dict) -> dict:
    """Map an API record into the DataTable row shape."""
    return {
        "id": record["id"],
        "date": record["date"],
        "merchant": record["merchant"],
        "category": record["category"],
        "account": record["account"],
        # Display-only dollar value for native numeric sorting.
        "amount": round(record["amount_cents"] / 100, 2),
        "notes": record["notes"],
    }


def _category_highlights() -> list[dict]:
    """Color the Category cell with its own category hue."""
    rules = []
    for category in CATEGORIES:
        rules.append(
            {
                "if": {
                    "column_id": "category",
                    "filter_query": f'{{category}} eq "{category["name"]}"',
                },
                "color": category["color"],
                "fontWeight": "600",
            }
        )
    return rules


def transactions_table(
    records: list[dict],
    page_size: int = 25,
    max_height: str = "620px",
    table_id: str = "transactions-data-table",
) -> dash_table.DataTable:
    """Render a themed, sortable, paginated transactions table."""
    data = [transaction_row(r) for r in records]
    tooltips = [
        {"merchant": {"value": row["notes"], "type": "text"}} if row.get("notes") else {}
        for row in data
    ]

    return dash_table.DataTable(
        id=table_id,
        columns=COLUMNS,
        data=data,
        page_action="native",
        page_size=page_size,
        sort_action="native",
        sort_mode="single",
        tooltip_header={"merchant": "Notes"},
        tooltip_data=tooltips,
        style_table={"overflowX": "auto", "minWidth": "100%", "maxHeight": max_height},
        style_header=_STYLE_HEADER,
        style_cell=_STYLE_CELL,
        style_data={
            "whiteSpace": "normal",
            "height": "auto",
            "maxWidth": "340px",
            "overflow": "hidden",
            "textOverflow": "ellipsis",
        },
        style_header_conditional=[{"if": {"column_id": "amount"}, "textAlign": "right"}],
        style_cell_conditional=[
            {"if": {"column_id": "amount"}, "textAlign": "right", "fontVariantNumeric": "tabular-nums"},
            {"if": {"column_id": "date"}, "fontVariantNumeric": "tabular-nums"},
        ],
        style_data_conditional=_category_highlights(),
        css=[
            {
                "selector": ".dash-table-container .dash-spreadsheet-container .dash-spreadsheet-inner table",
                "rule": "font-family: 'Public Sans', sans-serif;",
            },
            {
                "selector": ".dash-table-container .dash-spreadsheet-container .dash-spreadsheet-inner td",
                "rule": "min-width: 0px !important;",
            },
            {
                "selector": ".dash-table-container .dash-spreadsheet-container .dash-spreadsheet-inner tr:hover td",
                "rule": "background-color: #1c1c21 !important;",
            },
        ],
        style_as_list_view=True,
        virtualization=False,
    )
