"""Small shared UI pieces used across all three pages."""

from __future__ import annotations

from dash import html


def demo_badge() -> html.Div:
    """The live, pulsing demo-data badge shown in the shared shell."""
    return html.Div(
        [
            html.Span(className="demo-dot"),
            html.Span("Demo data"),
        ],
        className="demo-badge",
        title="Read-only seeded demo dataset",
    )


def kpi_cell(label: str, value: str, sub: str, accent: bool = False) -> html.Div:
    """A single dense statistic cell for the KPI strip."""
    return html.Div(
        [
            html.Span(label, className="kpi-label"),
            html.Div(value, className="kpi-value" + (" kpi-accent" if accent else "")),
            html.Div(sub, className="kpi-sub"),
        ],
        className="kpi-cell",
    )


def section_header(title: str, period: str | None = None, control=None) -> html.Div:
    """Consistent card header: title, optional period, optional control."""
    children = [
        html.Div(
            [
                html.H2(title, className="card-title"),
                html.Span(period, className="card-period") if period else None,
            ],
            className="card-heading",
        )
    ]
    if control is not None:
        children.append(html.Div(control, className="card-control"))
    return html.Div(children, className="card-header")


def error_panel(retry_href: str, message: str = "We couldn't load this data.") -> html.Div:
    """Designed error state with an inline retry link that re-runs the call."""
    return html.Div(
        [
            html.Div("Data unavailable", className="state-title"),
            html.P(f"{message} The local seed file may be missing. Try again.", className="state-copy"),
            html.A("Retry", href=retry_href, className="button button-secondary"),
        ],
        className="state-card state-error",
        role="alert",
    )


def empty_panel(
    title: str,
    message: str,
    action_label: str | None = None,
    action_href: str | None = None,
) -> html.Div:
    """Designed empty state with an optional primary action."""
    action = None
    if action_label:
        if action_href:
            action = html.A(action_label, href=action_href, className="button button-primary")
        else:
            action = html.Button(action_label, className="button button-primary")

    return html.Div(
        [
            html.Div(title, className="state-title"),
            html.P(message, className="state-copy"),
            action,
        ],
        className="state-card state-empty",
    )
