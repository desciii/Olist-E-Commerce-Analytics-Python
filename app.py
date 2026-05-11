import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
from dash_iconify import DashIconify

from theme import C
from pages.overview import page_overview
from pages.delivery import page_delivery
from pages.reviews  import page_reviews
from pages.payments import page_payments
from pages.predictions import page_predictions
from pages.about    import page_about
from dash import clientside_callback


# ── App init ───────────────────────────────────────────────────────────────────
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600"
        "&family=Syne:wght@700;800&display=swap",
    ],
    title="Olist E-Commerce Analytics",
    suppress_callback_exceptions=True,
)
server = app.server

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            *, *::before, *::after { box-sizing: border-box; }
            html, body {
                margin: 0 !important;
                padding: 0 !important;
                overflow-x: hidden;
                background: ''' + C["bg"] + ''';
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# ── Nav items ──────────────────────────────────────────────────────────────────
NAV_ITEMS = [
    ("lucide:layout-dashboard", " Overview",    "overview"),
    ("lucide:truck",            " Delivery",    "delivery"),
    ("lucide:star",             " Reviews",     "reviews"),
    ("lucide:credit-card",      " Payments",    "payments"),
    ("lucide:sparkles",         " Predictions", "predictions"),
    ("lucide:info",             " About",       "about"),
]

# ── Sidebar ────────────────────────────────────────────────────────────────────
sidebar = html.Div([

    # Logo
    html.Div([
        html.Div("◈", style={
            "fontSize": "24px",
            "background": "linear-gradient(135deg, #8b5cf6, #6366f1)",
            "WebkitBackgroundClip": "text",
            "WebkitTextFillColor": "transparent",
            "lineHeight": "1",
            "minWidth": "24px",
        }),
        html.Div([
            html.H2("Olist", style={
                "color": "#f9fafb",
                "fontFamily": "'Syne', sans-serif",
                "fontWeight": "800",
                "margin": "0",
                "fontSize": "20px",
                "letterSpacing": "-0.5px",
                "lineHeight": "1.1",
            }),
            html.P("E-Commerce Analytics", style={
                "color": "#4b5563",
                "fontSize": "9.5px",
                "margin": "0",
                "letterSpacing": "2px",
                "textTransform": "uppercase",
                "fontFamily": "'DM Sans', sans-serif",
            }),
        ], className="logo-text"),
    ], className="logo-wrapper", style={
        "display": "flex",
        "alignItems": "center",
        "gap": "10px",
        "marginBottom": "32px",
        "paddingLeft": "4px",
    }),

    # Nav label
    html.P("Menu", className="sidebar-eyebrow"),

    # Nav buttons
    html.Div(
        [
            html.Button(
                [
                    DashIconify(
                        icon=icon,
                        width=18,
                        height=18,
                        className="nav-icon",
                    ),
                    html.Span(label, className="nav-label"),
                ],
                id=f"btn-{tid}",
                n_clicks=0,
                className="nav-btn",
                **{"data-label": label},
            )
            for icon, label, tid in NAV_ITEMS
        ],
        className="nav-buttons"
    ),

    # Footer
    html.Div([
        html.Div(className="sidebar-divider"),
        html.P("Dataset", className="sidebar-eyebrow"),
        html.A(
            "↗ Olist on Kaggle",
            href="https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce",
            target="_blank",
            className="sidebar-link",
            style={
                "color": "#8b5cf6",
                "fontSize": "12px",
                "textDecoration": "none",
                "padding": "0 14px",
                "display": "block",
                "fontFamily": "'DM Sans', sans-serif",
                "fontWeight": "500",
                "transition": "color 0.15s ease",
            },
        ),
    ], className="sidebar-footer", style={
        "marginTop": "auto",
    }),

], className="sidebar", style={
    "width": "210px",
    "minHeight": "100vh",
    "background": "linear-gradient(180deg, #111318 0%, #0d0f14 100%)",
    "borderRight": "1px solid rgba(255,255,255,0.06)",
    "padding": "28px 16px",
    "position": "fixed",
    "top": "0", "left": "0",
    "zIndex": "100",
    "boxShadow": "4px 0 24px rgba(0,0,0,0.35)",
    "display": "flex",
    "flexDirection": "column",
    "overflowY": "auto",
    "overflowX": "hidden",
})

# ── App layout ─────────────────────────────────────────────────────────────────
app.layout = html.Div([
    sidebar,
    html.Div(id="page-content", className="page-content", style={
        "marginLeft": "210px",
        "padding": "36px 40px",
        "minHeight": "100vh",
        "background": C["bg"],
        "fontFamily": "'DM Sans', sans-serif",
        "color": C["text"],
    }),
    dcc.Store(id="active-tab", data="overview"),
], style={
    "background": C["bg"],
    "margin": "0",
    "padding": "0",
    "minHeight": "100vh",
    "width": "100%",
})

dcc.Store(id="screen-size"),
dcc.Interval(id="screen-interval", interval=1000, n_intervals=0),

# ── Callbacks ──────────────────────────────────────────────────────────────────
@app.callback(
    Output("active-tab", "data"),
    [Input(f"btn-{tid}", "n_clicks") for _, _, tid in NAV_ITEMS],
    prevent_initial_call=True,
)
def switch_tab(*args):
    ctx = dash.callback_context
    if not ctx.triggered:
        return "overview"
    return ctx.triggered[0]["prop_id"].split(".")[0].replace("btn-", "")


@app.callback(
    [Output(f"btn-{tid}", "className") for _, _, tid in NAV_ITEMS],
    Input("active-tab", "data"),
)
def highlight_nav(active_tab):
    return [
        "nav-btn active" if tid == active_tab else "nav-btn"
        for _, _, tid in NAV_ITEMS
    ]


clientside_callback(
    """
    function(n) {
        return window.innerWidth;
    }
    """,
    Output("screen-size", "data"),
    Input("screen-interval", "n_intervals"),
)

@app.callback(Output("page-content", "children"), Input("active-tab", "data"))
def render(tab):
    pages = {
        "overview":    page_overview,
        "delivery":    page_delivery,
        "reviews":     page_reviews,
        "payments":    page_payments,
        "predictions": page_predictions,
        "about":       page_about,
    }
    return pages.get(tab, page_overview)()


if __name__ == "__main__":
    app.run(debug=True)