import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
from dash_iconify import DashIconify

from theme import C
from pages.overview    import page_overview
from pages.delivery    import page_delivery
from pages.reviews     import page_reviews
from pages.payments    import page_payments
from pages.predictions import page_predictions
from pages.about       import page_about
from dash import clientside_callback


# ── App init ───────────────────────────────────────────────────────────────────
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600"
        "&family=Syne:wght@700;800"
        "&family=Space+Grotesk:wght@700;800"
        "&display=swap",
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
    ("lucide:layout-dashboard",  " Overview",    "overview"),
    ("lucide:truck",             " Delivery",    "delivery"),
    ("lucide:star",              " Reviews",     "reviews"),
    ("lucide:credit-card",       " Payments",    "payments"),
    ("lucide:trending-up-down",  " Predictions", "predictions"),
    ("lucide:info",              " About",       "about"),
]

# ── Sidebar ────────────────────────────────────────────────────────────────────
sidebar = html.Div([

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

    html.P("Menu", className="sidebar-eyebrow"),

    html.Div([
        html.Button(
            [
                DashIconify(icon=icon, width=18, height=18, className="nav-icon"),
                html.Span(label, className="nav-label"),
            ],
            id=f"btn-{tid}",
            n_clicks=0,
            className="nav-btn",
            **{"data-label": label},
        )
        for icon, label, tid in NAV_ITEMS
    ], className="nav-buttons"),

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
    ], className="sidebar-footer", style={"marginTop": "auto"}),

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

# ── Welcome modal (plain HTML, no Bootstrap JS dependency) ────────────────────
welcome_modal = html.Div([

    # Backdrop
    html.Div(id="welcome-backdrop", style={
        "position": "fixed",
        "inset": "0",
        "background": "rgba(0,0,0,0.75)",
        "zIndex": "9998",
    }),

    # Dialog
    html.Div([

        # Header
        html.Div([
            html.Div([
                html.Span("◈ ", style={
                    "background": "linear-gradient(135deg, #8b5cf6, #6366f1)",
                    "WebkitBackgroundClip": "text",
                    "WebkitTextFillColor": "transparent",
                    "fontSize": "20px",
                }),
                html.Span("Welcome to Olist Analytics", style={
                    "fontFamily": "'Space Grotesk', sans-serif",
                    "fontWeight": "700",
                    "fontSize": "18px",
                    "color": "#f9fafb",
                }),
            ], style={"display": "flex", "alignItems": "center", "gap": "6px"}),
        ], style={
            "padding": "20px 24px",
            "borderBottom": "1px solid #252b38",
        }),

        # Body
        html.Div([
            html.P(
                "This dashboard is built on the Olist Brazilian E-Commerce Public Dataset with a "
                "a real-world collection of 100,000+ orders from Brazil's largest online "
                "marketplace aggregator, spanning 2016 to 2018.",
                style={
                    "color": "#9ca3af", "fontSize": "14px",
                    "lineHeight": "1.8", "marginBottom": "14px",
                },
            ),
            html.P(
                "Explore order trends, delivery performance, customer reviews, payment insights, "
                "and machine-learning forecasts all in one place.",
                style={
                    "color": "#9ca3af", "fontSize": "14px",
                    "lineHeight": "1.8", "margin": "0",
                },
            ),
        ], style={"padding": "24px"}),

        # Footer
        html.Div([
            html.Button(
                "Get Started",
                id="welcome-close",
                n_clicks=0,
                style={
                    "padding": "10px 28px",
                    "background": "linear-gradient(135deg, #00d4aa, #00a884)",
                    "border": "none",
                    "borderRadius": "8px",
                    "color": "#0d0f14",
                    "fontWeight": "700",
                    "fontSize": "14px",
                    "cursor": "pointer",
                    "fontFamily": "'DM Sans', sans-serif",
                },
            ),
        ], style={
            "padding": "16px 24px",
            "borderTop": "1px solid #252b38",
            "display": "flex",
            "justifyContent": "flex-end",
        }),

    ], style={
        "position": "fixed",
        "top": "50%",
        "left": "50%",
        "transform": "translate(-50%, -50%)",
        "background": "#161a23",
        "border": "1px solid #252b38",
        "borderRadius": "14px",
        "width": "480px",
        "maxWidth": "90vw",
        "zIndex": "9999",
        "fontFamily": "'DM Sans', sans-serif",
        "boxShadow": "0 24px 64px rgba(0,0,0,0.6)",
    }),

], id="welcome-modal")


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
    welcome_modal,
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
    Output("welcome-modal", "style"),
    Input("welcome-close", "n_clicks"),
    prevent_initial_call=True,
)
def close_welcome(_):
    return {"display": "none"}


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

    if tab == "overview":
        from pages.overview import page_overview
        return page_overview()

    elif tab == "delivery":
        from pages.delivery import page_delivery
        return page_delivery()

    elif tab == "reviews":
        from pages.reviews import page_reviews
        return page_reviews()

    elif tab == "payments":
        from pages.payments import page_payments
        return page_payments()

    elif tab == "predictions":
        from pages.predictions import page_predictions
        return page_predictions()

    elif tab == "about":
        from pages.about import page_about
        return page_about()

    return html.Div("Page not found")


if __name__ == "__main__":
    app.run(debug=True)