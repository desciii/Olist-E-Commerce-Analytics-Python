import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc

from theme import C
from pages.overview import page_overview
from pages.delivery import page_delivery
from pages.reviews  import page_reviews
from pages.payments import page_payments
from pages.about    import page_about

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

# Strip Bootstrap's default body margin/padding and scrollbar gutter
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

# ── Sidebar ────────────────────────────────────────────────────────────────────
NAV_ITEMS = [
    ("", "Overview", "overview"),
    ("", "Delivery", "delivery"),
    ("", "Reviews",  "reviews"),
    ("", "Payments", "payments"),
    ("", "About",    "about"),
]

sidebar = html.Div([

    # ── Logo ───────────────────────────────────────────────────────────────────
    html.Div([
        html.Div("◈", style={
            "fontSize": "24px",
            "background": "linear-gradient(135deg, #8b5cf6, #6366f1)",
            "WebkitBackgroundClip": "text",
            "WebkitTextFillColor": "transparent",
            "lineHeight": "1",
        }),
        html.Div([
            html.H2("Olist", style={
                "color": "#f9fafb", "fontFamily": "'Syne', sans-serif",
                "fontWeight": "800", "margin": "0",
                "fontSize": "20px", "letterSpacing": "-0.5px", "lineHeight": "1.1",
            }),
            html.P("E-Commerce Analytics", style={
                "color": "#4b5563", "fontSize": "9.5px", "margin": "0",
                "letterSpacing": "2px", "textTransform": "uppercase",
                "fontFamily": "'DM Sans', sans-serif", "paddingTop": "-4px",
            }),
        ]),
    ], style={"display": "flex", "alignItems": "center", "gap": "10px", "marginBottom": "80px"}),

    # ── Nav label ──────────────────────────────────────────────────────────────
    html.P("Menu", className="sidebar-eyebrow"),

    # ── Nav buttons ───────────────────────────────────────────────────────────
    *[
        html.Button(
            [html.Span(icon, className="nav-icon"), html.Span(label)],
            id=f"btn-{tid}",
            n_clicks=0,
            className="nav-btn",
        )
        for icon, label, tid in NAV_ITEMS
    ],

    # ── Footer ─────────────────────────────────────────────────────────────────
    html.Div([
        html.Div(className="sidebar-divider"),
        html.P("Dataset", className="sidebar-eyebrow"),
        html.A(
            "↗ Olist on Kaggle",
            href="https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce",
            target="_blank",
            className="sidebar-link",
            style={
                "color": "#8b5cf6", "fontSize": "12px", "textDecoration": "none",
                "padding": "0 14px", "display": "block",
                "fontFamily": "'DM Sans', sans-serif", "fontWeight": "500",
                "transition": "color 0.15s ease",
            },
        ),
    ], style={"position": "absolute", "bottom": "24px", "left": "0", "right": "0"}),

], style={
    "width": "210px", "minHeight": "100vh",
    "background": "linear-gradient(180deg, #111318 0%, #0d0f14 100%)",
    "borderRight": "1px solid rgba(255,255,255,0.06)",
    "padding": "28px 16px",
    "position": "fixed", "top": "0", "left": "0", "zIndex": "100",
    "boxShadow": "4px 0 24px rgba(0,0,0,0.35)",
})

# ── Layout ─────────────────────────────────────────────────────────────────────
app.layout = html.Div([
    sidebar,
    html.Div(id="page-content", style={
        "marginLeft": "210px", "padding": "36px 40px",
        "minHeight": "100vh", "background": C["bg"],
        "fontFamily": "'DM Sans', sans-serif", "color": C["text"],
    }),
    dcc.Store(id="active-tab", data="overview"),
], style={
    "background": C["bg"],
    "margin": "0",
    "padding": "0",
    "minHeight": "100vh",
    "width": "100%",
})

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


@app.callback(Output("page-content", "children"), Input("active-tab", "data"))
def render(tab):
    pages = {
        "overview": page_overview,
        "delivery": page_delivery,
        "reviews":  page_reviews,
        "payments": page_payments,
        "about":    page_about,
    }
    return pages.get(tab, page_overview)()


if __name__ == "__main__":
    app.run(debug=True)