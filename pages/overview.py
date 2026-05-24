from dash import dcc, html, Input, Output, callback
import plotly.express as px

from data_loader import df
from theme import C, PLOTLY_LAYOUT, kpi

# ─────────────────────────────────────────────
# DATA PREP
# ─────────────────────────────────────────────
_df = df.copy()
_df["_year_month"] = _df["month"].astype(str)

_VALID_STATUSES = {"delivered", "shipped", "canceled", "invoiced", "processing", "created", "approved"}

_df = _df[_df["order_status"].isin(_VALID_STATUSES)]

_STATUS_OPTIONS = [
    {"label": s.replace("_", " ").title(), "value": s}
    for s in sorted(_df["order_status"].dropna().unique())
]

_MIN_YM = _df["_year_month"].min()
_MAX_YM = _df["_year_month"].max()

# ─────────────────────────────────────────────
# STYLES
# ─────────────────────────────────────────────
LABEL_STYLE = {
    "fontSize": "11px",
    "fontWeight": "600",
    "textTransform": "uppercase",
    "letterSpacing": "0.06em",
    "color": "white",
    "marginBottom": "6px",
    "display": "block",
}

INPUT_STYLE = {
    "width": "100%",
    "padding": "10px 12px",
    "borderRadius": "8px",
    "border": f"1px solid {C.get('border', '#2a2e3e')}",
    "background": C.get("surface", "#1e2235"),
    "color": "white",
    "fontSize": "13px",
    "outline": "none",
    "boxSizing": "border-box",
}

DROPDOWN_STYLE = {
    "borderRadius": "8px",
    "fontSize": "13px",
    "color": "black",
}

# ─────────────────────────────────────────────
# TAGS
# ─────────────────────────────────────────────
def _tag(label, bg, color, border):
    return html.Span(
        label,
        style={
            "padding": "4px 10px",
            "borderRadius": "20px",
            "fontSize": "12px",
            "fontWeight": "500",
            "background": bg,
            "color": color,
            "border": f"1px solid {border}",
            "display": "inline-block",
        },
    )

# ─────────────────────────────────────────────
# PAGE
# ─────────────────────────────────────────────
def page_overview():
    return html.Div([

        # TITLE
        html.H1(
            "Overview",
            style={"fontFamily": "'Space Grotesk'", "fontWeight": "700"},
        ),
        html.P(
            "High-level snapshot of the Olist marketplace.",
            style={"color": C["muted"], "marginBottom": "24px"},
        ),

        # ───────────────────────── FILTER BAR ─────────────────────────
        html.Div([

            # Status
            html.Div([
                html.Label("Order Status", style=LABEL_STYLE),
                dcc.Dropdown(
                    id="ov-status-filter",
                    options=_STATUS_OPTIONS,
                    multi=True,
                    placeholder="All statuses",
                    style=DROPDOWN_STYLE,
                ),
            ], style={"flex": "1 1 240px", "minWidth": "200px"}),

            # From
            html.Div([
                html.Label("From", style=LABEL_STYLE),
                dcc.Dropdown(
                    id="ov-start-ym",
                    options=[{"label": m, "value": m} for m in sorted(_df["_year_month"].unique())],
                    value=_MIN_YM,
                    clearable=False,
                    style=DROPDOWN_STYLE,
                ),
            ], style={"flex": "1 1 160px", "minWidth": "140px"}),

            # To
            html.Div([
                html.Label("To", style=LABEL_STYLE),
                dcc.Dropdown(
                    id="ov-end-ym",
                    options=[{"label": m, "value": m} for m in sorted(_df["_year_month"].unique())],
                    value=_MAX_YM,
                    clearable=False,
                    style=DROPDOWN_STYLE,
                ),
            ], style={"flex": "1 1 160px", "minWidth": "140px"}),

            # Reset
            html.Button(
                "Reset Filters",
                id="ov-reset-btn",
                n_clicks=0,
                style={
                    "padding": "10px 14px",
                    "borderRadius": "8px",
                    "border": f"1px solid {C.get('border', '#2a2e3e')}",
                    "background": "transparent",
                    "color": C["muted"],
                    "fontSize": "12px",
                    "fontWeight": "600",
                    "cursor": "pointer",
                    "whiteSpace": "nowrap",
                    "flex": "0 0 auto",
                    "alignSelf": "flex-end",
                },
            ),

        ], style={
            "display": "flex",
            "flexWrap": "wrap",
            "gap": "12px",
            "alignItems": "flex-end",
            "padding": "16px",
            "background": C.get("surface", "#1e2235"),
            "borderRadius": "12px",
            "border": f"1px solid {C.get('border', '#2a2e3e')}",
        }),

        # FILTER TAGS
        html.Div(
            id="ov-filter-tags",
            style={
                "display": "flex",
                "flexWrap": "wrap",
                "gap": "8px",
                "marginTop": "14px",
                "marginBottom": "20px",
            },
        ),

        # KPI ROW
        html.Div(id="ov-kpis", style={"marginBottom": "20px"}),

        # CHARTS
        html.Div([

            html.Div(
                dcc.Loading(
                    type="circle",
                    children=dcc.Graph(
                        id="ov-trend-chart",
                        config={"displayModeBar": False}
                    ),
                ),
                style={
                    "background": C.get("card", "#24293e"),
                    "borderRadius": "12px",
                    "border": f"1px solid {C['border']}",
                    "padding": "12px",
                    "flex": "1 1 500px",
                    "minWidth": "280px",
                },
            ),

            html.Div(
                dcc.Loading(
                    type="circle",
                    children=dcc.Graph(
                        id="ov-status-chart",
                        config={"displayModeBar": False}
                    ),
                ),
                style={
                    "background": C.get("card", "#24293e"),
                    "borderRadius": "12px",
                    "border": f"1px solid {C['border']}",
                    "padding": "12px",
                    "flex": "1 1 500px",
                    "minWidth": "280px",
                },
            ),

        ], style={
            "display": "flex",
            "flexWrap": "wrap",
            "gap": "16px",
        }),
    ])

# ─────────────────────────────────────────────
# RESET CALLBACK
# ─────────────────────────────────────────────
@callback(
    Output("ov-status-filter", "value"),
    Output("ov-start-ym", "value"),
    Output("ov-end-ym", "value"),
    Input("ov-reset-btn", "n_clicks"),
    prevent_initial_call=True,
)
def _reset(_):
    return [], _MIN_YM, _MAX_YM

# ─────────────────────────────────────────────
# MAIN CALLBACK
# ─────────────────────────────────────────────
@callback(
    Output("ov-kpis", "children"),
    Output("ov-trend-chart", "figure"),
    Output("ov-status-chart", "figure"),
    Output("ov-filter-tags", "children"),
    Input("ov-status-filter", "value"),
    Input("ov-start-ym", "value"),
    Input("ov-end-ym", "value"),
)
def _update(statuses, start_ym, end_ym):

    filt = _df.copy()

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

    # Charts
    monthly = filt.groupby("_year_month")["payment_value"].sum().reset_index()
    fig_trend = px.area(monthly, x="_year_month", y="payment_value")
    fig_trend.update_layout(**PLOTLY_LAYOUT, title="Monthly Revenue")

    sc = filt["order_status"].value_counts().reset_index()
    sc.columns = ["status", "count"]
    fig_status = px.pie(sc, names="status", values="count")
    fig_status.update_layout(**PLOTLY_LAYOUT, title="Order Status Breakdown")

    # Tags
    tags = []
    for s in (statuses or []):
        tags.append(_tag(s.title(), "#fff0f0", C["accent3"], C["accent3"]))
    if start_ym != _MIN_YM or end_ym != _MAX_YM:
        tags.append(_tag(f"{start_ym} → {end_ym}", "#eef6ff", "#4a90e2", "#4a90e2"))
    if not tags:
        tags = [_tag("All data", "transparent", C["muted"], C.get("border", "#2a2e3e"))]

    return kpis_el, fig_trend, fig_status, tags