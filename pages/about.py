from dash import html
from theme import C


def page_about():

    def section_header(title):
        return html.H3(title, style={
            "fontFamily": "'Space Grotesk'",
            "fontWeight": "700",
            "color": C["text"],
            "marginBottom": "16px",
            "marginTop": "0",
            "fontSize": "18px",
            "letterSpacing": "-0.01em",
        })

    def info_card(title, body, accent=None):
        color = accent or C["accent"]
        return html.Div([
            html.H4(title, style={
                "color": color,
                "fontFamily": "'Space Grotesk'",
                "marginBottom": "8px",
                "fontSize": "15px",
                "fontWeight": "700",
            }),
            html.P(body, style={
                "color": C["muted"],
                "fontSize": "13.5px",
                "lineHeight": "1.75",
                "whiteSpace": "pre-line",
                "margin": "0",
            }),
        ], style={
            "background":   C["card"],
            "border":       f"1px solid {C['border']}",
            "borderRadius": "12px",
            "padding":      "22px",
            "flex":         "1",
            "minWidth":     "220px",
        })

    def metric_pill(label, value, color=None):
        return html.Div([
            html.Div(value, style={
                "fontSize": "26px",
                "fontWeight": "700",
                "color": color or C["accent"],
                "fontFamily": "'Space Grotesk'",
                "lineHeight": "1",
                "marginBottom": "4px",
            }),
            html.Div(label, style={
                "fontSize": "11px",
                "color": C["muted"],
                "textTransform": "uppercase",
                "letterSpacing": "0.08em",
                "fontWeight": "600",
            }),
        ], style={
            "background": C["card"],
            "border": f"1px solid {C['border']}",
            "borderRadius": "10px",
            "padding": "16px 22px",
            "textAlign": "center",
            "flex": "1",
            "minWidth": "120px",
        })

    def feature_row(tab, description, filters):
        return html.Div([
            html.Div([
                html.Span(tab, style={
                    "fontWeight": "700",
                    "color": C["accent"],
                    "fontFamily": "'Space Grotesk'",
                    "fontSize": "14px",
                    "display": "block",
                    "marginBottom": "4px",
                }),
                html.Span(description, style={
                    "color": C["text"],
                    "fontSize": "13.5px",
                }),
            ], style={"flex": "2"}),
            html.Div(filters, style={
                "color": C["muted"],
                "fontSize": "13px",
                "flex": "3",
                "lineHeight": "1.6",
            }),
        ], style={
            "display": "flex",
            "gap": "24px",
            "padding": "14px 0",
            "borderBottom": f"1px solid {C['border']}",
            "alignItems": "flex-start",
        })

    def bullet(text):
        return html.Li(text, style={
            "color": C["muted"],
            "fontSize": "13.5px",
            "lineHeight": "1.8",
            "marginBottom": "2px",
        })

    return html.Div([

        # ── Hero ────────────────────────────────────────────
        html.H1("About This Dashboard", style={
            "fontFamily": "'Space Grotesk'", "fontWeight": "700", "marginBottom": "6px"
        }),
        html.P(
            "Olist E-Commerce Analytics — a business intelligence dashboard built on a real-world "
            "Brazilian marketplace dataset.",
            style={"color": C["muted"], "marginBottom": "36px", "fontSize": "15px"}
        ),

        # ── Dataset at a glance ─────────────────────────────
        html.Div([
            metric_pill("Orders",        "100k+"),
            metric_pill("Time Period",   "2016–2018", color=C["accent2"]),
            metric_pill("Brazilian States", "27",     color=C["accent3"]),
            metric_pill("Product Categories", "70+",  color="#4a90e2"),
            metric_pill("Data Tables",   "9",          color=C["accent"]),
        ], style={"display": "flex", "gap": "12px", "flexWrap": "wrap", "marginBottom": "28px"}),

        # ── Business Problem ─────────────────────────────────
        html.Div([
            section_header("Business Problem"),
            html.P(
                "E-commerce businesses generate enormous volumes of transactional data, but raw data alone "
                "doesn't drive decisions — visibility does. Olist, one of Brazil's largest online marketplaces, "
                "faces operational challenges that are common across the industry:",
                style={"color": C["muted"], "fontSize": "13.5px", "lineHeight": "1.8", "marginBottom": "12px"}
            ),
            html.Ul([
                bullet("Delivery delays that vary significantly by region, hurting customer satisfaction"),
                bullet("Inconsistent review scores across product categories, signaling quality or expectation gaps"),
                bullet("Unclear payment trends that make it harder to optimize checkout and financing options"),
                bullet("Lack of a unified view of order status, revenue, and fulfillment across time"),
            ], style={"paddingLeft": "20px", "marginBottom": "12px"}),
            html.P(
                "This dashboard centralizes those insights into one interactive tool, enabling data-driven "
                "decision-making for operations, marketing, and finance teams.",
                style={"color": C["muted"], "fontSize": "13.5px", "lineHeight": "1.8", "margin": "0"}
            ),
        ], style={
            "background": C["card"],
            "border": f"1px solid {C['border']}",
            "borderRadius": "12px",
            "padding": "28px",
            "marginBottom": "20px",
        }),

        # ── Who it's for / What it answers ──────────────────
        html.Div([
            info_card(
                "Who Is It For?",
                "• Operations Managers — monitoring delivery KPIs and late-order rates by region\n"
                "• Marketing Teams — identifying low-rated product categories to address\n"
                "• Finance Teams — tracking revenue by payment method and time period\n"
                "• Business Analysts — exploring trends and correlations in the data",
            ),
            info_card(
                "Key Questions Answered",
                "• Which states have the highest late delivery rates?\n"
                "• How long does delivery take on average — and for whom?\n"
                "• Which product categories drive the worst reviews?\n"
                "• Does faster delivery correlate with higher review scores?\n"
                "• What payment methods generate the most revenue?\n"
                "• How is monthly revenue trending over time?",
                accent=C["accent2"],
            ),
            info_card(
                "Business Value",
                "• Pinpoint underperforming logistics regions for targeted improvement\n"
                "• Prioritize product categories with low satisfaction scores\n"
                "• Optimize payment offerings based on revenue and usage data\n"
                "• Track business health over time with monthly revenue trends",
                accent=C["accent3"],
            ),
        ], style={"display": "flex", "gap": "16px", "flexWrap": "wrap", "marginBottom": "20px"}),

        # ── Dashboard Feature Map ────────────────────────────
        html.Div([
            section_header("Dashboard Pages & Features"),
            feature_row(
                "Overview",
                "High-level marketplace snapshot with monthly revenue trend and order status breakdown.",
                "Filters: Order ID search, order status, date range (month/year). KPIs: total orders, revenue, avg review score, delivery rate."
            ),
            feature_row(
                "Delivery Performance",
                "Analyzes how fast and reliably orders are delivered across Brazilian states.",
                "Filters: Customer state, max delivery days, delivery status (all / late / on-time). Charts: late rate by state, delivery time distribution."
            ),
            feature_row(
                "Customer Reviews",
                "Explores what drives customer satisfaction — by product category and delivery time.",
                "Filters: Product category, min review score, max delivery days. Charts: score distribution, score vs delivery scatter, best/worst categories."
            ),
            feature_row(
                "Payment Insights",
                "Breaks down how customers pay and how payment behavior affects revenue.",
                "Filters: Payment type, max installments, min order value. Charts: payment type pie, revenue by type, installment distribution."
            ),
            html.Div(style={"borderBottom": "none"}),  # remove last divider
        ], style={
            "background": C["card"],
            "border": f"1px solid {C['border']}",
            "borderRadius": "12px",
            "padding": "28px",
            "marginBottom": "20px",
        }),

        # ── Analytics Techniques ─────────────────────────────
        html.Div([
            section_header("Analytics Techniques Used"),
            html.Div([
                html.Div([
                    html.Div([
                        html.Span("Descriptive Analytics", style={
                            "fontWeight": "700", "color": C["accent"], "fontSize": "13.5px"
                        }),
                        html.P(
                            "KPIs such as average delivery time, late delivery rate, average review score, "
                            "and total revenue summarize the current state of the business.",
                            style={"color": C["muted"], "fontSize": "13px", "lineHeight": "1.7", "marginTop": "4px"}
                        ),
                    ], style={"marginBottom": "16px"}),
                    html.Div([
                        html.Span("Diagnostic Analytics", style={
                            "fontWeight": "700", "color": C["accent2"], "fontSize": "13.5px"
                        }),
                        html.P(
                            "The review score vs. delivery time scatter plot and state-level late delivery "
                            "breakdowns help identify *why* satisfaction or performance varies.",
                            style={"color": C["muted"], "fontSize": "13px", "lineHeight": "1.7", "marginTop": "4px"}
                        ),
                    ]),
                ], style={"flex": "1"}),
                html.Div([
                    html.Div([
                        html.Span("Trend Analysis", style={
                            "fontWeight": "700", "color": C["accent3"], "fontSize": "13.5px"
                        }),
                        html.P(
                            "The monthly revenue area chart on the Overview page tracks business growth "
                            "over the 2016–2018 period, revealing seasonality and growth patterns.",
                            style={"color": C["muted"], "fontSize": "13px", "lineHeight": "1.7", "marginTop": "4px"}
                        ),
                    ], style={"marginBottom": "16px"}),
                    html.Div([
                        html.Span("Comparative Analysis", style={
                            "fontWeight": "700", "color": "#4a90e2", "fontSize": "13.5px"
                        }),
                        html.P(
                            "Best vs. worst rated product categories, state-by-state delivery performance, "
                            "and payment method breakdowns allow direct comparison across segments.",
                            style={"color": C["muted"], "fontSize": "13px", "lineHeight": "1.7", "marginTop": "4px"}
                        ),
                    ]),
                ], style={"flex": "1"}),
            ], style={"display": "flex", "gap": "32px", "flexWrap": "wrap"}),
        ], style={
            "background": C["card"],
            "border": f"1px solid {C['border']}",
            "borderRadius": "12px",
            "padding": "28px",
            "marginBottom": "20px",
        }),

        # ── Dataset Source ────────────────────────────────────
        html.Div([
            section_header("Dataset Source"),
            html.P(
                "This dashboard uses the publicly available Olist Brazilian E-Commerce Public Dataset, "
                "published on Kaggle by Olist, Brazil's largest department store operating through marketplaces. "
                "The dataset contains 100,000+ real orders placed between 2016 and 2018, covering:",
                style={"color": C["muted"], "lineHeight": "1.8", "fontSize": "13.5px", "marginBottom": "12px"}
            ),
            html.Div([
                html.Div([
                    bullet("Order status and timestamps"),
                    bullet("Customer location (state-level)"),
                    bullet("Product categories and descriptions"),
                    bullet("Payment type, installments, and value"),
                ], style={"flex": "1"}),
                html.Div([
                    bullet("Delivery estimates vs. actual dates"),
                    bullet("Seller information and location"),
                    bullet("Customer review scores and comments"),
                    bullet("Geolocation data for customers and sellers"),
                ], style={"flex": "1"}),
            ], style={"display": "flex", "gap": "24px", "flexWrap": "wrap",
                      "marginBottom": "20px"}),
            html.Div([
                html.A(
                    "→ View Dataset on Kaggle",
                    href="https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce",
                    target="_blank",
                    style={
                        "color": C["accent"],
                        "fontWeight": "700",
                        "textDecoration": "none",
                        "fontSize": "14px",
                        "marginRight": "24px",
                    },
                ),
                html.A(
                    "→ Olist Official Website",
                    href="https://olist.com",
                    target="_blank",
                    style={
                        "color": C["muted"],
                        "fontWeight": "600",
                        "textDecoration": "none",
                        "fontSize": "14px",
                    },
                ),
            ]),
        ], style={
            "background": C["card"],
            "border": f"1px solid {C['border']}",
            "borderRadius": "12px",
            "padding": "28px",
            "marginBottom": "20px",
        }),

        # ── Built With ────────────────────────────────────────
        html.Div([
            section_header("Built With"),
            html.Div([
                html.Div([
                    html.Span("Plotly Dash", style={"color": C["accent"], "fontWeight": "700", "fontSize": "13.5px"}),
                    html.Span(" — Python web framework for analytical dashboards", style={"color": C["muted"], "fontSize": "13.5px"}),
                ], style={"marginBottom": "8px"}),
                html.Div([
                    html.Span("Plotly Express", style={"color": C["accent2"], "fontWeight": "700", "fontSize": "13.5px"}),
                    html.Span(" — Interactive charting library (bar, pie, scatter, histogram, area)", style={"color": C["muted"], "fontSize": "13.5px"}),
                ], style={"marginBottom": "8px"}),
                html.Div([
                    html.Span("Pandas", style={"color": C["accent3"], "fontWeight": "700", "fontSize": "13.5px"}),
                    html.Span(" — Data wrangling, merging, and aggregation across 9 source tables", style={"color": C["muted"], "fontSize": "13.5px"}),
                ], style={"marginBottom": "8px"}),
                html.Div([
                    html.Span("Dash Callbacks", style={"color": "#4a90e2", "fontWeight": "700", "fontSize": "13.5px"}),
                    html.Span(" — Reactive interactivity: all filters update charts and KPIs in real time", style={"color": C["muted"], "fontSize": "13.5px"}),
                ]),
            ]),
        ], style={
            "background": C["card"],
            "border": f"1px solid {C['border']}",
            "borderRadius": "12px",
            "padding": "28px",
        }),

    ])