from dash import html

# ── Colour palette ─────────────────────────────────────────────────────────────
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

C_LIGHT = {
    "bg":      "#f4f6f9",
    "card":    "#ffffff",
    "border":  "#e2e6ef",
    "accent":  "#00a884",
    "accent2": "#e05555",
    "accent3": "#d4a000",
    "text":    "#1a1d23",
    "muted":   "#6b7585",
}

# ── Shared Plotly layout ───────────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=C["text"], family="DM Sans, sans-serif"),
    margin=dict(l=20, r=20, t=40, b=20),
    xaxis=dict(gridcolor=C["border"], zeroline=False),
    yaxis=dict(gridcolor=C["border"], zeroline=False),
    legend=dict(bgcolor="rgba(0,0,0,0)"),
)

# ── Reusable KPI card ──────────────────────────────────────────────────────────
def kpi(title, value, sub="", color=C["accent"]):
    return html.Div([
        html.P(title, style={
            "color": C["muted"], "fontSize": "11px",
            "textTransform": "uppercase", "letterSpacing": "1.5px",
            "marginBottom": "4px",
        }),
        html.H3(value, style={
            "color": color, "fontSize": "28px",
            "fontWeight": "700", "margin": "0",
        }),
        html.P(sub, style={"color": C["muted"], "fontSize": "12px", "margin": "0"}),
    ], style={
        "background":   C["card"],
        "border":       f"1px solid {C['border']}",
        "borderTop":    f"3px solid {color}",
        "borderRadius": "10px",
        "padding":      "18px 22px",
        "flex":         "1",
        "minWidth":     "160px",
    })

    # ─────────────────────────────────────────────
# MOBILE PLOTLY LAYOUT (Compact Charts)
# ─────────────────────────────────────────────

MOBILE_PLOTLY_LAYOUT = {
    "margin": dict(l=30, r=10, t=35, b=30),
    "title": {"font": {"size": 13}},
    "legend": {
        "font": {"size": 10},
        "orientation": "h",
        "y": -0.25
    },
    "xaxis": {
        "tickfont": {"size": 10},
        "title": {"font": {"size": 11}}
    },
    "yaxis": {
        "tickfont": {"size": 10},
        "title": {"font": {"size": 11}}
    }
}