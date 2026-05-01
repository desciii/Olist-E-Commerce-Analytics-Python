from dash import dcc, html, Input, Output, callback
import plotly.express as px

from data_loader import delivered
from theme import C, PLOTLY_LAYOUT, kpi


_d = delivered.copy()

_STATE_OPTIONS = [
    {"label": s, "value": s}
    for s in sorted(_d["customer_state"].dropna().unique())
]

_MAX_DAYS = int(_d["delivery_days"].quantile(0.99))  # cap at 99th pct for slider


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


_label_style = {
    "fontSize": "11px",
    "fontWeight": "600",
    "textTransform": "uppercase",
    "letterSpacing": "0.06em",
    "color": C["muted"],
    "marginBottom": "6px",
    "display": "block",
}


def page_delivery():
    return html.Div([

        html.H1("Delivery Performance", style={
            "fontFamily": "'Space Grotesk'", "fontWeight": "700", "marginBottom": "8px"
        }),
        html.P("How fast and reliably are orders delivered?", style={
            "color": C["muted"], "marginBottom": "24px"
        }),

        # ── FILTER BAR ──────────────────────────────────────
        html.Div([

            # State filter
            html.Div([
                html.Label("Customer State", style=_label_style),
                dcc.Dropdown(
                    id="dv-state-filter",
                    options=_STATE_OPTIONS,
                    multi=True,
                    placeholder="All states",
                    style={"borderRadius": "8px", "fontSize": "13px"},
                ),
            ], style={"flex": "1.5"}),

            # Max delivery days
            html.Div([
                html.Label("Max Delivery Days", style=_label_style),
                dcc.Dropdown(
                    id="dv-days-filter",
                    options=[{"label": f"Up to {d} days", "value": d}
                             for d in [7, 14, 21, 30, 45, 60, _MAX_DAYS]],
                    value=_MAX_DAYS,
                    clearable=False,
                    style={"borderRadius": "8px", "fontSize": "13px"},
                ),
            ], style={"flex": "1"}),

            # Late only toggle
            html.Div([
                html.Label("Delivery Status", style=_label_style),
                dcc.Dropdown(
                    id="dv-late-filter",
                    options=[
                        {"label": "All orders", "value": "all"},
                        {"label": "Late only",  "value": "late"},
                        {"label": "On-time only", "value": "ontime"},
                    ],
                    value="all",
                    clearable=False,
                    style={"borderRadius": "8px", "fontSize": "13px"},
                ),
            ], style={"flex": "1"}),

            # Reset
            html.Button("↺  Reset Filters", id="dv-reset-btn", n_clicks=0, style={
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

        # Active filter tags
        html.Div(id="dv-filter-tags", style={
            "display": "flex",
            "flexWrap": "wrap",
            "gap": "8px",
            "marginBottom": "20px",
        }),

        # KPIs
        html.Div(id="dv-kpis", style={
            "display": "flex", "gap": "16px", "marginBottom": "28px"
        }),

        # Charts
        html.Div([
            html.Div(dcc.Graph(id="dv-late-chart", config={"displayModeBar": False}),
                     style={"flex": "1", "background": C["card"], "borderRadius": "12px",
                            "border": f"1px solid {C['border']}", "padding": "8px"}),
            html.Div(dcc.Graph(id="dv-hist-chart", config={"displayModeBar": False}),
                     style={"flex": "1", "background": C["card"], "borderRadius": "12px",
                            "border": f"1px solid {C['border']}", "padding": "8px"}),
        ], style={"display": "flex", "gap": "16px"}),
    ])


# ─────────────────────────────────────────────
# RESET CALLBACK
# ─────────────────────────────────────────────
@callback(
    Output("dv-state-filter", "value"),
    Output("dv-days-filter",  "value"),
    Output("dv-late-filter",  "value"),
    Input("dv-reset-btn", "n_clicks"),
    prevent_initial_call=True,
)
def _reset(_):
    return [], _MAX_DAYS, "all"


# ─────────────────────────────────────────────
# MAIN CALLBACK
# ─────────────────────────────────────────────
@callback(
    Output("dv-kpis",        "children"),
    Output("dv-late-chart",  "figure"),
    Output("dv-hist-chart",  "figure"),
    Output("dv-filter-tags", "children"),
    Input("dv-state-filter", "value"),
    Input("dv-days-filter",  "value"),
    Input("dv-late-filter",  "value"),
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
    late_pct = filt["late"].mean() * 100    if not empty else 0

    kpis_el = html.Div([
        kpi("Avg Delivery Time",  f"{avg_days:.1f} days"),
        kpi("Late Delivery Rate", f"{late_pct:.1f}%", color=C["accent2"]),
        kpi("Orders in View",     f"{len(filt):,}"),
    ], style={"display": "flex", "gap": "16px", "flexWrap": "wrap"})

    # Late by state chart
    late_by_state = (
        filt.groupby("customer_state")["late"]
        .mean().mul(100).reset_index()
    )
    late_by_state.columns = ["state", "late_pct"]
    late_by_state = late_by_state.sort_values("late_pct", ascending=True).tail(15)

    fig_late = px.bar(
        late_by_state, x="late_pct", y="state", orientation="h",
        color_discrete_sequence=[C["accent2"]],
        title="Top 15 States by Late Delivery Rate (%)",
    )
    fig_late.update_layout(**PLOTLY_LAYOUT)

    # Delivery time histogram
    hist_data = filt[filt["delivery_days"] < max_days] if max_days else filt[filt["delivery_days"] < 60]
    fig_hist = px.histogram(
        hist_data, x="delivery_days", nbins=40,
        color_discrete_sequence=[C["accent"]],
        title="Distribution of Delivery Times (days)",
    )
    fig_hist.update_layout(**PLOTLY_LAYOUT)

    # Filter tags
    tags = []
    for s in (states or []):
        tags.append(_tag(f"● {s}", "#fff0f0", C["accent3"], C["accent3"]))
    if max_days != _MAX_DAYS:
        tags.append(_tag(f"📅 ≤ {max_days} days", "#eef6ff", "#4a90e2", "#4a90e2"))
    if late_filter == "late":
        tags.append(_tag("Late only", "#fff8e8", C["accent2"], C["accent2"]))
    elif late_filter == "ontime":
        tags.append(_tag("On-time only", "#e8fff8", C["accent"], C["accent"]))
    if not tags:
        tags = [_tag("Showing all data", "transparent", C["muted"], C.get("border", "#2a2e3e"))]

    return kpis_el, fig_late, fig_hist, tags