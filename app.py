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
        "https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;700"
        "&family=Space+Grotesk:wght@600;700&display=swap",
    ],
    title="Olist E-Commerce Analytics",
)
server = app.server  # required for Render deployment

# ── Sidebar ────────────────────────────────────────────────────────────────────
NAV_ITEMS = [
    ("🏠", "Overview", "overview"),
    ("📦", "Delivery", "delivery"),
    ("⭐", "Reviews",  "reviews"),
    ("💳", "Payments", "payments"),
    ("📖", "About",    "about"),
]

sidebar = html.Div([
    html.Div([
        html.Div("◈", style={"fontSize": "28px", "color": C["accent"]}),
        html.H2("Olist", style={
            "color": C["text"], "fontFamily": "'Space Grotesk'",
            "fontWeight": "700", "margin": "0", "fontSize": "22px",
        }),
        html.P("E-Commerce Analytics", style={
            "color": C["muted"], "fontSize": "11px",
            "margin": "0", "letterSpacing": "1px",
        }),
    ], style={"marginBottom": "36px"}),

    *[
        html.Button([icon, " ", label], id=f"btn-{tid}", n_clicks=0, style={
            "display": "block", "width": "100%", "textAlign": "left",
            "background": "transparent", "border": "none",
            "color": C["muted"], "padding": "10px 14px", "borderRadius": "8px",
            "fontSize": "13px", "cursor": "pointer", "marginBottom": "4px",
            "fontFamily": "'DM Sans', sans-serif",
        })
        for icon, label, tid in NAV_ITEMS
    ],

    html.Div([
        html.P("Dataset", style={
            "color": C["muted"], "fontSize": "10px",
            "textTransform": "uppercase", "letterSpacing": "1px",
        }),
        html.A("Kaggle: Olist",
               href="https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce",
               target="_blank",
               style={"color": C["accent"], "fontSize": "12px", "textDecoration": "none"}),
    ], style={"position": "absolute", "bottom": "28px", "left": "24px"}),

], style={
    "width": "200px", "minHeight": "100vh",
    "background": C["card"],
    "borderRight": f"1px solid {C['border']}",
    "padding": "28px 20px",
    "position": "fixed", "top": "0", "left": "0", "zIndex": "100",
})

# ── Layout ─────────────────────────────────────────────────────────────────────
app.layout = html.Div([
    sidebar,
    html.Div(id="page-content", style={
        "marginLeft": "200px", "padding": "36px 40px",
        "minHeight": "100vh", "background": C["bg"],
        "fontFamily": "'DM Sans', sans-serif", "color": C["text"],
    }),
    dcc.Store(id="active-tab", data="overview"),
], style={"background": C["bg"]})

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