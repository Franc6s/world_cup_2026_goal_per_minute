from dash import dcc, html

from theme import (
    NAVY, DARK_BLUE, BLUE, MID_BLUE, LIGHT_BLUE, PALE_BLUE,
    GOLD, LIGHT_GOLD, WHITE, OFF_WHITE, TEXT, MUTED, BORDER, CONFED_COLORS,
)

# ============================================================
# HELPERS
# ============================================================
def card(title, value_id=None, value=None):
    display_value = value if value is not None else ""
    return html.Div(
        [
            html.Div(title, style={
                "fontSize": "12px",
                "fontWeight": "700",
                "color": MUTED,
                "textTransform": "uppercase",
                "letterSpacing": "0.8px",
            }),
            html.Div(
                display_value,
                id=value_id,
                style={
                    "fontSize": "28px",
                    "fontWeight": "800",
                    "color": NAVY,
                    "marginTop": "6px",
                },
            ),
        ],
        style={
            "backgroundColor": WHITE,
            "padding": "18px 20px",
            "borderRadius": "14px",
            "border": f"1px solid {BORDER}",
            "boxShadow": "0 4px 16px rgba(6, 26, 45, 0.06)",
            "minHeight": "92px",
        },
    )


def graph_card(title, graph_id, height=430):
    return html.Div(
        [
            html.Div(
                title,
                style={
                    "fontSize": "17px",
                    "fontWeight": "800",
                    "color": NAVY,
                    "marginBottom": "6px",
                },
            ),
            dcc.Graph(
                id=graph_id,
                config={"displayModeBar": False},
                style={"height": f"{height}px"},
            ),
        ],
        style={
            "backgroundColor": WHITE,
            "padding": "16px",
            "borderRadius": "14px",
            "border": f"1px solid {BORDER}",
            "boxShadow": "0 4px 16px rgba(6, 26, 45, 0.05)",
        },
    )


def format_fig(fig, title=None):
    fig.update_layout(
        title=title,
        paper_bgcolor=WHITE,
        plot_bgcolor=WHITE,
        font=dict(family="Arial, sans-serif", color=TEXT),
        margin=dict(l=45, r=30, t=55 if title else 35, b=45),
        legend_title_text="",
        hoverlabel=dict(bgcolor=WHITE, font_color=TEXT),
    )
    fig.update_xaxes(showgrid=True, gridcolor="#EDF2F7", zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="#EDF2F7", zeroline=False)
    return fig


def country_flag(country):
    # Small emoji helper for common ISO-style country names.
    # If a name isn't found, a globe is displayed.
    flags = {
        "Argentina": "🇦🇷", "Algeria": "🇩🇿", "Australia": "🇦🇺",
        "Belgium": "🇧🇪", "Brazil": "🇧🇷", "Canada": "🇨🇦",
        "Colombia": "🇨🇴", "Croatia": "🇭🇷", "Ecuador": "🇪🇨",
        "England": "🏴", "France": "🇫🇷", "Germany": "🇩🇪",
        "Ghana": "🇬🇭", "Iran": "🇮🇷", "Italy": "🇮🇹",
        "Japan": "🇯🇵", "Mexico": "🇲🇽", "Morocco": "🇲🇦",
        "Netherlands": "🇳🇱", "New Zealand": "🇳🇿", "Nigeria": "🇳🇬",
        "Portugal": "🇵🇹", "Saudi Arabia": "🇸🇦", "Senegal": "🇸🇳",
        "South Africa": "🇿🇦", "South Korea": "🇰🇷", "Spain": "🇪🇸",
        "Switzerland": "🇨🇭", "Tunisia": "🇹🇳", "United States": "🇺🇸",
        "Uruguay": "🇺🇾",
    }
    return flags.get(country, "🌎")


sidebar = html.Div(
    [
        html.Div(
            [
                html.Div("WORLD CUP", style={
                    "fontSize": "25px",
                    "fontWeight": "900",
                    "letterSpacing": "1px",
                    "color": WHITE,
                }),
                html.Div("2026 GOAL ANALYTICS", style={
                    "fontSize": "12px",
                    "fontWeight": "700",
                    "letterSpacing": "1.4px",
                    "color": LIGHT_GOLD,
                }),
            ],
            style={"marginBottom": "34px"},
        ),

        dcc.RadioItems(
            id="page-selector",
            options=[
                {"label": "  Overview", "value": "overview"},
                {"label": "  Country Profile", "value": "country"},
                {"label": "  Confederation", "value": "confederation"},
                {"label": "  Venue Profile", "value": "venue"},
                {"label": "  Referee Profile", "value": "referee"},
                {"label": "  Goal Insights", "value": "insights"},
            ],
            value="overview",
            labelStyle={
                "display": "block",
                "padding": "12px 10px",
                "marginBottom": "6px",
                "cursor": "pointer",
                "borderRadius": "8px",
            },
            inputStyle={"marginRight": "9px"},
            style={
                "color": WHITE,
                "fontSize": "15px",
                "fontWeight": "600",
            },
        ),

        html.Div(
            "Vizual Optima",
            style={
                "position": "absolute",
                "bottom": "24px",
                "left": "24px",
                "color": "#8FB4D3",
                "fontSize": "12px",
            },
        ),
    ],
    style={
        "position": "fixed",
        "top": 0,
        "left": 0,
        "bottom": 0,
        "width": "235px",
        "padding": "28px 22px",
        "background": f"linear-gradient(180deg, {NAVY} 0%, {DARK_BLUE} 100%)",
        "zIndex": 10,
    },
)

