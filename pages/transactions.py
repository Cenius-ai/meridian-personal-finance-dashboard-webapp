"""Transactions — searchable, filterable, sortable, paginated table."""

from __future__ import annotations

import logging

from dash import Input, Output, callback, dcc, html, register_page

from components.common import empty_panel, error_panel
from components.table import transactions_table
from data import repository

log = logging.getLogger("meridian.transactions")

register_page(__name__, path="/transactions", name="Transactions", title="Transactions")

MONTH_OPTIONS = [{"label": "All months", "value": "all"}] + [
    {"label": m, "value": m} for m in repository.available_months()
]
CATEGORY_OPTIONS = [{"label": "All categories", "value": "all"}] + [
    {"label": c["name"], "value": c["name"]} for c in repository.list_categories()
]

layout = html.Div(
    [
        html.Div(
            [
                html.Div(
                    [
                        html.H1("Transactions", className="page-title"),
                        html.P(
                            "Every expense in the seeded dataset, with search and filters.",
                            className="page-subtitle",
                        ),
                    ],
                    className="page-heading",
                ),
            ],
            className="page-header",
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Label("Search", className="control-label", htmlFor="tx-search"),
                        dcc.Input(
                            id="tx-search",
                            type="text",
                            placeholder="Search merchant or notes…",
                            className="control-input",
                            autoComplete="off",
                        ),
                    ],
                    className="control-group control-search",
                ),
                html.Div(
                    [
                        html.Label("Month", className="control-label", htmlFor="tx-month"),
                        dcc.Dropdown(
                            id="tx-month",
                            options=MONTH_OPTIONS,
                            value="all",
                            clearable=False,
                            className="control-dropdown",
                        ),
                    ],
                    className="control-group",
                ),
                html.Div(
                    [
                        html.Label("Category", className="control-label", htmlFor="tx-category"),
                        dcc.Dropdown(
                            id="tx-category",
                            options=CATEGORY_OPTIONS,
                            value="all",
                            clearable=False,
                            className="control-dropdown",
                        ),
                    ],
                    className="control-group",
                ),
                html.Button("Clear filters", id="tx-clear", n_clicks=0, className="button button-secondary"),
            ],
            className="controls-bar card",
        ),
        dcc.Loading(
            html.Div(id="tx-results"),
            type="circle",
            color="#ed7940",
            className="loading-wrap",
        ),
    ],
    className="page",
)


def _populated(records: list[dict]) -> list:
    total = len(records)
    return [
        html.Div(f"{total:,} transaction{'s' if total != 1 else ''}", className="result-count"),
        transactions_table(records, page_size=25, table_id="transactions-data-table", max_height="680px"),
    ]


@callback(
    Output("tx-results", "children"),
    Input("tx-search", "value"),
    Input("tx-month", "value"),
    Input("tx-category", "value"),
)
def render_transactions(search: str | None, month: str | None, category: str | None):
    try:
        records = repository.list_transactions(
            month=month,
            category=category,
            search=search,
            sort_by="date",
            sort_order="desc",
        )["data"]

        if not records:
            return empty_panel(
                "No matching transactions",
                "No transactions match the current search and filters. Clear the filters to see the full dataset again.",
                action_label="Clear filters",
                action_href="/transactions",
            )

        return _populated(records)
    except Exception:
        log.exception("transactions render failed")
        return error_panel("/transactions", "Could not load transactions.")


@callback(
    Output("tx-search", "value"),
    Output("tx-month", "value"),
    Output("tx-category", "value"),
    Input("tx-clear", "n_clicks"),
    prevent_initial_call=True,
)
def clear_filters(_n_clicks: int):
    return "", "all", "all"
