from dash import dcc, html, Input, Output, callback
import plotly.express as px

from data_loader import payments
from theme import C, PLOTLY_LAYOUT, kpi


_p = payments.copy()

_TYPE_OPTIONS = [
    {"label": t.replace("_", " ").title(), "value": t}
    for t in sorted(_p["payment_type"].dropna().unique())
]

_MAX_INSTALLMENTS = int(_p["payment_installments"].max())

# ─────────────────────────────────────────────
# STYLES (Synced with Overview)
# ─────────────────────────────────────────────
_DROPDOWN_STYLE = {
    "borderRadius": "8px",
    "fontSize": "13px",
    "color": "black",
    "backgroundColor": "white"
}

_LABEL_STYLE = {
    "fontSize": "11px",
    "fontWeight": "600",
    "textTransform": "uppercase",
    "letterSpacing": "0.06em",
    "color": C["muted"],
    "marginBottom": "6px",
    "display": "block",
}

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


def page_payments():
    return html.Div([

        html.H1("Payment Insights", style={
            "fontFamily": "'Space Grotesk'", "fontWeight": "700", "marginBottom": "8px"
        }),
        html.P("How are customers paying, and how much?", style={
            "color": C["muted"], "marginBottom": "24px"
        }),

        # ── FILTER BAR ──────────────────────────────────────
        html.Div([

            # Payment type
            html.Div([
                html.Label("Payment Type", style=_LABEL_STYLE),
                dcc.Dropdown(
                    id="pm-type-filter",
                    options=_TYPE_OPTIONS,
                    multi=True,
                    placeholder="All types",
                    style=_DROPDOWN_STYLE,
                ),
            ], style={"flex": "1.5"}),

            # Installments
            html.Div([
                html.Label("Max Installments", style=_LABEL_STYLE),
                dcc.Dropdown(
                    id="pm-install-filter",
                    options=[{"label": f"Up to {i}", "value": i}
                             for i in [1, 2, 3, 6, 9, 12, _MAX_INSTALLMENTS]],
                    value=_MAX_INSTALLMENTS,
                    clearable=False,
                    style=_DROPDOWN_STYLE,
                ),
            ], style={"flex": "1"}),

            # Min payment value
            html.Div([
                html.Label("Min Order Value (R$)", style=_LABEL_STYLE),
                dcc.Dropdown(
                    id="pm-minval-filter",
                    options=[{"label": f"R$ {v:,}+", "value": v}
                             for v in [0, 50, 100, 250, 500, 1000]],
                    value=0,
                    clearable=False,
                    style=_DROPDOWN_STYLE,
                ),
            ], style={"flex": "1"}),

            # Reset button
            html.Button("↺  Reset Filters", id="pm-reset-btn", n_clicks=0, style={
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
        html.Div(id="pm-filter-tags", style={
            "display": "flex",
            "flexWrap": "wrap",
            "gap": "8px",
            "marginBottom": "20px",
        }),

        # KPIs
        html.Div(id="pm-kpis", style={"marginBottom": "20px"}),

        # Charts row 1
        html.Div([
            html.Div(
                dcc.Graph(id="pm-type-chart", config={"displayModeBar": False}),
                style={
                    "flex": "1",
                    "background": C.get("card", "#24293e"),
                    "borderRadius": "12px",
                    "border": f"1px solid {C['border']}",
                    "padding": "12px"
                }
            ),
            html.Div(
                dcc.Graph(id="pm-rev-chart", config={"displayModeBar": False}),
                style={
                    "flex": "1",
                    "background": C.get("card", "#24293e"),
                    "borderRadius": "12px",
                    "border": f"1px solid {C['border']}",
                    "padding": "12px"
                }
            ),
        ], style={
            "display": "flex",
            "gap": "16px",
            "marginBottom": "16px"
        }),

        # Chart row 2
        html.Div(
            html.Div(
                dcc.Graph(id="pm-install-chart", config={"displayModeBar": False}),
                style={
                    "background": C.get("card", "#24293e"),
                    "borderRadius": "12px",
                    "border": f"1px solid {C['border']}",
                    "padding": "12px",
                }
            ),
            style={
                "width": "100%"
            }
        ),
    ])


# ─────────────────────────────────────────────
# RESET CALLBACK
# ─────────────────────────────────────────────
@callback(
    Output("pm-type-filter",   "value"),
    Output("pm-install-filter","value"),
    Output("pm-minval-filter", "value"),
    Input("pm-reset-btn", "n_clicks"),
    prevent_initial_call=True,
)
def _reset(_):
    return [], _MAX_INSTALLMENTS, 0


# ─────────────────────────────────────────────
# MAIN CALLBACK
# ─────────────────────────────────────────────
@callback(
    Output("pm-kpis",          "children"),
    Output("pm-type-chart",    "figure"),
    Output("pm-rev-chart",     "figure"),
    Output("pm-install-chart", "figure"),
    Output("pm-filter-tags",   "children"),
    Input("pm-type-filter",    "value"),
    Input("pm-install-filter", "value"),
    Input("pm-minval-filter",  "value"),
)
def _update(types, max_install, min_val):
    filt = _p.copy()

    if types:
        filt = filt[filt["payment_type"].isin(types)]
    if max_install:
        filt = filt[filt["payment_installments"] <= max_install]
    if min_val:
        filt = filt[filt["payment_value"] >= min_val]

    empty = len(filt) == 0

    total_rev  = filt["payment_value"].sum()  if not empty else 0
    avg_val    = filt["payment_value"].mean() if not empty else 0
    avg_inst   = filt[filt["payment_installments"] > 0]["payment_installments"].mean() if not empty else 0
    n_orders   = filt["order_id"].nunique()   if not empty else 0

    kpis_el = html.Div([
        kpi("Total Revenue",    f"R$ {total_rev:,.0f}", color=C["accent3"]),
        kpi("Avg Order Value",  f"R$ {avg_val:,.2f}"),
        kpi("Avg Installments", f"{avg_inst:.1f}x",     color=C["accent2"]),
        kpi("Orders in View",   f"{n_orders:,}"),
    ], style={"display": "flex", "gap": "16px", "flexWrap": "wrap"})

    # Payment type pie
    pay_type = filt["payment_type"].value_counts().reset_index()
    pay_type.columns = ["type", "count"]
    fig_type = px.pie(
        pay_type, names="type", values="count",
        color_discrete_sequence=[C["accent"], C["accent2"], C["accent3"], "#4a90e2"],
        title="Payment Type Breakdown",
    )
    fig_type.update_layout(**PLOTLY_LAYOUT)
    fig_type.update_traces(textfont_color=C["text"])

    # Revenue by type bar
    rev_by_type = filt.groupby("payment_type")["payment_value"].sum().reset_index()
    fig_rev = px.bar(
        rev_by_type, x="payment_type", y="payment_value",
        color_discrete_sequence=[C["accent3"]], title="Revenue by Payment Type",
    )
    fig_rev.update_layout(**PLOTLY_LAYOUT)

    # Installment distribution
    install = filt[filt["payment_installments"] > 0]
    install_dist = install["payment_installments"].value_counts().sort_index().reset_index()
    install_dist.columns = ["installments", "count"]
    fig_install = px.bar(
        install_dist, x="installments", y="count",
        color_discrete_sequence=[C["accent"]], title="Installment Plan Distribution",
    )
    fig_install.update_layout(**PLOTLY_LAYOUT)

    # Filter tags
    tags = []
    for t in (types or []):
        tags.append(_tag(f"● {t.replace('_', ' ').title()}", "#fff0f0", C["accent3"], C["accent3"]))
    if max_install != _MAX_INSTALLMENTS:
        tags.append(_tag(f"≤ {max_install} installments", "#eef6ff", "#4a90e2", "#4a90e2"))
    if min_val and min_val > 0:
        tags.append(_tag(f"R$ {min_val:,}+", "#e8fff8", C["accent"], C["accent"]))
    if not tags:
        tags = [_tag("Showing all data", "transparent", C["muted"], C.get("border", "#2a2e3e"))]

    return kpis_el, fig_type, fig_rev, fig_install, tags