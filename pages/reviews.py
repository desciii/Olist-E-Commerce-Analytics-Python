from dash import dcc, html, Input, Output, callback
import plotly.express as px
import pandas as pd

from data_loader import df
from theme import C, PLOTLY_LAYOUT, kpi

# ── Module-level pre-computation ─────────────────────────────
_d = df.copy()
_d["product_category_name_english"] = (
    _d["product_category_name_english"].astype("category")
)

_CAT_OPTIONS = [
    {"label": c.replace("_", " ").title(), "value": c}
    for c in sorted(_d["product_category_name_english"].dropna().unique())
]

_SCORE_OPTIONS = [
    {"label": f"{i} Stars & Up", "value": i}
    for i in range(1, 6)
]

# Pre-compute full category rating aggregation once at startup.
# Callbacks will slice this instead of re-grouping the raw frame.
_BASE_CAT_REVIEW = (
    _d.groupby("product_category_name_english", observed=True)["review_score"]
    .mean()
    .dropna()
    .sort_values()
    .reset_index()
)

# ── Styles ───────────────────────────────────────────────────
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

# ── Helpers ──────────────────────────────────────────────────
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


def _chart_card(graph, color=C["accent"]):
    return html.Div(
        dcc.Loading(type="circle", color=color, children=graph),
        className="rv-chart-card",
        style={
            "background": C.get("card", "#24293e"),
            "borderRadius": "12px",
            "border": f"1px solid {C['border']}",
            "padding": "12px",
        },
    )


# ── Layout ───────────────────────────────────────────────────
def page_reviews():
    return html.Div([
        html.H1(
            "Customer Reviews",
            style={"fontFamily": "'Space Grotesk'", "fontWeight": "700"},
        ),
        html.P(
            "What drives customer satisfaction?",
            style={"color": C["muted"], "marginBottom": "24px"},
        ),

        # FILTER BAR
        html.Div([
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

        # CHART GRID
        html.Div([
            _chart_card(dcc.Graph(id="rv-dist-chart",  config={"displayModeBar": False}), color=C["accent"]),
            _chart_card(dcc.Graph(id="rv-box-chart",   config={"displayModeBar": False}), color=C["accent3"]),
            _chart_card(dcc.Graph(id="rv-worst-chart", config={"displayModeBar": False}), color=C["accent2"]),
            _chart_card(dcc.Graph(id="rv-best-chart",  config={"displayModeBar": False}), color="#54a0ff"),
        ], className="rv-charts-grid"),
    ])


# ── Callbacks ────────────────────────────────────────────────
@callback(
    Output("rv-cat-filter",      "value"),
    Output("rv-minscore-filter", "value"),
    Output("rv-days-filter",     "value"),
    Input("rv-reset-btn",        "n_clicks"),
    prevent_initial_call=True,
)
def _reset(_):
    return [], 1, 60


@callback(
    Output("rv-kpis",        "children"),
    Output("rv-dist-chart",  "figure"),
    Output("rv-box-chart",   "figure"),
    Output("rv-worst-chart", "figure"),
    Output("rv-best-chart",  "figure"),
    Output("rv-filter-tags", "children"),
    Input("rv-cat-filter",      "value"),
    Input("rv-minscore-filter", "value"),
    Input("rv-days-filter",     "value"),
)
def _update(categories, min_score, max_days):

    # ── Single-pass boolean mask filter ──────────────────────
    mask = pd.Series(True, index=_d.index)

    if categories:
        mask &= _d["product_category_name_english"].isin(categories)
    if min_score and min_score > 1:
        mask &= _d["review_score"] >= min_score
    if max_days:
        mask &= _d["delivery_days"] <= max_days

    filt = _d[mask]
    empty = filt.empty

    # ── KPI aggregations ─────────────────────────────────────
    scores = filt["review_score"] if not empty else pd.Series(dtype=float)

    avg_score = scores.mean()      if not empty else 0.0
    n_reviews = scores.count()     if not empty else 0
    pct_5star = (scores == 5).mean() * 100 if not empty else 0.0
    pct_1star = (scores == 1).mean() * 100 if not empty else 0.0

    kpis_el = html.Div([
        kpi("Avg Review Score", f"{avg_score:.2f} / 5", color=C["accent3"]),
        kpi("Total Reviews",    f"{n_reviews:,}"),
        kpi("5-Star Rate",      f"{pct_5star:.1f}%",    color=C["accent"]),
        kpi("1-Star Rate",      f"{pct_1star:.1f}%",    color=C["accent2"]),
    ], style={"display": "flex", "gap": "16px", "flexWrap": "wrap"})

    # ── Review Score Distribution ─────────────────────────────
    score_dist = (
        scores.value_counts()
        .sort_index()
        .reset_index()
    )
    score_dist.columns = ["score", "count"]

    fig_dist = px.bar(score_dist, x="score", y="count")
    fig_dist.update_layout(**PLOTLY_LAYOUT, title="Review Score Distribution")

    # ── Box Plot ──────────────────────────────────────────────
    box_data = (
        filt.dropna(subset=["delivery_days", "review_score"])
        .sample(min(5000, len(filt)), random_state=42)
    )
    box_data = box_data.assign(
        star=box_data["review_score"].astype(int).astype(str) + " Star"
    )

    fig_box = px.box(
        box_data,
        x="star",
        y="delivery_days",
        color="star",
        color_discrete_sequence=[
            C["accent2"], "#ff9f43", C["accent3"], "#54a0ff", C["accent"],
        ],
        category_orders={"star": ["1 Star", "2 Star", "3 Star", "4 Star", "5 Star"]},
    )
    fig_box.update_layout(**PLOTLY_LAYOUT, title="Delivery Days by Review Score", showlegend=False)
    fig_box.update_yaxes(title="Delivery Days")
    fig_box.update_xaxes(title="Review Score")
    fig_box.update_traces(boxpoints=False, hovertemplate=None)

    # ── Category Ratings (slice pre-computed aggregation) ─────
    if categories:
        # Only re-aggregate for the selected subset — still far cheaper
        # than grouping the full raw frame every time
        cat_review = (
            filt.groupby("product_category_name_english", observed=True)["review_score"]
            .mean()
            .dropna()
            .sort_values()
            .reset_index()
        )
    else:
        # No category filter: just slice the pre-built table
        cat_review = _BASE_CAT_REVIEW.copy()

    if min_score > 1 or (max_days and max_days < 60):
        # Score/days filters change the per-category mean — must re-aggregate
        cat_review = (
            filt.groupby("product_category_name_english", observed=True)["review_score"]
            .mean()
            .dropna()
            .sort_values()
            .reset_index()
        )

    fig_worst = px.bar(cat_review.head(10), x="review_score", y="product_category_name_english", orientation="h")
    fig_worst.update_layout(**PLOTLY_LAYOUT, title="Lowest Rated Categories")

    fig_best = px.bar(cat_review.tail(10), x="review_score", y="product_category_name_english", orientation="h")
    fig_best.update_layout(**PLOTLY_LAYOUT, title="Highest Rated Categories")

    # ── Filter Tags ───────────────────────────────────────────
    tags = []

    if categories:
        tags += [_tag(c.title(), "#fff0f0", C["accent3"], C["accent3"]) for c in categories]
    if min_score and min_score > 1:
        tags.append(_tag(f"{min_score}+ Stars", "#e8fff8", C["accent"], C["accent"]))
    if max_days and max_days < 60:
        tags.append(_tag(f"≤ {max_days} Days", "#eef6ff", "#4a90e2", "#4a90e2"))
    if not tags:
        tags = [_tag("All data", "transparent", C["muted"], C.get("border", "#2a2e3e"))]

    return kpis_el, fig_dist, fig_box, fig_worst, fig_best, tags