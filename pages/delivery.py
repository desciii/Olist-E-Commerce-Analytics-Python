from dash import dcc, html, Input, Output, callback
import plotly.express as px

from data_loader import delivered
from theme import C, PLOTLY_LAYOUT, kpi

# ─────────────────────────────────────────────
# DATA
# ─────────────────────────────────────────────
_d = delivered.copy()

_STATE_OPTIONS = [
    {"label": s, "value": s}
    for s in sorted(_d["customer_state"].dropna().unique())
]

_MAX_DAYS = int(_d["delivery_days"].quantile(0.99))

# ─────────────────────────────────────────────
# STYLES
# ─────────────────────────────────────────────
_LABEL_STYLE = {
    "fontSize": "11px",
    "fontWeight": "600",
    "textTransform": "uppercase",
    "letterSpacing": "0.06em",
    "color": C["muted"],
    "marginBottom": "6px",
    "display": "block",
}

_INPUT_STYLE = {
    "width": "100%",
    "padding": "10px 12px",
    "borderRadius": "8px",
    "border": f"1px solid {C.get('border', '#2a2e3e')}",
    "background": C.get("surface", "#1e2235"),
    "color": C.get("text", "#e8eaf6"),
    "fontSize": "13px",
    "boxSizing": "border-box",
    "outline": "none",
}

_DROPDOWN_STYLE = {
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
def page_delivery():
    return html.Div([

        # TITLE
        html.H1(
            "Delivery Performance",
            style={"fontFamily": "'Space Grotesk'", "fontWeight": "700", "marginBottom": "8px"},
        ),
        html.P(
            "How fast and reliably are orders delivered?",
            style={"color": C["muted"], "marginBottom": "24px"},
        ),

        # ───────────────────────── FILTER BAR ─────────────────────────
        html.Div([

            # STATE
            html.Div([
                html.Label("Customer State", style=_LABEL_STYLE),
                dcc.Dropdown(
                    id="dv-state-filter",
                    options=_STATE_OPTIONS,
                    multi=True,
                    placeholder="All states",
                    style=_DROPDOWN_STYLE,
                ),
            ], style={"flex": "1 1 220px", "minWidth": "180px"}),

            # DAYS
            html.Div([
                html.Label("Max Delivery Days", style=_LABEL_STYLE),
                dcc.Dropdown(
                    id="dv-days-filter",
                    options=[{"label": f"Up to {d} days", "value": d}
                             for d in [7, 14, 21, 30, 45, 60, _MAX_DAYS]],
                    value=_MAX_DAYS,
                    clearable=False,
                    style=_DROPDOWN_STYLE,
                ),
            ], style={"flex": "1 1 180px", "minWidth": "160px"}),

            # LATE FILTER
            html.Div([
                html.Label("Delivery Status", style=_LABEL_STYLE),
                dcc.Dropdown(
                    id="dv-late-filter",
                    options=[
                        {"label": "All orders", "value": "all"},
                        {"label": "Late only", "value": "late"},
                        {"label": "On-time only", "value": "ontime"},
                    ],
                    value="all",
                    clearable=False,
                    style=_DROPDOWN_STYLE,
                ),
            ], style={"flex": "1 1 180px", "minWidth": "160px"}),

            # RESET
            html.Button(
                "Reset Filters",
                id="dv-reset-btn",
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
            id="dv-filter-tags",
            style={
                "display": "flex",
                "flexWrap": "wrap",
                "gap": "8px",
                "marginTop": "14px",
                "marginBottom": "20px",
            },
        ),

        # KPIS
        html.Div(id="dv-kpis", style={"marginBottom": "20px"}),

        # CHARTS
        html.Div([

            html.Div(
                dcc.Graph(id="dv-late-chart", config={"displayModeBar": False}),
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
                dcc.Graph(id="dv-hist-chart", config={"displayModeBar": False}),
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
    Output("dv-state-filter", "value"),
    Output("dv-days-filter", "value"),
    Output("dv-late-filter", "value"),
    Input("dv-reset-btn", "n_clicks"),
    prevent_initial_call=True,
)
def _reset(_):
    return [], _MAX_DAYS, "all"

# ─────────────────────────────────────────────
# MAIN CALLBACK
# ─────────────────────────────────────────────
@callback(
    Output("dv-kpis", "children"),
    Output("dv-late-chart", "figure"),
    Output("dv-hist-chart", "figure"),
    Output("dv-filter-tags", "children"),
    Input("dv-state-filter", "value"),
    Input("dv-days-filter", "value"),
    Input("dv-late-filter", "value"),
)
def _update(states, max_days, late_filter):

    filt = _d.copy()

    if states:
        filt = filt[filt["customer_state"].isin(states)]

    if max_days:
        filt = filt[filt["delivery_days"] <= max_days]

    if late_filter == "late":
        filt = filt[filt["late"] == 1]
    elif late_filter == "ontime":
        filt = filt[filt["late"] == 0]

    empty = len(filt) == 0

    avg_days = filt["delivery_days"].mean() if not empty else 0
    late_pct = filt["late"].mean() * 100 if not empty else 0

    # KPIs
    kpis_el = html.Div([
        kpi("Avg Delivery Time", f"{avg_days:.1f} days"),
        kpi("Late Delivery Rate", f"{late_pct:.1f}%", color=C["accent2"]),
        kpi("Orders in View", f"{len(filt):,}"),
    ], style={"display": "flex", "gap": "16px", "flexWrap": "wrap"})

    # Late by state
    late_by_state = (
        filt.groupby("customer_state")["late"]
        .mean().mul(100).reset_index()
        .sort_values("late", ascending=True)
        .tail(15)
    )
    late_by_state.columns = ["state", "late_pct"]

    fig_late = px.bar(
        late_by_state,
        x="late_pct",
        y="state",
        orientation="h",
        color_discrete_sequence=[C["accent2"]],
        title="Top 15 States by Late Delivery Rate (%)",
    )
    fig_late.update_layout(**PLOTLY_LAYOUT)

    # Histogram
    fig_hist = px.histogram(
        filt,
        x="delivery_days",
        nbins=40,
        color_discrete_sequence=[C["accent"]],
        title="Distribution of Delivery Times (days)",
    )
    fig_hist.update_layout(**PLOTLY_LAYOUT)

    # Tags
    tags = []

    for s in (states or []):
        tags.append(_tag(s, "#fff0f0", C["accent3"], C["accent3"]))

    if max_days != _MAX_DAYS:
        tags.append(_tag(f"≤ {max_days} days", "#eef6ff", "#4a90e2", "#4a90e2"))

    if late_filter == "late":
        tags.append(_tag("Late only", "#fff8e8", C["accent2"], C["accent2"]))
    elif late_filter == "ontime":
        tags.append(_tag("On-time only", "#e8fff8", C["accent"], C["accent"]))

    if not tags:
        tags = [_tag("All data", "transparent", C["muted"], C.get("border", "#2a2e3e"))]

    return kpis_el, fig_late, fig_hist, tags