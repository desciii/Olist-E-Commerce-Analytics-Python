from dash import dcc, html, Input, Output, callback
import plotly.express as px

from data_loader import delivered
from theme import C, PLOTLY_LAYOUT, kpi


_d = delivered.copy()

_CAT_OPTIONS = [
    {"label": c.replace("_", " ").title(), "value": c}
    for c in sorted(_d["product_category_name_english"].dropna().unique())
]

_SCORE_OPTIONS = [{"label": str(i), "value": i} for i in range(1, 6)]


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


def page_reviews():
    return html.Div([

        html.H1("Customer Reviews", style={
            "fontFamily": "'Space Grotesk'", "fontWeight": "700", "marginBottom": "8px"
        }),
        html.P("What drives customer satisfaction?", style={
            "color": C["muted"], "marginBottom": "24px"
        }),

        # ── FILTER BAR ──────────────────────────────────────
        html.Div([

            # Category filter
            html.Div([
                html.Label("Product Category", style=_label_style),
                dcc.Dropdown(
                    id="rv-cat-filter",
                    options=_CAT_OPTIONS,
                    multi=True,
                    placeholder="All categories",
                    style={"borderRadius": "8px", "fontSize": "13px"},
                ),
            ], style={"flex": "2"}),

            # Min score filter
            html.Div([
                html.Label("Min Review Score", style=_label_style),
                dcc.Dropdown(
                    id="rv-minscore-filter",
                    options=_SCORE_OPTIONS,
                    value=1,
                    clearable=False,
                    style={"borderRadius": "8px", "fontSize": "13px"},
                ),
            ], style={"flex": "1"}),

            # Max delivery days for scatter
            html.Div([
                html.Label("Max Delivery Days", style=_label_style),
                dcc.Dropdown(
                    id="rv-days-filter",
                    options=[{"label": f"Up to {d} days", "value": d}
                             for d in [7, 14, 21, 30, 45, 60]],
                    value=60,
                    clearable=False,
                    style={"borderRadius": "8px", "fontSize": "13px"},
                ),
            ], style={"flex": "1"}),

            # Reset
            html.Button("↺  Reset Filters", id="rv-reset-btn", n_clicks=0, style={
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
        html.Div(id="rv-filter-tags", style={
            "display": "flex",
            "flexWrap": "wrap",
            "gap": "8px",
            "marginBottom": "20px",
        }),

        # KPIs
        html.Div(id="rv-kpis", style={
            "display": "flex", "gap": "16px",
            "marginBottom": "28px", "flexWrap": "wrap",
        }),

        # Charts row 1
        html.Div([
            html.Div(dcc.Graph(id="rv-dist-chart",    config={"displayModeBar": False}),
                     style={"flex": "1", "background": C["card"], "borderRadius": "12px",
                            "border": f"1px solid {C['border']}", "padding": "8px"}),
            html.Div(dcc.Graph(id="rv-scatter-chart", config={"displayModeBar": False}),
                     style={"flex": "1", "background": C["card"], "borderRadius": "12px",
                            "border": f"1px solid {C['border']}", "padding": "8px"}),
        ], style={"display": "flex", "gap": "16px", "marginBottom": "16px"}),

        # Charts row 2
        html.Div([
            html.Div(dcc.Graph(id="rv-worst-chart", config={"displayModeBar": False}),
                     style={"flex": "1", "background": C["card"], "borderRadius": "12px",
                            "border": f"1px solid {C['border']}", "padding": "8px"}),
            html.Div(dcc.Graph(id="rv-best-chart",  config={"displayModeBar": False}),
                     style={"flex": "1", "background": C["card"], "borderRadius": "12px",
                            "border": f"1px solid {C['border']}", "padding": "8px"}),
        ], style={"display": "flex", "gap": "16px"}),
    ])


# ─────────────────────────────────────────────
# RESET CALLBACK
# ─────────────────────────────────────────────
@callback(
    Output("rv-cat-filter",      "value"),
    Output("rv-minscore-filter", "value"),
    Output("rv-days-filter",     "value"),
    Input("rv-reset-btn", "n_clicks"),
    prevent_initial_call=True,
)
def _reset(_):
    return [], 1, 60


# ─────────────────────────────────────────────
# MAIN CALLBACK
# ─────────────────────────────────────────────
@callback(
    Output("rv-kpis",         "children"),
    Output("rv-dist-chart",   "figure"),
    Output("rv-scatter-chart","figure"),
    Output("rv-worst-chart",  "figure"),
    Output("rv-best-chart",   "figure"),
    Output("rv-filter-tags",  "children"),
    Input("rv-cat-filter",      "value"),
    Input("rv-minscore-filter", "value"),
    Input("rv-days-filter",     "value"),
)
def _update(categories, min_score, max_days):
    filt = _d.copy()

    if categories:
        filt = filt[filt["product_category_name_english"].isin(categories)]
    if min_score and min_score > 1:
        filt = filt[filt["review_score"] >= min_score]
    if max_days:
        filt = filt[filt["delivery_days"] <= max_days]

    empty = len(filt) == 0

    avg_score  = filt["review_score"].mean()  if not empty else 0
    n_reviews  = filt["review_score"].count() if not empty else 0
    pct_5star  = ((filt["review_score"] == 5).mean() * 100) if not empty else 0
    pct_1star  = ((filt["review_score"] == 1).mean() * 100) if not empty else 0

    kpis_el = html.Div([
        kpi("Avg Review Score", f"{avg_score:.2f} / 5"),
        kpi("Total Reviews",    f"{n_reviews:,}",       color=C["accent3"]),
        kpi("5-Star Rate",      f"{pct_5star:.1f}%",    color=C["accent"]),
        kpi("1-Star Rate",      f"{pct_1star:.1f}%",    color=C["accent2"]),
    ], style={"display": "flex", "gap": "16px", "flexWrap": "wrap"})

    # Score distribution
    score_dist = filt["review_score"].value_counts().sort_index().reset_index()
    score_dist.columns = ["score", "count"]
    fig_dist = px.bar(
        score_dist, x="score", y="count",
        color_discrete_sequence=[C["accent3"]], title="Review Score Distribution",
    )
    fig_dist.update_layout(**PLOTLY_LAYOUT)

    # Score vs delivery time scatter
    scatter = filt[filt["delivery_days"] < max_days].dropna(subset=["review_score", "delivery_days"])
    fig_scatter = px.scatter(
        scatter.sample(min(3000, len(scatter)), random_state=42) if not empty else scatter,
        x="delivery_days", y="review_score",
        color="review_score",
        color_continuous_scale=["#ff6b6b", "#ffd166", "#00d4aa"],
        title="Review Score vs Delivery Time",
        opacity=0.5,
    )
    fig_scatter.update_layout(**PLOTLY_LAYOUT)

    # Category ratings
    cat_review = (
        filt.groupby("product_category_name_english")["review_score"]
        .mean().reset_index()
    )
    cat_review.columns = ["category", "avg_score"]
    cat_review = cat_review.dropna().sort_values("avg_score")

    fig_worst = px.bar(
        cat_review.head(10), x="avg_score", y="category", orientation="h",
        color_discrete_sequence=[C["accent2"]], title="10 Worst Rated Categories",
    )
    fig_worst.update_layout(**PLOTLY_LAYOUT)

    fig_best = px.bar(
        cat_review.tail(10), x="avg_score", y="category", orientation="h",
        color_discrete_sequence=[C["accent"]], title="10 Best Rated Categories",
    )
    fig_best.update_layout(**PLOTLY_LAYOUT)

    # Filter tags
    tags = []
    for c in (categories or []):
        tags.append(_tag(f"● {c.replace('_', ' ').title()}", "#fff0f0", C["accent3"], C["accent3"]))
    if min_score and min_score > 1:
        tags.append(_tag(f"★ {min_score}+ stars", "#e8fff8", C["accent"], C["accent"]))
    if max_days != 60:
        tags.append(_tag(f"📅 ≤ {max_days} days", "#eef6ff", "#4a90e2", "#4a90e2"))
    if not tags:
        tags = [_tag("Showing all data", "transparent", C["muted"], C.get("border", "#2a2e3e"))]

    return kpis_el, fig_dist, fig_scatter, fig_worst, fig_best, tags