# pages/predictions.py
import os
import joblib
import pandas as pd
import numpy as np
from dash import dcc, html, Input, Output, State, callback
import plotly.graph_objects as go
import plotly.express as px

from theme import C, PLOTLY_LAYOUT, kpi

BASE = os.path.dirname(os.path.dirname(__file__))
DATA = os.path.join(BASE, "data")

# ── Load pre-computed artefacts ────────────────────────────────────────────────
_forecast_df    = pd.read_csv(os.path.join(DATA, "revenue_forecast.csv"))
_importance_df  = pd.read_csv(os.path.join(DATA, "feature_importance.csv"))
_cat_df         = pd.read_csv(os.path.join(DATA, "category_revenue.csv"))
_model_bundle   = joblib.load(os.path.join(DATA, "delay_model.pkl"))
_clf            = _model_bundle["model"]
_features       = _model_bundle["features"]
_le             = _model_bundle["label_encoder"]

_KNOWN_CATS = sorted(_le.classes_.tolist())
_CAT_OPTIONS = [{"label": c.replace("_", " ").title(), "value": c}
                for c in _KNOWN_CATS]

_LABEL = {
    "fontSize": "11px", "fontWeight": "600",
    "textTransform": "uppercase", "letterSpacing": "0.06em",
    "color": C["muted"], "marginBottom": "6px", "display": "block",
}
_INPUT = {
    "width": "100%",
    "padding": "9px 12px",
    "background": "#1a1f2e",
    "border": f"1px solid {C['border']}",
    "borderRadius": "8px",
    "color": C["text"],
    "fontSize": "13px",
    "outline": "none",
    "boxSizing": "border-box",
    "appearance": "none",
    "WebkitAppearance": "none",
    "MozAppearance": "textfield",
}
_CARD = {
    "background": C["card"], "borderRadius": "12px",
    "border": f"1px solid {C['border']}", "padding": "20px",
}

# ── Field tooltip definitions ──────────────────────────────────────────────────
_TOOLTIPS = {
    "Product Category": "The type of product being ordered. e.g. 'Health & Beauty', 'Electronics'. Categories with longer supply chains tend to have higher delay risk.",
    "Item Price (R$)": "The listed price of the product in Brazilian Reais. e.g. R$120 for a mid-range item. Higher priced items may have more careful handling but also more complex logistics.",
    "Freight Value (R$)": "The shipping cost charged to the customer in R$. e.g. R$18 for standard delivery. Higher freight often means longer distance or bulkier items, which can increase delay risk.",
    "Payment Value (R$)": "The total amount paid including the item and freight. e.g. R$138 = R$120 item + R$18 freight. Usually item price + freight value.",
    "Installments": "How many monthly installments the customer split the payment into. e.g. 1 = paid in full, 3 = split over 3 months. Common in Brazil for larger purchases.",
    "Est. Delivery Days": "The number of days the seller estimated for delivery at the time of purchase. e.g. 14 days. This is the seller's promise, not the actual delivery time.",
    "Purchase Day of Week": "The day of the week the order was placed. e.g. Friday orders may sit in warehouses over the weekend, increasing delay risk.",
    "Purchase Month": "The month the order was placed. Peak months like Nov–Dec (Black Friday, Christmas) tend to have higher delay rates due to volume surges.",
}


def _tooltip_icon(field_name):
    """Renders a ! icon with a CSS hover tooltip."""
    tip = _TOOLTIPS.get(field_name, "")
    return html.Span(
        [
            html.Span("!", style={
                "display": "inline-flex",
                "alignItems": "center",
                "justifyContent": "center",
                "width": "14px",
                "height": "14px",
                "borderRadius": "50%",
                "border": f"1px solid {C['muted']}",
                "color": C["muted"],
                "fontSize": "9px",
                "fontWeight": "700",
                "cursor": "help",
                "lineHeight": "1",
                "flexShrink": "0",
            }),
            html.Span(tip, style={
                "visibility": "hidden",
                "opacity": "0",
                "position": "absolute",
                "bottom": "calc(100% + 8px)",
                "left": "0",
                "width": "240px",
                "background": "#1e2330",
                "border": f"1px solid {C['border']}",
                "borderRadius": "8px",
                "padding": "10px 12px",
                "fontSize": "12px",
                "color": C["text"],
                "lineHeight": "1.5",
                "zIndex": "9999",
                "boxShadow": "0 4px 20px rgba(0,0,0,0.4)",
                "pointerEvents": "none",
                "transition": "opacity 0.15s ease",
                "fontWeight": "400",
                "textTransform": "none",
                "letterSpacing": "0",
            }, className="tooltip-bubble"),
        ],
        className="tooltip-wrapper",
        style={
            "position": "relative",
            "display": "inline-flex",
            "alignItems": "center",
            "marginLeft": "6px",
            "verticalAlign": "middle",
        },
    )


def _label_with_tip(text):
    """Label row with text + tooltip icon."""
    return html.Div([
        html.Span(text, style={
            **_LABEL,
            "display": "inline",
            "marginBottom": "0",
        }),
        _tooltip_icon(text),
    ], style={
        "display": "flex",
        "alignItems": "center",
        "gap": "4px",
        "marginBottom": "6px",
    })


def _section(title, subtitle, children):
    return html.Div([
        html.H2(title, style={
            "fontFamily": "'Space Grotesk'", "fontWeight": "700",
            "fontSize": "18px", "marginBottom": "2px", "color": C["text"],
        }),
        html.P(subtitle, style={"color": C["muted"], "fontSize": "13px",
                                 "marginBottom": "16px"}),
        *children,
    ], style={"marginBottom": "40px"})


def page_predictions():
    hist = _forecast_df[~_forecast_df["is_forecast"]]
    fcast = _forecast_df[_forecast_df["is_forecast"]]
    next_rev = fcast["revenue"].iloc[0] if len(fcast) else 0
    last_rev = hist["revenue"].iloc[-1] if len(hist) else 0
    delta_pct = ((next_rev - last_rev) / last_rev * 100) if last_rev else 0

    return html.Div([
        html.H1(
            "Predictive Analysis",
            style={"fontFamily": "'Space Grotesk'", "fontWeight": "700"},
        ),
        html.P(
            "Machine-learning forecasts trained offline on the full Olist dataset.",
            style={"color": C["muted"], "marginBottom": "32px"},
        ),

        # ── Section 1: Revenue Forecast ────────────────────────────────────────
        _section("Revenue Forecast", "Linear trend extrapolation — next 6 months", [
            html.Div([
                kpi("Last Month Revenue", f"R$ {last_rev:,.0f}"),
                kpi("Next Month Forecast", f"R$ {next_rev:,.0f}", color=C["accent"]),
                kpi("Projected Change",
                    f"{'+' if delta_pct >= 0 else ''}{delta_pct:.1f}%",
                    color=C["accent"] if delta_pct >= 0 else C["accent2"]),
            ], style={"display": "flex", "gap": "16px",
                      "flexWrap": "wrap", "marginBottom": "20px"}),
            html.Div(
                dcc.Graph(id="pred-revenue-chart", config={"displayModeBar": False}),
                style=_CARD,
            ),
        ]),

        # ── Section 2: Category Trends ─────────────────────────────────────────
        _section("Top Category Revenue Trends",
                 "Monthly revenue for the 10 highest-earning product categories", [
            html.Div(
                dcc.Graph(id="pred-category-chart", config={"displayModeBar": False}),
                style=_CARD,
            ),
        ]),

        # ── Section 3: Delay Risk Predictor ────────────────────────────────────
        _section("Order Delay Risk Predictor",
                 "Enter order details to get a late-delivery probability", [
            html.Div([
                html.Div([

                    html.Div([
                        _label_with_tip("Product Category"),
                        dcc.Dropdown(
                            id="pred-cat",
                            options=_CAT_OPTIONS,
                            placeholder="Select category…",
                            style={"fontSize": "13px"},
                        ),
                    ], style={"flex": "2", "minWidth": "180px"}),

                    html.Div([
                        _label_with_tip("Item Price (R$)"),
                        dcc.Input(id="pred-price", type="text",
                                placeholder="e.g. 120", style=_INPUT),
                    ], style={"flex": "1", "minWidth": "130px"}),

                    html.Div([
                        _label_with_tip("Freight Value (R$)"),
                        dcc.Input(id="pred-freight", type="text",
                                placeholder="e.g. 18", style=_INPUT),
                    ], style={"flex": "1", "minWidth": "130px"}),

                    html.Div([
                        _label_with_tip("Payment Value (R$)"),
                        dcc.Input(id="pred-payment", type="text",
                                placeholder="e.g. 138", style=_INPUT),
                    ], style={"flex": "1", "minWidth": "130px"}),

                    html.Div([
                        _label_with_tip("Installments"),
                        dcc.Input(id="pred-installments", type="text",
                                placeholder="e.g. 3", style=_INPUT),
                    ], style={"flex": "1", "minWidth": "130px"}),

                    html.Div([
                        _label_with_tip("Est. Delivery Days"),
                        dcc.Input(id="pred-est-days", type="text",
                                placeholder="e.g. 14", style=_INPUT),
                    ], style={"flex": "1", "minWidth": "110px"}),

                    html.Div([
                        _label_with_tip("Purchase Day of Week"),
                        dcc.Dropdown(
                            id="pred-dow",
                            options=[
                                {"label": d, "value": i}
                                for i, d in enumerate([
                                    "Monday", "Tuesday", "Wednesday",
                                    "Thursday", "Friday", "Saturday", "Sunday"
                                ])
                            ],
                            placeholder="Day…",
                            style={"fontSize": "13px"},
                        ),
                    ], style={"flex": "1", "minWidth": "180px"}),

                    html.Div([
                        _label_with_tip("Purchase Month"),
                        dcc.Dropdown(
                            id="pred-month",
                            options=[{"label": m, "value": i + 1}
                                     for i, m in enumerate([
                                        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                                        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
                                     ])],
                            placeholder="Month…",
                            style={"fontSize": "13px"},
                        ),
                    ], style={"flex": "1", "minWidth": "130px"}),

                ], style={
                    "display": "flex", "flexWrap": "wrap", "gap": "12px",
                    "marginBottom": "16px",
                }),

                html.Button(
                    "Predict Delay Risk",
                    id="pred-run-btn",
                    n_clicks=0,
                    style={
                        "padding": "11px 28px",
                        "background": f"linear-gradient(135deg, {C['accent']}, #00a884)",
                        "border": "none", "borderRadius": "8px",
                        "color": "#0d0f14", "fontWeight": "700",
                        "fontSize": "14px", "cursor": "pointer",
                        "marginBottom": "20px",
                    },
                ),

                html.Div(id="pred-delay-result"),

            ], style=_CARD),
        ]),

        # ── Section 4: Feature Importance ─────────────────────────────────────
        _section("What Drives Late Deliveries?",
                 "Feature importance from the trained gradient boosting model", [
            html.Div(
                dcc.Graph(id="pred-importance-chart", config={"displayModeBar": False}),
                style=_CARD,
            ),
        ]),
    ])


# ── Callbacks (unchanged) ──────────────────────────────────────────────────────

@callback(
    Output("pred-revenue-chart", "figure"),
    Input("pred-revenue-chart", "id"),
)
def _render_forecast(_):
    hist  = _forecast_df[~_forecast_df["is_forecast"]]
    fcast = _forecast_df[_forecast_df["is_forecast"]]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hist["month"], y=hist["revenue"],
        mode="lines", name="Historical",
        line=dict(color=C["accent"], width=2),
        fill="tozeroy", fillcolor="rgba(0,212,170,0.08)",
    ))
    fig.add_trace(go.Scatter(
        x=list(fcast["month"]) + list(fcast["month"])[::-1],
        y=list(fcast["revenue_high"]) + list(fcast["revenue_low"])[::-1],
        fill="toself", fillcolor="rgba(255,209,102,0.12)",
        line=dict(color="rgba(0,0,0,0)"),
        name="Confidence Band", showlegend=True,
    ))
    fig.add_trace(go.Scatter(
        x=fcast["month"], y=fcast["revenue"],
        mode="lines+markers", name="Forecast",
        line=dict(color=C["accent3"], width=2, dash="dash"),
        marker=dict(size=6, color=C["accent3"]),
    ))
    fig.update_layout(
        **PLOTLY_LAYOUT,
        title="Revenue Forecast — Next 6 Months",
        hovermode="x unified",
        hoverlabel=dict(bgcolor="white", font_color="black", font_size=12),
    )
    return fig


@callback(
    Output("pred-category-chart", "figure"),
    Input("pred-category-chart", "id"),
)
def _render_category(_):
    fig = px.line(
        _cat_df.rename(columns={
            "_ym": "month",
            "payment_value": "revenue",
            "product_category_name_english": "category",
        }),
        x="month", y="revenue", color="category",
        color_discrete_sequence=px.colors.qualitative.Safe,
    )
    fig.update_layout(
        **PLOTLY_LAYOUT,
        title="Top 10 Categories — Monthly Revenue",
        hovermode="x unified",
        hoverlabel=dict(bgcolor="white", font_color="black", font_size=12),
    )
    return fig


@callback(
    Output("pred-importance-chart", "figure"),
    Input("pred-importance-chart", "id"),
)
def _render_importance(_):
    FRIENDLY = {
        "freight_value":        "Freight Value",
        "price":                "Item Price",
        "estimated_days":       "Estimated Delivery Days",
        "purchase_dow":         "Purchase Day of Week",
        "purchase_month":       "Purchase Month",
        "payment_value":        "Payment Value",
        "payment_installments": "Payment Installments",
        "cat_encoded":          "Product Category",
    }
    df = _importance_df.copy()
    df["feature"] = df["feature"].map(FRIENDLY).fillna(df["feature"])
    df = df.sort_values("importance")
    fig = px.bar(df, x="importance", y="feature", orientation="h",
                 color="importance",
                 color_continuous_scale=[[0, C["border"]], [1, C["accent"]]])
    fig.update_layout(**PLOTLY_LAYOUT,
                      title="Feature Importance — Delay Classifier",
                      coloraxis_showscale=False)
    return fig


def _safe_float(v):
    try:
        return float(str(v).strip())
    except (TypeError, ValueError):
        return None


@callback(
    Output("pred-delay-result", "children"),
    Input("pred-run-btn", "n_clicks"),
    State("pred-cat",          "value"),
    State("pred-price",        "value"),
    State("pred-freight",      "value"),
    State("pred-payment",      "value"),
    State("pred-installments", "value"),
    State("pred-est-days",     "value"),
    State("pred-dow",          "value"),
    State("pred-month",        "value"),
    prevent_initial_call=True,
)
def _predict_delay(_, cat, price, freight, payment, installments, est_days, dow, month):
    price        = _safe_float(price)
    freight      = _safe_float(freight)
    payment      = _safe_float(payment)
    installments = _safe_float(installments)
    est_days     = _safe_float(est_days)

    missing = []
    if cat          is None: missing.append("Product Category")
    if price        is None: missing.append("Item Price")
    if freight      is None: missing.append("Freight Value")
    if payment      is None: missing.append("Payment Value")
    if installments is None: missing.append("Installments")
    if est_days     is None: missing.append("Est. Delivery Days")
    if dow          is None: missing.append("Purchase Day of Week")
    if month        is None: missing.append("Purchase Month")

    if missing:
        return html.P(
            f"Please fill in: {', '.join(missing)}",
            style={"color": C["accent2"], "fontSize": "13px"},
        )

    cat_enc = _le.transform([cat])[0] if cat in _le.classes_ else 0
    X = pd.DataFrame([{
        "freight_value":        freight,
        "price":                price,
        "estimated_days":       est_days,
        "purchase_dow":         dow,
        "purchase_month":       month,
        "payment_value":        payment,
        "payment_installments": installments,
        "cat_encoded":          cat_enc,
    }])[_features]

    prob = _clf.predict_proba(X)[0][1]
    pct  = prob * 100

    if pct < 30:
        color, label = C["accent"],  "Low Risk"
    elif pct < 60:
        color, label = C["accent3"], "Medium Risk"
    else:
        color, label = C["accent2"], "High Risk"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=pct,
        number={"suffix": "%", "font": {"color": color, "size": 36}},
        gauge={
            "axis": {"range": [0, 100],
                     "tickcolor": C["muted"], "tickfont": {"color": C["muted"]}},
            "bar":  {"color": color},
            "bgcolor": C["card"],
            "steps": [
                {"range": [0,  30], "color": "rgba(0,212,170,0.12)"},
                {"range": [30, 60], "color": "rgba(255,209,102,0.12)"},
                {"range": [60,100], "color": "rgba(255,107,107,0.12)"},
            ],
            "threshold": {"line": {"color": color, "width": 3}, "value": pct},
        },
        title={"text": f"{label} — Late Delivery Probability",
               "font": {"color": color, "size": 15}},
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=C["text"], family="DM Sans"),
        margin=dict(l=30, r=30, t=60, b=20),
        height=260,
    )

    return html.Div([
        dcc.Graph(figure=fig, config={"displayModeBar": False}),
        html.P(
            f"This order has a {pct:.1f}% chance of arriving after the estimated date "
            f"based on the trained model.",
            style={"color": C["muted"], "fontSize": "12px",
                   "textAlign": "center", "marginTop": "4px"},
        ),
    ])