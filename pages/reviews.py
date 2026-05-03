from dash import dcc, html, Input, Output, callback
import plotly.express as px

from data_loader import df
from theme import C, PLOTLY_LAYOUT, kpi

# ─────────────────────────────────────────────
# DATA
# ─────────────────────────────────────────────
_d = df.copy()

_CAT_OPTIONS = [
    {"label": c.replace("_", " ").title(), "value": c}
    for c in sorted(_d["product_category_name_english"].dropna().unique())
]

_SCORE_OPTIONS = [
    {"label": f"{i} Stars & Up", "value": i}
    for i in range(1, 6)
]

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
def page_reviews():
    return html.Div([

        # TITLE
        html.H1(
            "Customer Reviews",
            style={"fontFamily": "'Space Grotesk'", "fontWeight": "700"},
        ),
        html.P(
            "What drives customer satisfaction?",
            style={"color": C["muted"], "marginBottom": "24px"},
        ),

        # ───────────────────────── FILTER BAR ─────────────────────────
        html.Div([

            # CATEGORY
            html.Div([
                html.Label("Product Category", style=_LABEL_STYLE),
                dcc.Dropdown(
                    id="rv-cat-filter",
                    options=_CAT_OPTIONS,
                    multi=True,
                    placeholder="All categories",
                    style=_DROPDOWN_STYLE,
                ),
            ], style={"flex": "2 1 260px", "minWidth": "220px"}),

            # MIN SCORE
            html.Div([
                html.Label("Min Review Score", style=_LABEL_STYLE),
                dcc.Dropdown(
                    id="rv-minscore-filter",
                    options=_SCORE_OPTIONS,
                    value=1,
                    clearable=False,
                    style=_DROPDOWN_STYLE,
                ),
            ], style={"flex": "1 1 160px", "minWidth": "140px"}),

            # DELIVERY DAYS
            html.Div([
                html.Label("Max Delivery Days", style=_LABEL_STYLE),
                dcc.Dropdown(
                    id="rv-days-filter",
                    options=[
                        {"label": f"Up to {d} days", "value": d}
                        for d in [7, 14, 21, 30, 45, 60]
                    ],
                    value=60,
                    clearable=False,
                    style=_DROPDOWN_STYLE,
                ),
            ], style={"flex": "1 1 160px", "minWidth": "140px"}),

            # RESET
            html.Button(
                "Reset Filters",
                id="rv-reset-btn",
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
            id="rv-filter-tags",
            style={
                "display": "flex",
                "flexWrap": "wrap",
                "gap": "8px",
                "marginTop": "14px",
                "marginBottom": "20px",
            },
        ),

        # KPI ROW
        html.Div(id="rv-kpis", style={"marginBottom": "20px"}),

        # ───────────────────────── CHART GRID ─────────────────────────
        html.Div([

            html.Div(
                dcc.Graph(id="rv-dist-chart", config={"displayModeBar": False}),
                style={
                    "background": C.get("card", "#24293e"),
                    "borderRadius": "12px",
                    "border": f"1px solid {C['border']}",
                    "padding": "12px",
                    "flex": "1 1 420px",
                    "minWidth": "280px",
                },
            ),

            html.Div(
                dcc.Graph(id="rv-scatter-chart", config={"displayModeBar": False}),
                style={
                    "background": C.get("card", "#24293e"),
                    "borderRadius": "12px",
                    "border": f"1px solid {C['border']}",
                    "padding": "12px",
                    "flex": "1 1 420px",
                    "minWidth": "280px",
                },
            ),

            html.Div(
                dcc.Graph(id="rv-worst-chart", config={"displayModeBar": False}),
                style={
                    "background": C.get("card", "#24293e"),
                    "borderRadius": "12px",
                    "border": f"1px solid {C['border']}",
                    "padding": "12px",
                    "flex": "1 1 420px",
                    "minWidth": "280px",
                },
            ),

            html.Div(
                dcc.Graph(id="rv-best-chart", config={"displayModeBar": False}),
                style={
                    "background": C.get("card", "#24293e"),
                    "borderRadius": "12px",
                    "border": f"1px solid {C['border']}",
                    "padding": "12px",
                    "flex": "1 1 420px",
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
    Output("rv-cat-filter", "value"),
    Output("rv-minscore-filter", "value"),
    Output("rv-days-filter", "value"),
    Input("rv-reset-btn", "n_clicks"),
    prevent_initial_call=True,
)
def _reset(_):
    return [], 1, 60

# ─────────────────────────────────────────────
# MAIN CALLBACK
# ─────────────────────────────────────────────
@callback(
    Output("rv-kpis", "children"),
    Output("rv-dist-chart", "figure"),
    Output("rv-scatter-chart", "figure"),
    Output("rv-worst-chart", "figure"),
    Output("rv-best-chart", "figure"),
    Output("rv-filter-tags", "children"),
    Input("rv-cat-filter", "value"),
    Input("rv-minscore-filter", "value"),
    Input("rv-days-filter", "value"),
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

    # KPIs
    avg_score = filt["review_score"].mean() if not empty else 0
    n_reviews = filt["review_score"].count() if not empty else 0
    pct_5star = ((filt["review_score"] == 5).mean() * 100) if not empty else 0
    pct_1star = ((filt["review_score"] == 1).mean() * 100) if not empty else 0

    kpis_el = html.Div([
        kpi("Avg Review Score", f"{avg_score:.2f} / 5", color=C["accent3"]),
        kpi("Total Reviews", f"{n_reviews:,}"),
        kpi("5-Star Rate", f"{pct_5star:.1f}%", color=C["accent"]),
        kpi("1-Star Rate", f"{pct_1star:.1f}%", color=C["accent2"]),
    ], style={"display": "flex", "gap": "16px", "flexWrap": "wrap"})

    # Charts
    score_dist = filt["review_score"].value_counts().sort_index().reset_index()
    score_dist.columns = ["score", "count"]

    fig_dist = px.bar(score_dist, x="score", y="count")
    fig_dist.update_layout(**PLOTLY_LAYOUT, title="Review Score Distribution")

    scatter = filt.sample(min(2000, len(filt))) if not empty else filt

    fig_scatter = px.scatter(
        scatter,
        x="delivery_days",
        y="review_score",
        color="review_score",
    )
    fig_scatter.update_layout(**PLOTLY_LAYOUT, title="Review Score vs Delivery Time")

    cat_review = (
        filt.groupby("product_category_name_english")["review_score"]
        .mean()
        .dropna()
        .sort_values()
        .reset_index()
    )

    fig_worst = px.bar(
        cat_review.head(10),
        x="review_score",
        y="product_category_name_english",
        orientation="h",
    )
    fig_worst.update_layout(**PLOTLY_LAYOUT, title="Lowest Rated Categories")

    fig_best = px.bar(
        cat_review.tail(10),
        x="review_score",
        y="product_category_name_english",
        orientation="h",
    )
    fig_best.update_layout(**PLOTLY_LAYOUT, title="Highest Rated Categories")

    # Tags
    tags = []

    if categories:
        for c in categories:
            tags.append(_tag(c.title(), "#fff0f0", C["accent3"], C["accent3"]))

    if min_score and min_score > 1:
        tags.append(_tag(f"{min_score}+ Stars", "#e8fff8", C["accent"], C["accent"]))

    if max_days < 60:
        tags.append(_tag(f"≤ {max_days} Days", "#eef6ff", "#4a90e2", "#4a90e2"))

    if not tags:
        tags = [_tag("All data", "transparent", C["muted"], C.get("border", "#2a2e3e"))]

    return kpis_el, fig_dist, fig_scatter, fig_worst, fig_best, tags