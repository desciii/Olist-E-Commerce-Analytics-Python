from dash import html
from theme import C


def page_about():
    def info_card(title, body, icon=""):
        return html.Div([
            html.Div(icon, style={"fontSize": "28px", "marginBottom": "10px"}),
            html.H4(title, style={"color": C["accent"], "fontFamily": "'Space Grotesk'", "marginBottom": "8px"}),
            html.P(body,  style={"color": C["muted"], "fontSize": "14px", "lineHeight": "1.7",
                                  "whiteSpace": "pre-line"}),
        ], style={
            "background":   C["card"],
            "border":       f"1px solid {C['border']}",
            "borderRadius": "12px",
            "padding":      "24px",
            "flex":         "1",
            "minWidth":     "220px",
        })

    return html.Div([
        html.H1("About This Dashboard",
                style={"fontFamily": "'Space Grotesk'", "fontWeight": "700", "marginBottom": "8px"}),
        html.P("What this tool is, what it solves, and where the data comes from.",
               style={"color": C["muted"], "marginBottom": "36px"}),

        html.Div([
            info_card(
                "Business Problem",
                "E-commerce operators need visibility into order performance, delivery reliability, "
                "and customer satisfaction. This dashboard helps operations and marketing teams "
                "identify bottlenecks and areas of improvement.",
                "🎯",
            ),
            info_card(
                "Who It's For",
                "Operations managers tracking delivery KPIs, marketing teams analyzing customer "
                "satisfaction by product category, and finance teams reviewing payment trends.",
                "👥",
            ),
            info_card(
                "Key Questions Answered",
                "• Which states have the worst delivery times?\n"
                "• What product categories get the worst reviews?\n"
                "• What payment methods drive the most revenue?\n"
                "• How is revenue trending month over month?",
                "❓",
            ),
        ], style={"display": "flex", "gap": "16px", "flexWrap": "wrap", "marginBottom": "24px"}),

        html.Div([
            html.H4("Dataset Source", style={"color": C["accent"], "fontFamily": "'Space Grotesk'"}),
            html.P(
                "This dashboard uses the publicly available Olist Brazilian E-Commerce dataset, "
                "published on Kaggle. It contains 100,000+ orders from 2016–2018 across multiple "
                "marketplaces in Brazil, with information on orders, payments, delivery, reviews, "
                "products, and sellers.",
                style={"color": C["muted"], "lineHeight": "1.8"},
            ),
            html.A(
                "→ View Dataset on Kaggle",
                href="https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce",
                target="_blank",
                style={"color": C["accent"], "fontWeight": "600",
                       "textDecoration": "none", "fontSize": "14px"},
            ),
        ], style={
            "background":   C["card"],
            "border":       f"1px solid {C['border']}",
            "borderRadius": "12px",
            "padding":      "28px",
        }),
    ])