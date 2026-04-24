from dash import dcc, html
import plotly.express as px

from data_loader import delivered
from theme import C, PLOTLY_LAYOUT


def page_reviews():
    # Category ratings
    cat_review = (
        delivered.groupby("product_category_name_english")["review_score"]
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

    # Score distribution
    score_dist = delivered["review_score"].value_counts().sort_index().reset_index()
    score_dist.columns = ["score", "count"]
    fig_dist = px.bar(
        score_dist, x="score", y="count",
        color_discrete_sequence=[C["accent3"]], title="Review Score Distribution",
    )
    fig_dist.update_layout(**PLOTLY_LAYOUT)

    # Score vs delivery time scatter
    scatter = (
        delivered[delivered["delivery_days"] < 60]
        .dropna(subset=["review_score", "delivery_days"])
    )
    fig_scatter = px.scatter(
        scatter.sample(min(3000, len(scatter))),
        x="delivery_days", y="review_score",
        color="review_score",
        color_continuous_scale=["#ff6b6b", "#ffd166", "#00d4aa"],
        title="Review Score vs Delivery Time",
        opacity=0.5,
    )
    fig_scatter.update_layout(**PLOTLY_LAYOUT)

    return html.Div([
        html.H1("Customer Reviews",
                style={"fontFamily": "'Space Grotesk'", "fontWeight": "700", "marginBottom": "8px"}),
        html.P("What drives customer satisfaction?",
               style={"color": C["muted"], "marginBottom": "28px"}),

        html.Div([
            html.Div(dcc.Graph(figure=fig_dist,    config={"displayModeBar": False}),
                     style={"flex": "1", "background": C["card"], "borderRadius": "12px",
                            "border": f"1px solid {C['border']}", "padding": "8px"}),
            html.Div(dcc.Graph(figure=fig_scatter, config={"displayModeBar": False}),
                     style={"flex": "1", "background": C["card"], "borderRadius": "12px",
                            "border": f"1px solid {C['border']}", "padding": "8px"}),
        ], style={"display": "flex", "gap": "16px", "marginBottom": "16px"}),

        html.Div([
            html.Div(dcc.Graph(figure=fig_worst, config={"displayModeBar": False}),
                     style={"flex": "1", "background": C["card"], "borderRadius": "12px",
                            "border": f"1px solid {C['border']}", "padding": "8px"}),
            html.Div(dcc.Graph(figure=fig_best,  config={"displayModeBar": False}),
                     style={"flex": "1", "background": C["card"], "borderRadius": "12px",
                            "border": f"1px solid {C['border']}", "padding": "8px"}),
        ], style={"display": "flex", "gap": "16px"}),
    ])