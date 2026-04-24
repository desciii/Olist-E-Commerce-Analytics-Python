from dash import dcc, html
import plotly.express as px

from data_loader import payments
from theme import C, PLOTLY_LAYOUT


def page_payments():
    # Payment type breakdown
    pay_type = payments["payment_type"].value_counts().reset_index()
    pay_type.columns = ["type", "count"]
    fig_type = px.pie(
        pay_type, names="type", values="count",
        color_discrete_sequence=[C["accent"], C["accent2"], C["accent3"], "#4a90e2"],
        title="Payment Type Breakdown",
    )
    fig_type.update_layout(**PLOTLY_LAYOUT)
    fig_type.update_traces(textfont_color=C["text"])

    # Revenue by payment type
    rev_by_type = payments.groupby("payment_type")["payment_value"].sum().reset_index()
    fig_rev = px.bar(
        rev_by_type, x="payment_type", y="payment_value",
        color_discrete_sequence=[C["accent3"]], title="Revenue by Payment Type",
    )
    fig_rev.update_layout(**PLOTLY_LAYOUT)

    # Installment plan distribution
    install = payments[payments["payment_installments"] > 0]
    install_dist = install["payment_installments"].value_counts().sort_index().reset_index()
    install_dist.columns = ["installments", "count"]
    fig_install = px.bar(
        install_dist, x="installments", y="count",
        color_discrete_sequence=[C["accent"]], title="Installment Plan Distribution",
    )
    fig_install.update_layout(**PLOTLY_LAYOUT)

    return html.Div([
        html.H1("Payment Insights",
                style={"fontFamily": "'Space Grotesk'", "fontWeight": "700", "marginBottom": "8px"}),
        html.P("How are customers paying, and how much?",
               style={"color": C["muted"], "marginBottom": "28px"}),

        html.Div([
            html.Div(dcc.Graph(figure=fig_type, config={"displayModeBar": False}),
                     style={"flex": "1", "background": C["card"], "borderRadius": "12px",
                            "border": f"1px solid {C['border']}", "padding": "8px"}),
            html.Div(dcc.Graph(figure=fig_rev,  config={"displayModeBar": False}),
                     style={"flex": "1", "background": C["card"], "borderRadius": "12px",
                            "border": f"1px solid {C['border']}", "padding": "8px"}),
        ], style={"display": "flex", "gap": "16px", "marginBottom": "16px"}),

        html.Div(
            dcc.Graph(figure=fig_install, config={"displayModeBar": False}),
            style={"background": C["card"], "borderRadius": "12px",
                   "border": f"1px solid {C['border']}", "padding": "8px"},
        ),
    ])