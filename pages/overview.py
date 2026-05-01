from dash import dcc, html, Input, Output, callback
import plotly.express as px
import pandas as pd

from data_loader import df
from theme import C, PLOTLY_LAYOUT, kpi

# ─────────────────────────────────────────────
# Prepare dataframe once
# ─────────────────────────────────────────────
_df = df.copy()

if "order_purchase_timestamp" in _df.columns:
    _df["order_purchase_timestamp"] = pd.to_datetime(
        _df["order_purchase_timestamp"], errors="coerce"
    )
    _df["_year_month"] = _df["order_purchase_timestamp"].dt.to_period("M").astype(str)
else:
    _df["_year_month"] = _df["month"].astype(str).str[:7]

_STATUS_OPTIONS = [
    {"label": s.replace("_", " ").title(), "value": s}
    for s in sorted(_df["order_status"].dropna().unique())
]

_MIN_YM = _df["_year_month"].min()
_MAX_YM = _df["_year_month"].max()

# ─────────────────────────────────────────────
# Helper for filter tag pills
# ─────────────────────────────────────────────
def _tag(label, bg, color, border):
    return html.Span(label, style={
        "padding": "4px 12px",
        "borderRadius": "20px",
        "fontSize": "12px",
        "fontWeight": "500",
        "background": bg,
        "color": color,
        "border": f"1px solid {border}",
        "display": "inline-block",
    })

_DROPDOWN_STYLE = {
    "borderRadius": "8px",
    "fontSize": "13px",
    "color": "black",
    "backgroundColor": "white"
}

# ─────────────────────────────────────────────
# PAGE LAYOUT
# ─────────────────────────────────────────────
def page_overview():
    return html.Div([

        html.H1("Overview", style={"fontFamily": "'Space Grotesk'", "fontWeight": "700"}),
        html.P("High-level snapshot of the Olist marketplace.",
               style={"color": C["muted"], "marginBottom": "24px"}),

        # FILTER BAR
        html.Div([

            # Search
            html.Div([
                html.Label("Search Order ID", style={
                    "fontSize": "11px",
                    "fontWeight": "600",
                    "textTransform": "uppercase",
                    "letterSpacing": "0.06em",
                    "color": C["muted"],
                    "marginBottom": "6px",
                    "display": "block",
                }),
                dcc.Input(
                    id="ov-search",
                    type="text",
                    debounce=True,
                    placeholder="Type order id prefix…",
                    style={
                        "width": "100%",
                        "padding": "9px 12px",
                        "borderRadius": "8px",
                        "border": f"1px solid {C.get('border', '#2a2e3e')}",
                        "background": C.get("surface", "#1e2235"),
                        "color": C.get("text", "#e8eaf6"),
                        "fontSize": "13px",
                        "boxSizing": "border-box",
                        "outline": "none",
                    },
                ),
            ], style={"flex": "1.2"}),

            # Status filter
            html.Div([
                html.Label("Order Status", style={
                    "fontSize": "11px",
                    "fontWeight": "600",
                    "textTransform": "uppercase",
                    "letterSpacing": "0.06em",
                    "color": C["muted"],
                    "marginBottom": "6px",
                    "display": "block",
                }),
                dcc.Dropdown(
                    id="ov-status-filter",
                    options=_STATUS_OPTIONS,
                    multi=True,
                    placeholder="All statuses",
                    style=_DROPDOWN_STYLE,
                ),
            ], style={"flex": "1.3"}),

            # From
            html.Div([
                html.Label("From", style={
                    "fontSize": "11px",
                    "fontWeight": "600",
                    "textTransform": "uppercase",
                    "letterSpacing": "0.06em",
                    "color": C["muted"],
                    "marginBottom": "6px",
                    "display": "block",
                }),
                dcc.Dropdown(
                    id="ov-start-ym",
                    options=[{"label": m, "value": m}
                             for m in sorted(_df["_year_month"].unique())],
                    value=_MIN_YM,
                    clearable=False,
                    style=_DROPDOWN_STYLE,
                ),
            ], style={"flex": "1"}),

            # To
            html.Div([
                html.Label("To", style={
                    "fontSize": "11px",
                    "fontWeight": "600",
                    "textTransform": "uppercase",
                    "letterSpacing": "0.06em",
                    "color": C["muted"],
                    "marginBottom": "6px",
                    "display": "block",
                }),
                dcc.Dropdown(
                    id="ov-end-ym",
                    options=[{"label": m, "value": m}
                             for m in sorted(_df["_year_month"].unique())],
                    value=_MAX_YM,
                    clearable=False,
                    style=_DROPDOWN_STYLE,
                ),
            ], style={"flex": "1"}),

            # Reset button
            html.Button("↺  Reset Filters", id="ov-reset-btn", n_clicks=0, style={
                "alignSelf": "flex-end",
                "padding": "9px 16px",
                "borderRadius": "8px",
                "border": f"1px solid {C.get('border', '#2a2e3e')}",
                "background": "transparent",
                "color": C["muted"],
                "fontSize": "12px",
                "fontWeight": "600",
                "cursor": "pointer",
                "whiteSpace": "nowrap",
                "letterSpacing": "0.04em",
            }),

        ], style={
            "display": "flex",
            "gap": "12px",
            "alignItems": "flex-end",
            "marginBottom": "16px",
            "padding": "16px 18px",
            "background": C.get("surface", "#1e2235"),
            "borderRadius": "12px",
            "border": f"1px solid {C.get('border', '#2a2e3e')}",
            "flexWrap": "wrap",
        }),

        html.Div(id="ov-filter-tags", style={
            "display": "flex",
            "flexWrap": "wrap",
            "gap": "8px",
            "marginBottom": "20px",
        }),
        html.Div(id="ov-kpis", style={"marginBottom": "20px"}),

        html.Div([
            dcc.Graph(id="ov-trend-chart"),
            dcc.Graph(id="ov-status-chart"),
        ], style={"display": "flex", "gap": "16px"}),
    ])

# ─────────────────────────────────────────────
# RESET CALLBACK
# ─────────────────────────────────────────────
@callback(
    Output("ov-search", "value"),
    Output("ov-status-filter", "value"),
    Output("ov-start-ym", "value"),
    Output("ov-end-ym", "value"),
    Input("ov-reset-btn", "n_clicks"),
    prevent_initial_call=True
)
def _reset(_):
    return "", [], _MIN_YM, _MAX_YM

# ─────────────────────────────────────────────
# MAIN DASHBOARD CALLBACK
# ─────────────────────────────────────────────
@callback(
    Output("ov-kpis", "children"),
    Output("ov-trend-chart", "figure"),
    Output("ov-status-chart", "figure"),
    Output("ov-filter-tags", "children"),
    Input("ov-search", "value"),
    Input("ov-status-filter", "value"),
    Input("ov-start-ym", "value"),
    Input("ov-end-ym", "value"),
)
def _update(search, statuses, start_ym, end_ym):

    filt = _df.copy()

    if search:
        filt = filt[filt["order_id"].str.startswith(search.strip(), na=False)]

    if statuses:
        filt = filt[filt["order_status"].isin(statuses)]

    filt = filt[filt["_year_month"].between(start_ym, end_ym)]

    empty = len(filt) == 0

    # KPIs
    n_orders = filt["order_id"].nunique() if not empty else 0
    total_rev = filt["payment_value"].sum() if not empty else 0
    avg_review = filt["review_score"].mean() if not empty else 0
    delivered_pct = ((filt["order_status"] == "delivered").mean() * 100) if not empty else 0

    kpis_el = html.Div([
        kpi("Total Orders", f"{n_orders:,}"),
        kpi("Total Revenue", f"R$ {total_rev:,.0f}", color=C["accent3"]),
        kpi("Avg Review Score", f"{avg_review:.2f} / 5", color=C["accent2"]),
        kpi("Delivery Rate", f"{delivered_pct:.1f}%"),
    ], style={"display": "flex", "gap": "16px", "flexWrap": "wrap"})

    # Monthly revenue chart
    monthly = filt.groupby("_year_month")["payment_value"].sum().reset_index()
    fig_trend = px.area(monthly, x="_year_month", y="payment_value")
    fig_trend.update_layout(**PLOTLY_LAYOUT, title="Monthly Revenue")

    # Status pie chart
    sc = filt["order_status"].value_counts().reset_index()
    sc.columns = ["status", "count"]
    fig_status = px.pie(sc, names="status", values="count")
    fig_status.update_layout(**PLOTLY_LAYOUT, title="Order Status Breakdown")

    # Filter tags
    tags = []
    if search:
        tags.append(_tag(f"⌕  {search}", "#e8fff8", C["accent"], C["accent"]))
    for s in (statuses or []):
        tags.append(_tag(s.replace("_", " ").title(), "#fff0f0", C["accent3"], C["accent3"]))
    if start_ym != _MIN_YM or end_ym != _MAX_YM:
        tags.append(_tag(f" {start_ym} → {end_ym}", "#eef6ff", "#4a90e2", "#4a90e2"))
    if not tags:
        tags = [_tag("Showing all data", "transparent", C["muted"], C.get("border", "#2a2e3e"))]

    return kpis_el, fig_trend, fig_status, tags