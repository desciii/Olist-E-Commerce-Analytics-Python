from dash import dcc, html
import plotly.express as px

from data_loader import df
from theme import C, PLOTLY_LAYOUT, kpi


def page_overview():
    total_orders  = len(df["order_id"].unique())
    total_rev     = df["payment_value"].sum()
    avg_review    = df["review_score"].mean()
    delivered_pct = (df["order_status"] == "delivered").mean() * 100

    # Monthly revenue trend
    monthly = df.groupby("month")["payment_value"].sum().reset_index()
    fig_trend = px.area(monthly, x="month", y="payment_value",
                        color_discrete_sequence=[C["accent"]])
    fig_trend.update_layout(**PLOTLY_LAYOUT, title="Monthly Revenue")
    fig_trend.update_traces(line_color=C["accent"], fillcolor="rgba(0,212,170,0.1)")

    # Order status pie
    status_counts = df["order_status"].value_counts().reset_index()
    status_counts.columns = ["status", "count"]
    fig_status = px.pie(
        status_counts, names="status", values="count",
        color_discrete_sequence=[C["accent"], C["accent2"], C["accent3"], "#6b7585", "#4a90e2"],
    )
    fig_status.update_layout(**PLOTLY_LAYOUT, title="Order Status Breakdown")
    fig_status.update_traces(textfont_color=C["text"])

    return html.Div([
        html.H1("Overview", style={"fontFamily": "'Space Grotesk'", "fontWeight": "700", "marginBottom": "8px"}),
        html.P("High-level snapshot of the Olist marketplace.", style={"color": C["muted"], "marginBottom": "28px"}),

        html.Div([
            kpi("Total Orders",     f"{total_orders:,}"),
            kpi("Total Revenue",    f"R$ {total_rev:,.0f}",  color=C["accent3"]),
            kpi("Avg Review Score", f"{avg_review:.2f} / 5", color=C["accent2"]),
            kpi("Delivery Rate",    f"{delivered_pct:.1f}%", color="#4a90e2"),
        ], style={"display": "flex", "gap": "16px", "flexWrap": "wrap", "marginBottom": "28px"}),

        html.Div([
            html.Div(dcc.Graph(figure=fig_trend,  config={"displayModeBar": False}),
                     style={"flex": "2", "background": C["card"], "borderRadius": "12px",
                            "border": f"1px solid {C['border']}", "padding": "8px"}),
            html.Div(dcc.Graph(figure=fig_status, config={"displayModeBar": False}),
                     style={"flex": "1", "background": C["card"], "borderRadius": "12px",
                            "border": f"1px solid {C['border']}", "padding": "8px"}),
        ], style={"display": "flex", "gap": "16px"}),
    ])