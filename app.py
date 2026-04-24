import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os

# ─────────────────────────────────────────
#  LOAD & MERGE DATA
# ─────────────────────────────────────────
BASE = os.path.join(os.getcwd(), "data")

orders   = pd.read_csv(f"{BASE}/olist_orders_dataset.csv")
items    = pd.read_csv(f"{BASE}/olist_order_items_dataset.csv")
reviews  = pd.read_csv(f"{BASE}/olist_order_reviews_dataset.csv")
customers= pd.read_csv(f"{BASE}/olist_customers_dataset.csv")
payments = pd.read_csv(f"{BASE}/olist_order_payments_dataset.csv")
products = pd.read_csv(f"{BASE}/olist_products_dataset.csv")
category = pd.read_csv(f"{BASE}/product_category_name_translation.csv")

# Merge
df = orders.merge(items, on="order_id", how="left")
df = df.merge(reviews[["order_id","review_score"]].drop_duplicates("order_id"), on="order_id", how="left")
df = df.merge(customers, on="customer_id", how="left")
df = df.merge(payments[["order_id","payment_type","payment_value"]].drop_duplicates("order_id"), on="order_id", how="left")
df = df.merge(products[["product_id","product_category_name"]], on="product_id", how="left")
df = df.merge(category, on="product_category_name", how="left")

# Date parsing
df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])
df["order_delivered_customer_date"] = pd.to_datetime(df["order_delivered_customer_date"])
df["order_estimated_delivery_date"] = pd.to_datetime(df["order_estimated_delivery_date"])
df["month"] = df["order_purchase_timestamp"].dt.to_period("M").astype(str)
df["delivery_days"] = (df["order_delivered_customer_date"] - df["order_purchase_timestamp"]).dt.days
df["late"] = df["order_delivered_customer_date"] > df["order_estimated_delivery_date"]
df["year"] = df["order_purchase_timestamp"].dt.year

delivered = df[df["order_status"] == "delivered"].copy()

# ─────────────────────────────────────────
#  COLOUR PALETTE & THEME
# ─────────────────────────────────────────
C = {
    "bg":      "#0d0f14",
    "card":    "#161a23",
    "border":  "#252b38",
    "accent":  "#00d4aa",
    "accent2": "#ff6b6b",
    "accent3": "#ffd166",
    "text":    "#e8ecf1",
    "muted":   "#6b7585",
}

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=C["text"], family="DM Sans, sans-serif"),
    margin=dict(l=20, r=20, t=40, b=20),
    xaxis=dict(gridcolor=C["border"], zeroline=False),
    yaxis=dict(gridcolor=C["border"], zeroline=False),
    legend=dict(bgcolor="rgba(0,0,0,0)"),
)

# ─────────────────────────────────────────
#  HELPER: KPI CARD
# ─────────────────────────────────────────
def kpi(title, value, sub="", color=C["accent"]):
    return html.Div([
        html.P(title, style={"color": C["muted"], "fontSize": "11px",
                              "textTransform": "uppercase", "letterSpacing": "1.5px",
                              "marginBottom": "4px"}),
        html.H3(value, style={"color": color, "fontSize": "28px",
                               "fontWeight": "700", "margin": "0"}),
        html.P(sub, style={"color": C["muted"], "fontSize": "12px", "margin": "0"}),
    ], style={
        "background": C["card"],
        "border": f"1px solid {C['border']}",
        "borderTop": f"3px solid {color}",
        "borderRadius": "10px",
        "padding": "18px 22px",
        "flex": "1",
        "minWidth": "160px",
    })

# ─────────────────────────────────────────
#  APP
# ─────────────────────────────────────────
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;700&family=Space+Grotesk:wght@600;700&display=swap",
    ],
    title="Olist E-Commerce Analytics",
)
server = app.server  # for Render deployment

# ─────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────
sidebar = html.Div([
    html.Div([
        html.Div("◈", style={"fontSize": "28px", "color": C["accent"]}),
        html.H2("Olist", style={"color": C["text"], "fontFamily": "'Space Grotesk'",
                                  "fontWeight": "700", "margin": "0", "fontSize": "22px"}),
        html.P("E-Commerce Analytics", style={"color": C["muted"], "fontSize": "11px",
                                               "margin": "0", "letterSpacing": "1px"}),
    ], style={"marginBottom": "36px"}),

    *[html.Button([icon, " ", label], id=f"btn-{tid}", n_clicks=0, style={
        "display": "block", "width": "100%", "textAlign": "left",
        "background": "transparent", "border": "none",
        "color": C["muted"], "padding": "10px 14px", "borderRadius": "8px",
        "fontSize": "13px", "cursor": "pointer", "marginBottom": "4px",
        "fontFamily": "'DM Sans', sans-serif",
    }) for icon, label, tid in [
        ("🏠", "Overview", "overview"),
        ("📦", "Delivery", "delivery"),
        ("⭐", "Reviews", "reviews"),
        ("💳", "Payments", "payments"),
        ("📖", "About", "about"),
    ]],

    html.Div([
        html.P("Dataset", style={"color": C["muted"], "fontSize": "10px",
                                   "textTransform": "uppercase", "letterSpacing": "1px"}),
        html.A("Kaggle: Olist", href="https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce",
               target="_blank", style={"color": C["accent"], "fontSize": "12px",
                                        "textDecoration": "none"}),
    ], style={"position": "absolute", "bottom": "28px", "left": "24px"}),
], style={
    "width": "200px", "minHeight": "100vh", "background": C["card"],
    "borderRight": f"1px solid {C['border']}", "padding": "28px 20px",
    "position": "fixed", "top": "0", "left": "0", "zIndex": "100",
    "position": "fixed",
})

# ─────────────────────────────────────────
#  PAGE CONTENT AREA
# ─────────────────────────────────────────
content = html.Div(id="page-content", style={
    "marginLeft": "200px", "padding": "36px 40px",
    "minHeight": "100vh", "background": C["bg"],
    "fontFamily": "'DM Sans', sans-serif", "color": C["text"],
})

app.layout = html.Div([
    sidebar,
    content,
    dcc.Store(id="active-tab", data="overview"),
], style={"background": C["bg"]})


# ─────────────────────────────────────────
#  TAB ROUTING
# ─────────────────────────────────────────
@app.callback(
    Output("active-tab", "data"),
    [Input(f"btn-{t}", "n_clicks") for t in ["overview","delivery","reviews","payments","about"]],
    prevent_initial_call=True,
)
def switch_tab(*args):
    ctx = dash.callback_context
    if not ctx.triggered:
        return "overview"
    btn_id = ctx.triggered[0]["prop_id"].split(".")[0]
    return btn_id.replace("btn-", "")


# ─────────────────────────────────────────
#  PAGES
# ─────────────────────────────────────────
def page_overview():
    total_orders = len(df["order_id"].unique())
    total_rev = df["payment_value"].sum()
    avg_review = df["review_score"].mean()
    delivered_pct = (df["order_status"]=="delivered").mean() * 100

    monthly = df.groupby("month")["payment_value"].sum().reset_index()
    fig_trend = px.area(monthly, x="month", y="payment_value",
                        color_discrete_sequence=[C["accent"]])
    fig_trend.update_layout(**PLOTLY_LAYOUT, title="Monthly Revenue")
    fig_trend.update_traces(line_color=C["accent"], fillcolor="rgba(0,212,170,0.1)")

    status_counts = df["order_status"].value_counts().reset_index()
    status_counts.columns = ["status","count"]
    fig_status = px.pie(status_counts, names="status", values="count",
                        color_discrete_sequence=[C["accent"], C["accent2"],
                                                  C["accent3"],"#6b7585","#4a90e2"])
    fig_status.update_layout(**PLOTLY_LAYOUT, title="Order Status Breakdown")
    fig_status.update_traces(textfont_color=C["text"])

    return html.Div([
        html.H1("Overview", style={"fontFamily":"'Space Grotesk'","fontWeight":"700","marginBottom":"8px"}),
        html.P("High-level snapshot of the Olist marketplace.", style={"color":C["muted"],"marginBottom":"28px"}),

        html.Div([
            kpi("Total Orders", f"{total_orders:,}"),
            kpi("Total Revenue", f"R$ {total_rev:,.0f}", color=C["accent3"]),
            kpi("Avg Review Score", f"{avg_review:.2f} / 5", color=C["accent2"]),
            kpi("Delivery Rate", f"{delivered_pct:.1f}%", color="#4a90e2"),
        ], style={"display":"flex","gap":"16px","flexWrap":"wrap","marginBottom":"28px"}),

        html.Div([
            html.Div(dcc.Graph(figure=fig_trend, config={"displayModeBar":False}),
                     style={"flex":"2","background":C["card"],"borderRadius":"12px",
                            "border":f"1px solid {C['border']}","padding":"8px"}),
            html.Div(dcc.Graph(figure=fig_status, config={"displayModeBar":False}),
                     style={"flex":"1","background":C["card"],"borderRadius":"12px",
                            "border":f"1px solid {C['border']}","padding":"8px"}),
        ], style={"display":"flex","gap":"16px"}),
    ])


def page_delivery():
    d = delivered.copy()
    avg_days = d["delivery_days"].mean()
    late_pct = d["late"].mean() * 100

    state_avg = d.groupby("customer_state")["delivery_days"].mean().reset_index()
    fig_map = px.choropleth(state_avg, locations="customer_state",
                            locationmode="geojson-id",
                            color="delivery_days",
                            color_continuous_scale=["#00d4aa","#ffd166","#ff6b6b"],
                            title="Avg Delivery Days by State")
    fig_map.update_layout(**PLOTLY_LAYOUT)

    late_by_state = d.groupby("customer_state")["late"].mean().mul(100).reset_index()
    late_by_state.columns = ["state","late_pct"]
    late_by_state = late_by_state.sort_values("late_pct", ascending=True).tail(15)
    fig_late = px.bar(late_by_state, x="late_pct", y="state", orientation="h",
                      color_discrete_sequence=[C["accent2"]],
                      title="Top 15 States by Late Delivery Rate (%)")
    fig_late.update_layout(**PLOTLY_LAYOUT)

    fig_hist = px.histogram(d[d["delivery_days"]<60], x="delivery_days", nbins=40,
                            color_discrete_sequence=[C["accent"]],
                            title="Distribution of Delivery Times (days)")
    fig_hist.update_layout(**PLOTLY_LAYOUT)

    return html.Div([
        html.H1("Delivery Performance", style={"fontFamily":"'Space Grotesk'","fontWeight":"700","marginBottom":"8px"}),
        html.P("How fast and reliably are orders delivered?", style={"color":C["muted"],"marginBottom":"28px"}),

        html.Div([
            kpi("Avg Delivery Time", f"{avg_days:.1f} days"),
            kpi("Late Delivery Rate", f"{late_pct:.1f}%", color=C["accent2"]),
        ], style={"display":"flex","gap":"16px","marginBottom":"28px"}),

        html.Div([
            html.Div(dcc.Graph(figure=fig_late, config={"displayModeBar":False}),
                     style={"flex":"1","background":C["card"],"borderRadius":"12px",
                            "border":f"1px solid {C['border']}","padding":"8px"}),
            html.Div(dcc.Graph(figure=fig_hist, config={"displayModeBar":False}),
                     style={"flex":"1","background":C["card"],"borderRadius":"12px",
                            "border":f"1px solid {C['border']}","padding":"8px"}),
        ], style={"display":"flex","gap":"16px"}),
    ])


def page_reviews():
    cat_review = delivered.groupby("product_category_name_english")["review_score"].mean().reset_index()
    cat_review.columns = ["category","avg_score"]
    cat_review = cat_review.dropna().sort_values("avg_score")

    worst = cat_review.head(10)
    best  = cat_review.tail(10)

    fig_worst = px.bar(worst, x="avg_score", y="category", orientation="h",
                       color_discrete_sequence=[C["accent2"]], title="10 Worst Rated Categories")
    fig_worst.update_layout(**PLOTLY_LAYOUT)

    fig_best = px.bar(best, x="avg_score", y="category", orientation="h",
                      color_discrete_sequence=[C["accent"]], title="10 Best Rated Categories")
    fig_best.update_layout(**PLOTLY_LAYOUT)

    score_dist = delivered["review_score"].value_counts().sort_index().reset_index()
    score_dist.columns = ["score","count"]
    fig_dist = px.bar(score_dist, x="score", y="count",
                      color_discrete_sequence=[C["accent3"]], title="Review Score Distribution")
    fig_dist.update_layout(**PLOTLY_LAYOUT)

    scatter = delivered[delivered["delivery_days"]<60].dropna(subset=["review_score","delivery_days"])
    fig_scatter = px.scatter(scatter.sample(min(3000, len(scatter))),
                             x="delivery_days", y="review_score",
                             color="review_score",
                             color_continuous_scale=["#ff6b6b","#ffd166","#00d4aa"],
                             title="Review Score vs Delivery Time",
                             opacity=0.5)
    fig_scatter.update_layout(**PLOTLY_LAYOUT)

    return html.Div([
        html.H1("Customer Reviews", style={"fontFamily":"'Space Grotesk'","fontWeight":"700","marginBottom":"8px"}),
        html.P("What drives customer satisfaction?", style={"color":C["muted"],"marginBottom":"28px"}),

        html.Div([
            html.Div(dcc.Graph(figure=fig_dist, config={"displayModeBar":False}),
                     style={"flex":"1","background":C["card"],"borderRadius":"12px",
                            "border":f"1px solid {C['border']}","padding":"8px"}),
            html.Div(dcc.Graph(figure=fig_scatter, config={"displayModeBar":False}),
                     style={"flex":"1","background":C["card"],"borderRadius":"12px",
                            "border":f"1px solid {C['border']}","padding":"8px"}),
        ], style={"display":"flex","gap":"16px","marginBottom":"16px"}),

        html.Div([
            html.Div(dcc.Graph(figure=fig_worst, config={"displayModeBar":False}),
                     style={"flex":"1","background":C["card"],"borderRadius":"12px",
                            "border":f"1px solid {C['border']}","padding":"8px"}),
            html.Div(dcc.Graph(figure=fig_best, config={"displayModeBar":False}),
                     style={"flex":"1","background":C["card"],"borderRadius":"12px",
                            "border":f"1px solid {C['border']}","padding":"8px"}),
        ], style={"display":"flex","gap":"16px"}),
    ])


def page_payments():
    pay_type = payments["payment_type"].value_counts().reset_index()
    pay_type.columns = ["type","count"]
    fig_type = px.pie(pay_type, names="type", values="count",
                      color_discrete_sequence=[C["accent"], C["accent2"], C["accent3"],"#4a90e2"],
                      title="Payment Type Breakdown")
    fig_type.update_layout(**PLOTLY_LAYOUT)
    fig_type.update_traces(textfont_color=C["text"])

    rev_by_type = payments.groupby("payment_type")["payment_value"].sum().reset_index()
    fig_rev = px.bar(rev_by_type, x="payment_type", y="payment_value",
                     color_discrete_sequence=[C["accent3"]], title="Revenue by Payment Type")
    fig_rev.update_layout(**PLOTLY_LAYOUT)

    install = payments[payments["payment_installments"] > 0]
    install_dist = install["payment_installments"].value_counts().sort_index().reset_index()
    install_dist.columns = ["installments","count"]
    fig_install = px.bar(install_dist, x="installments", y="count",
                         color_discrete_sequence=[C["accent"]], title="Installment Plan Distribution")
    fig_install.update_layout(**PLOTLY_LAYOUT)

    return html.Div([
        html.H1("Payment Insights", style={"fontFamily":"'Space Grotesk'","fontWeight":"700","marginBottom":"8px"}),
        html.P("How are customers paying, and how much?", style={"color":C["muted"],"marginBottom":"28px"}),

        html.Div([
            html.Div(dcc.Graph(figure=fig_type, config={"displayModeBar":False}),
                     style={"flex":"1","background":C["card"],"borderRadius":"12px",
                            "border":f"1px solid {C['border']}","padding":"8px"}),
            html.Div(dcc.Graph(figure=fig_rev, config={"displayModeBar":False}),
                     style={"flex":"1","background":C["card"],"borderRadius":"12px",
                            "border":f"1px solid {C['border']}","padding":"8px"}),
        ], style={"display":"flex","gap":"16px","marginBottom":"16px"}),

        html.Div(dcc.Graph(figure=fig_install, config={"displayModeBar":False}),
                 style={"background":C["card"],"borderRadius":"12px",
                        "border":f"1px solid {C['border']}","padding":"8px"}),
    ])


def page_about():
    def info_card(title, body, icon=""):
        return html.Div([
            html.Div(icon, style={"fontSize":"28px","marginBottom":"10px"}),
            html.H4(title, style={"color":C["accent"],"fontFamily":"'Space Grotesk'","marginBottom":"8px"}),
            html.P(body, style={"color":C["muted"],"fontSize":"14px","lineHeight":"1.7"}),
        ], style={"background":C["card"],"border":f"1px solid {C['border']}",
                   "borderRadius":"12px","padding":"24px","flex":"1","minWidth":"220px"})

    return html.Div([
        html.H1("About This Dashboard", style={"fontFamily":"'Space Grotesk'","fontWeight":"700","marginBottom":"8px"}),
        html.P("What this tool is, what it solves, and where the data comes from.",
               style={"color":C["muted"],"marginBottom":"36px"}),

        html.Div([
            info_card("Business Problem",
                "E-commerce operators need visibility into order performance, delivery reliability, "
                "and customer satisfaction. This dashboard helps operations and marketing teams "
                "identify bottlenecks and areas of improvement.", "🎯"),
            info_card("Who It's For",
                "Operations managers tracking delivery KPIs, marketing teams analyzing customer "
                "satisfaction by product category, and finance teams reviewing payment trends.", "👥"),
            info_card("Key Questions Answered",
                "• Which states have the worst delivery times?\n"
                "• What product categories get the worst reviews?\n"
                "• What payment methods drive the most revenue?\n"
                "• How is revenue trending month over month?", "❓"),
        ], style={"display":"flex","gap":"16px","flexWrap":"wrap","marginBottom":"24px"}),

        html.Div([
            html.H4("Dataset Source", style={"color":C["accent"],"fontFamily":"'Space Grotesk'"}),
            html.P("This dashboard uses the publicly available Olist Brazilian E-Commerce dataset, "
                   "published on Kaggle. It contains 100,000+ orders from 2016–2018 across multiple "
                   "marketplaces in Brazil, with information on orders, payments, delivery, reviews, "
                   "products, and sellers.", style={"color":C["muted"],"lineHeight":"1.8"}),
            html.A("→ View Dataset on Kaggle",
                   href="https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce",
                   target="_blank",
                   style={"color":C["accent"],"fontWeight":"600","textDecoration":"none","fontSize":"14px"}),
        ], style={"background":C["card"],"border":f"1px solid {C['border']}",
                   "borderRadius":"12px","padding":"28px"}),
    ])


# ─────────────────────────────────────────
#  RENDER PAGE
# ─────────────────────────────────────────
@app.callback(Output("page-content", "children"), Input("active-tab", "data"))
def render(tab):
    pages = {
        "overview": page_overview,
        "delivery": page_delivery,
        "reviews":  page_reviews,
        "payments": page_payments,
        "about":    page_about,
    }
    return pages.get(tab, page_overview)()


if __name__ == "__main__":
    app.run(debug=True)