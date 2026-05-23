# pages/about.py
from dash import html
from theme import C


def page_about():

    def pill(label, value, color=None):
        return html.Div([
            html.Div(value, style={
                "fontSize": "24px", "fontWeight": "700", "lineHeight": "1",
                "color": color or C["accent"], "fontFamily": "'Space Grotesk'",
                "marginBottom": "4px",
            }),
            html.Div(label, style={
                "fontSize": "11px", "color": C["muted"],
                "textTransform": "uppercase", "letterSpacing": "0.08em", "fontWeight": "600",
            }),
        ], style={
            "background": C["card"], "border": f"1px solid {C['border']}",
            "borderRadius": "10px", "padding": "14px 20px",
            "textAlign": "center", "flex": "1", "minWidth": "110px",
        })

    def card(children, style=None):
        base = {
            "background": C["card"], "border": f"1px solid {C['border']}",
            "borderRadius": "12px", "padding": "24px", "marginBottom": "16px",
        }
        return html.Div(children, style={**base, **(style or {})})

    def h(text):
        return html.H3(text, style={
            "fontFamily": "'Space Grotesk'", "fontWeight": "700",
            "fontSize": "15px", "color": C["text"],
            "marginBottom": "12px", "marginTop": "0",
            "textTransform": "uppercase", "letterSpacing": "0.06em",
        })

    def muted(text, style=None):
        return html.P(text, style={
            "color": C["muted"], "fontSize": "13.5px",
            "lineHeight": "1.75", "margin": "0", **(style or {}),
        })

    def feature_row(name, desc, color=None, last=False):
        return html.Div([
            html.Span(name, style={
                "fontWeight": "700", "color": color or C["accent"],
                "fontSize": "13px", "display": "block", "marginBottom": "2px",
            }),
            html.Span(desc, style={"color": C["muted"], "fontSize": "13px", "lineHeight": "1.6"}),
        ], style={
            "padding": "12px 0",
            **({"borderBottom": f"1px solid {C['border']}"} if not last else {}),
        })

    def member(name):
        return html.Div([
            html.Span(name, style={"color": C["text"], "fontSize": "13px"}),
            html.Div("BSIT · BTM 3B", style={
                "color": C["muted"], "fontSize": "11px", "marginTop": "2px",
            }),
        ], style={
            "padding": "10px 14px", "borderRadius": "8px",
            "border": f"1px solid {C['border']}", "marginBottom": "8px",
        })

    return html.Div([

        # ── Title ──────────────────────────────────────────────────────────────
        html.H1("About", style={
            "fontFamily": "'Space Grotesk'", "fontWeight": "700", "marginBottom": "4px",
        }),
        muted(
            "Olist E-Commerce Analytics — a business intelligence dashboard built on "
            "real-world Brazilian marketplace data.",
            style={"marginBottom": "28px"},
        ),

        # ── Stats ──────────────────────────────────────────────────────────────
        html.Div([
            pill("Orders",        "100k+"),
            pill("Period",        "2016–18",  color=C["accent2"]),
            pill("States",        "27",       color=C["accent3"]),
            pill("Categories",    "70+",      color="#4a90e2"),
            pill("Source Tables", "9",        color=C["accent"]),
        ], style={"display": "flex", "gap": "10px", "flexWrap": "wrap", "marginBottom": "16px"}),

        # ── About Olist ────────────────────────────────────────────────────────
        card([
            h("About Olist"),
            muted(
                "Olist is Brazil's largest online marketplace aggregator, connecting small "
                "businesses to major retail channels like Mercado Livre, Americanas, and Shoptime "
                "through a single platform. Founded in 2015 and headquartered in Curitiba, "
                "Olist has facilitated over 100,000 orders across all 27 Brazilian states, "
                "handling product listings, payments, customer reviews, and logistics coordination."
            ),
        ]),

        # ── Dashboard ─────────────────────────────────────────────────────────
        card([
            h("What This Dashboard Does"),
            muted(
                "This tool turns Olist's raw transactional data into actionable insights across "
                "four core business areas — operations, customer satisfaction, logistics, and payments. "
                "Every chart is interactive and filterable so teams can drill into exactly the "
                "segment or time period they care about.",
                style={"marginBottom": "16px"},
            ),
            feature_row("Overview",     "Revenue trends, order volume, and delivery rate at a glance. Filterable by status and date range."),
            feature_row("Delivery",     "Late delivery rates by state, delivery time distributions, and on-time vs late breakdowns.", color=C["accent2"]),
            feature_row("Reviews",      "Customer satisfaction by product category, score distributions, and delivery vs rating analysis.", color=C["accent3"]),
            feature_row("Payments",     "Payment method usage, revenue by type, and installment behavior across the customer base.", color="#4a90e2"),
            feature_row("Predictions",  "Revenue forecast for the next 6 months, top category trends, and an order delay risk predictor powered by a trained machine learning model.", color="#8b5cf6", last=True),
        ]),

        # ── Tech stack ─────────────────────────────────────────────────────────
        card([
            h("Built With"),
            html.Div([
                html.Span("Plotly Dash · ", style={"color": C["accent"],  "fontWeight": "600", "fontSize": "13px"}),
                html.Span("Pandas · ",      style={"color": C["accent2"], "fontWeight": "600", "fontSize": "13px"}),
                html.Span("scikit-learn · ",style={"color": C["accent3"], "fontWeight": "600", "fontSize": "13px"}),
                html.Span("NumPy · ",       style={"color": "#4a90e2",    "fontWeight": "600", "fontSize": "13px"}),
                html.Span("joblib",         style={"color": C["muted"],   "fontWeight": "600", "fontSize": "13px"}),
            ], style={"marginBottom": "12px"}),
            html.A("↗ Dataset on Kaggle",
                   href="https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce",
                   target="_blank",
                   style={"color": C["accent"], "fontSize": "13px",
                          "fontWeight": "600", "textDecoration": "none"}),
        ]),

        # ── Team ───────────────────────────────────────────────────────────────
        card([
            h("Built By"),
            member("Marlou Angelo Panungcat"),
            member("Mishael Suboan"),
            member("Neilben Balili"),
        ]),

    ])