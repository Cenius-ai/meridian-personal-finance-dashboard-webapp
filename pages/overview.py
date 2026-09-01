"""Overview — monthly spending chart, KPI strip, recent activity."""

from __future__ import annotations

import logging

from dash import Input, Output, callback, dcc, html, register_page

from components import charts
from components.common import empty_panel, error_panel, kpi_cell, section_header
from components.table import transactions_table
from data import repository

log = logging.getLogger("meridian.overview")

register_page(__name__, path="/overview", name="Overview", title="Overview")

MONTH_OPTIONS = [{"label": m, "value": m} for m in repository.available_months()]
DEFAULT_MONTH = MONTH_OPTIONS[0]["value"]  # 2024-06, the latest full month

layout = html.Div(
    [
        html.Div(
            [
                html.Div(
                    [
                        html.H1("Overview", className="page-title"),
                        html.P(
                            "Monthly spending by category, with your latest activity.",
                            className="page-subtitle",
                        ),
                    ],
                    className="page-heading",
                ),
                html.Div(
                    [
                        html.Label("Month", className="control-label", htmlFor="month-selector"),
                        dcc.Dropdown(
                            id="month-selector",
                            options=MONTH_OPTIONS,
                            value=DEFAULT_MONTH,
                            clearable=False,
                            className="month-selector",
                        ),
                    ],
                    className="page-control",
                ),
            ],
            className="page-header",
        ),
        dcc.Loading(
            html.Div(id="overview-content"),
            type="circle",
            color="#ed7940",
            className="loading-wrap",
        ),
    ],
    className="page",
)


def _populated(spending: list[dict], recent: list[dict], month: str) -> list:
    total = sum(r["total_cents"] for r in spending)
    count = sum(r["count"] for r in spending)
    average = total // count if count else 0
    top_category = spending[0]["category"] if spending else "—"

    kpis = html.Div(
        [
            kpi_cell("Total spend", repository.format_cents(total), month, accent=True),
            kpi_cell("Transactions", f"{count:,}", "in selected month"),
            kpi_cell("Average", repository.format_cents(average), "per transaction"),
            kpi_cell("Top category", top_category, "largest share"),
        ],
        className="kpi-strip",
    )

    chart_card = html.Section(
        [
            section_header("Spending by category", month),
            dcc.Graph(
                figure=charts.spending_bar_figure(spending),
                config={"displayModeBar": False, "responsive": True},
                className="chart",
            ),
        ],
        className="card chart-card",
    )

    recent_card = html.Section(
        [
            section_header(
                "Recent transactions",
                month,
                control=html.A("View all", href="/transactions", className="text-link"),
            ),
            transactions_table(recent, page_size=8, table_id="overview-recent-table", max_height="420px"),
        ],
        className="card recent-card",
    )

    return [
        kpis,
        html.Div([chart_card, recent_card], className="overview-grid"),
    ]


@callback(
    Output("overview-content", "children"),
    Input("month-selector", "value"),
)
def render_overview(month: str | None):
    month = month or DEFAULT_MONTH
    try:
        spending = repository.spending_by_category(month)
        recent = repository.list_transactions(month=month, sort_by="date", sort_order="desc")["data"][:8]

        if not spending:
            return empty_panel(
                "No transactions this month",
                "There are no recorded expenses for this month. Choose a different month from the selector above.",
            )

        return _populated(spending, recent, month)
    except Exception:
        log.exception("overview render failed for month %s", month)
        return error_panel("/overview", "Could not load the overview.")
