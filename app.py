"""Meridian — a local-first personal finance dashboard built with Plotly Dash.

Multi-page shell via ``dash.page_registry``, JSON endpoints mounted on the
bundled Flask server, and a committed dark fintech visual identity.

Run::

    python3 app.py

The server binds 0.0.0.0 and honours the ``PORT`` environment variable with
Dash's conventional default (8050) as the fallback.
"""

from __future__ import annotations

import logging
import os

import dash
from dash import Dash, Input, Output, dcc, html, page_container

import api
from components.common import demo_badge

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
log = logging.getLogger("meridian")

app = Dash(
    __name__,
    use_pages=True,
    pages_folder="pages",
    suppress_callback_exceptions=True,
    title="Meridian",
    update_title=None,
)
server = app.server

# Dev-only fallback keeps the app bootable with no environment configured; no
# real credential lives in source. There is no auth in this demo app.
server.secret_key = os.environ.get("SECRET_KEY") or "cenius-dev-8f3a1c7e5d2b9a04"

api.register(server)

NAV_ITEMS = [
    {"name": "Overview", "path": "/overview", "id": "nav-overview"},
    {"name": "Transactions", "path": "/transactions", "id": "nav-transactions"},
    {"name": "Categories", "path": "/categories", "id": "nav-categories"},
]

app.index_string = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{%title%}</title>
    <link rel="icon" type="image/svg+xml" href="/assets/favicon.svg" />
    {%css%}
</head>
<body>
{%app_entry%}
<footer>
{%config%}
{%scripts%}
{%renderer%}
</footer>
</body>
</html>"""


def _build_nav() -> html.Nav:
    links = [
        html.A(item["name"], href=item["path"], id=item["id"], className="nav-link")
        for item in NAV_ITEMS
    ]
    return html.Nav(
        [
            html.Button(
                [
                    html.Span(className="nav-toggle-bar"),
                    html.Span(className="nav-toggle-bar"),
                    html.Span(className="nav-toggle-bar"),
                ],
                id="nav-toggle-button",
                className="nav-toggle",
                type="button",
                **{"aria-label": "Toggle navigation", "aria-expanded": "false"},
            ),
            html.Div(links, className="nav-links"),
        ],
        className="site-nav",
        id="site-nav",
    )


app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        dcc.Store(id="page-title", data=None),
        dcc.Store(id="nav-open-state", data=False),
        html.Header(
            html.Div(
                [
                    html.A("Meridian", href="/overview", className="brand"),
                    demo_badge(),
                    _build_nav(),
                ],
                className="header-inner",
            ),
            className="site-header",
        ),
        html.Main(page_container, className="app-main"),
        html.Footer(
            html.Div(
                [
                    html.Span("Meridian — local-first personal finance"),
                    html.Span("Read-only seeded data · no outbound network calls"),
                ],
                className="footer-inner",
            ),
            className="site-footer",
        ),
    ],
    className="app-shell",
)


@app.callback(
    Output("url", "pathname"),
    Input("url", "pathname"),
)
def redirect_root(pathname: str | None):
    """Redirect the root URL to the main dashboard view."""
    if pathname in (None, "", "/"):
        return "/overview"
    return dash.no_update


@app.callback(
    Output("nav-overview", "className"),
    Output("nav-transactions", "className"),
    Output("nav-categories", "className"),
    Input("url", "pathname"),
)
def highlight_active_nav(pathname: str | None):
    active = pathname or "/overview"
    return tuple(
        "nav-link active" if active == item["path"] else "nav-link" for item in NAV_ITEMS
    )


app.clientside_callback(
    """
    function(n_clicks) {
        if (n_clicks === undefined || n_clicks === null) {
            return window.dash_clientside.no_update;
        }
        const nav = document.getElementById('site-nav');
        const btn = document.getElementById('nav-toggle-button');
        if (nav) {
            nav.classList.toggle('nav-open');
            const open = nav.classList.contains('nav-open');
            if (btn) { btn.setAttribute('aria-expanded', open ? 'true' : 'false'); }
        }
        return window.dash_clientside.no_update;
    }
    """,
    Output("nav-open-state", "data"),
    Input("nav-toggle-button", "n_clicks"),
)


app.clientside_callback(
    """
    function(pathname) {
        const titles = {
            '/overview': 'Overview · Meridian',
            '/transactions': 'Transactions · Meridian',
            '/categories': 'Categories · Meridian'
        };
        document.title = titles[pathname] || 'Meridian';
        return window.dash_clientside.no_update;
    }
    """,
    Output("page-title", "data"),
    Input("url", "pathname"),
)


@server.after_request
def add_security_headers(response):
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault(
        "Content-Security-Policy",
        "default-src 'self'; script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; img-src 'self' data:; "
        "font-src 'self'; connect-src 'self'",
    )
    return response


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8050"))
    log.info("listening on 0.0.0.0:%s", port)
    app.run(host="0.0.0.0", port=port, debug=False)
