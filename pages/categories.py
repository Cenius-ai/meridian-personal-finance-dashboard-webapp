"""Categories — deep-dive into one category's 12-month trend and activity."""

from __future__ import annotations

import logging

from dash import Input, Output, callback, dcc, html, register_page

from components.common import empty_panel, error_panel, kpi_cell, section_header
from components.table import transactions_table
from components.trend import trend_line_figure
from data import repository
from data.catalog import CATEGORY_BY_NAME

log = logging.getLogger("meridian.categories")

register_page(__name__, path="/categories", name="Categories", title="Categories")

CATEGORY_OPTIONS = [
    {"label": c["name"], "value": c["name"]} for c in repository.list_categories()
]
DEFAULT_CATEGORY = CATEGORY_OPTIONS[0]["value"]  # "Food"

layout = html.Div(
    [
        html.Div(
            [
                html.Div(
                    [
                        html.H1("Categories", className="page-title"),
                        html.P(
                            "Analyze one spending category across the last twelve months.",
                            className="page-subtitle",
                        ),
                    ],
                    className="page-heading",
                ),
                html.Div(
                    [
                        html.Label("Category", className="control-label", htmlFor="category-selector"),
                        dcc.Dropdown(
                            id="category-selector",
                            options=CATEGORY_OPTIONS,
                            value=DEFAULT_CATEGORY,
                            clearable=False,
                            className="category-selector",
                        ),
                    ],
                    className="page-control",
                ),
            ],
            className="page-header",
        ),
        dcc.Loading(
            html.Div(id="categories-content"),
            type="circle",
            color="#ed7940",
            className="loading-wrap",
        ),
    ],
    className="page",
)


def _populated(category: dict, trend: list[dict], records: list[dict]) -> list:
    total = sum(r["total_cents"] for r in trend)
    count = sum(r["count"] for r in trend)
    average = total // count if count else 0

    summary = html.Div(
        [
            kpi_cell("12-month total", repository.format_cents(total), category["description"], accent=True),
            kpi_cell("Monthly average", repository.format_cents(average), "across 12 months"),
            kpi_cell("Transactions", f"{count:,}", "in the last year"),
        ],
        className="kpi-strip kpi-strip--three",
    )

    trend_card = html.Section(
        [
            section_header("Spending trend", "last 12 months"),
            dcc.Graph(
                figure=trend_line_figure(trend, category_color=category["color"]),
                config={"displayModeBar": False, "responsive": True},
                className="chart",
            ),
        ],
        className="card trend-card",
    )

    table_card = html.Section(
        [
            section_header(f"{category['name']} transactions", "last 12 months"),
            transactions_table(records, page_size=10, table_id="category-transactions-table", max_height="520px"),
        ],
        className="card category-table-card",
    )

    return [summary, trend_card, table_card]


@callback(
    Output("categories-content", "children"),
    Input("category-selector", "value"),
)
def render_category(category_name: str | None):
    category_name = category_name or DEFAULT_CATEGORY
    try:
        category = CATEGORY_BY_NAME.get(category_name)
        trend = repository.category_trend(category_name, months=12)
        records = repository.list_transactions(
            category=category_name, sort_by="date", sort_order="desc"
        )["data"]

        if category is None:
            return empty_panel(
                "Unknown category",
                "That category is not in the seeded dataset. Choose another category above.",
            )

        if not records:
            return empty_panel(
                "No transactions for this category",
                "This category has no recorded transactions. Choose another category above.",
            )

        return _populated(category, trend, records)
    except Exception:
        log.exception("category render failed for %s", category_name)
        return error_panel("/categories", "Could not load this category.")
