"""Plotly trend-line builder for the Categories deep-dive page."""

from __future__ import annotations

import plotly.graph_objects as go

from components.charts import DARK_LAYOUT
from data.repository import format_cents


def _trend_ticks(max_cents: int) -> tuple[list[int], list[str]]:
    if max_cents <= 0:
        return [0], [format_cents(0)]
    step = max(100, round(max_cents / 4 / 100) * 100)
    vals = list(range(0, max_cents + step, step))
    return vals, [format_cents(v) for v in vals]


def trend_line_figure(rows: list[dict], category_color: str = "#ed7940") -> go.Figure:
    """12-month spending trend with a monthly-average reference line."""
    months = [r["month"] for r in rows]
    totals = [r["total_cents"] for r in rows]
    average = round(sum(totals) / len(totals)) if totals else 0

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=months,
            y=totals,
            mode="lines+markers",
            line=dict(color=category_color, width=3, shape="spline", smoothing=0.6),
            marker=dict(color=category_color, size=8, line=dict(color="#0a0c11", width=2)),
            fill="tozeroy",
            fillcolor="rgba(237,121,64,0.10)",
            name="Monthly total",
            customdata=[format_cents(t) for t in totals],
            hovertemplate="%{x}<br><b>%{customdata}</b><extra></extra>",
        )
    )
    fig.add_hline(
        y=average,
        line=dict(color="#9b9fa5", width=1.5, dash="dot"),
        annotation_text=f"avg {format_cents(average)}",
        annotation_position="top left",
        annotation_font=dict(color="#9b9fa5", size=12),
    )

    fig.update_layout(
        DARK_LAYOUT,
        height=360,
        hoverlabel=dict(bgcolor="#1c1c21", bordercolor="rgba(255,255,255,0.12)", font=dict(color="#eef0f4")),
        showlegend=False,
    )

    max_total = max(totals) if totals else 0
    tick_vals, tick_text = _trend_ticks(max_total)
    fig.update_yaxes(tickvals=tick_vals, ticktext=tick_text)
    fig.update_xaxes(tickangle=0)
    return fig
