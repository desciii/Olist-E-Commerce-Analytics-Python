from dash import dcc, html
import plotly.express as px

from data_loader import delivered
from theme import C, PLOTLY_LAYOUT, kpi


def page_delivery():
    d = delivered.copy()

    avg_days = d["delivery_days"].mean()
    late_pct = d["late"].mean() * 100

    # Late delivery rate by state (top 15)
    late_by_state = (
        d.groupby("customer_state")["late"]
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

    # Delivery time distribution
    fig_hist = px.histogram(
        d[d["delivery_days"] < 60], x="delivery_days", nbins=40,
        color_discrete_sequence=[C["accent"]],
        title="Distribution of Delivery Times (days)",
    )
    fig_hist.update_layout(**PLOTLY_LAYOUT)

    return html.Div([
        html.H1("Delivery Performance",
                style={"fontFamily": "'Space Grotesk'", "fontWeight": "700", "marginBottom": "8px"}),
        html.P("How fast and reliably are orders delivered?",
               style={"color": C["muted"], "marginBottom": "28px"}),

        html.Div([
            kpi("Avg Delivery Time",  f"{avg_days:.1f} days"),
            kpi("Late Delivery Rate", f"{late_pct:.1f}%", color=C["accent2"]),
        ], style={"display": "flex", "gap": "16px", "marginBottom": "28px"}),

        html.Div([
            html.Div(dcc.Graph(figure=fig_late, config={"displayModeBar": False}),
                     style={"flex": "1", "background": C["card"], "borderRadius": "12px",
                            "border": f"1px solid {C['border']}", "padding": "8px"}),
            html.Div(dcc.Graph(figure=fig_hist, config={"displayModeBar": False}),
                     style={"flex": "1", "background": C["card"], "borderRadius": "12px",
                            "border": f"1px solid {C['border']}", "padding": "8px"}),
        ], style={"display": "flex", "gap": "16px"}),
    ])