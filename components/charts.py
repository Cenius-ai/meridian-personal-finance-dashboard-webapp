"""Plotly chart builders for the Overview page."""

from __future__ import annotations

import plotly.graph_objects as go

from data.repository import format_cents

# Shared dark-theme axes. Hex/rgb only — Plotly canvases do not parse oklch().
DARK_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Public Sans, sans-serif", color="#eef0f4", size=13),
    margin=dict(l=16, r=16, t=36, b=16),
    xaxis=dict(
        gridcolor="rgba(255,255,255,0.07)",
        zerolinecolor="rgba(255,255,255,0.12)",
        linecolor="rgba(255,255,255,0.12)",
        tickfont=dict(color="#9b9fa5"),
        showgrid=True,
    ),
    yaxis=dict(
        gridcolor="rgba(255,255,255,0.07)",
        zerolinecolor="rgba(255,255,255,0.12)",
        linecolor="rgba(255,255,255,0.12)",
        tickfont=dict(color="#9b9fa5"),
        showgrid=False,
    ),
)


def _spending_ticks(max_cents: int) -> tuple[list[int], list[str]]:
    """Return dollar-denominated axis ticks computed from integer cents."""
    if max_cents <= 0:
        return [0], [format_cents(0)]
    step = max(100, round(max_cents / 4 / 100) * 100)
    vals = list(range(0, max_cents, step))
    if vals[-1] != max_cents:
        vals.append(max_cents)
    return vals, [format_cents(v) for v in vals]


def spending_bar_figure(rows: list[dict]) -> go.Figure:
    """Horizontal bar chart of monthly spend by category.

    ``rows`` must already be sorted descending by total_cents.
    """
    ordered = list(reversed(rows))  # plotly draws the first row at the bottom
    categories = [r["category"] for r in ordered]
    totals = [r["total_cents"] for r in ordered]
    colors = [r["color"] for r in ordered]
    counts = [str(r["count"]) for r in ordered]
    averages = [format_cents(r["average_cents"]) for r in ordered]
    labels = [format_cents(t) for t in totals]
    custom = list(zip(counts, averages))

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=totals,
            y=categories,
            orientation="h",
            marker=dict(color=colors, line=dict(width=0)),
            text=labels,
            textposition="outside",
            cliponaxis=False,
            textfont=dict(color="#eef0f4", size=13),
            customdata=custom,
            hovertemplate=(
                "%{y}<br>"
                "<b>%{text}</b><br>"
                "%{customdata[0]} transactions · avg %{customdata[1]}"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        DARK_LAYOUT,
        height=420,
        bargap=0.32,
        hoverlabel=dict(bgcolor="#1c1c21", bordercolor="rgba(255,255,255,0.12)", font=dict(color="#eef0f4")),
        showlegend=False,
    )

    max_total = max(totals) if totals else 0
    tick_vals, tick_text = _spending_ticks(max_total)
    fig.update_xaxes(tickvals=tick_vals, ticktext=tick_text, range=[0, int(max_total * 1.24)] if max_total else [0, 1])
    fig.update_yaxes(automargin=True)
    return fig
