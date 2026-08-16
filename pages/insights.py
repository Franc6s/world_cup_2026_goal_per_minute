from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd

from data import goal_events, labels
from theme import *
from components import graph_card

insights_layout = html.Div(
    [
        html.H1("Goal Insights", style={"margin": 0, "color": NAVY}),
        html.P(
            "Designed around the three analytical questions behind the dashboard.",
            style={"color": MUTED},
        ),

        html.Div(
            [
                html.Div(
                    [
                        html.Div("01", style={"fontSize": "13px", "fontWeight": "900", "color": GOLD}),
                        html.H2("When are most goals scored?", style={"color": NAVY}),
                        html.Div(id="insight-time-text", style={"color": TEXT, "lineHeight": "1.7"}),
                    ],
                    style={
                        "backgroundColor": WHITE,
                        "padding": "22px",
                        "borderRadius": "14px",
                        "border": f"1px solid {BORDER}",
                    },
                ),
                html.Div(
                    [
                        html.Div("02", style={"fontSize": "13px", "fontWeight": "900", "color": GOLD}),
                        html.H2("Which position is most likely to score?", style={"color": NAVY}),
                        html.Div(id="insight-position-text", style={"color": TEXT, "lineHeight": "1.7"}),
                    ],
                    style={
                        "backgroundColor": WHITE,
                        "padding": "22px",
                        "borderRadius": "14px",
                        "border": f"1px solid {BORDER}",
                    },
                ),
                html.Div(
                    [
                        html.Div("03", style={"fontSize": "13px", "fontWeight": "900", "color": GOLD}),
                        html.H2("Do coaches need late defensive changes?", style={"color": NAVY}),
                        html.Div(id="insight-defense-text", style={"color": TEXT, "lineHeight": "1.7"}),
                    ],
                    style={
                        "backgroundColor": WHITE,
                        "padding": "22px",
                        "borderRadius": "14px",
                        "border": f"1px solid {BORDER}",
                    },
                ),
            ],
            style={
                "display": "grid",
                "gridTemplateColumns": "repeat(3, 1fr)",
                "gap": "18px",
                "marginBottom": "18px",
            },
        ),

        html.Div(
            [
                graph_card("Goal Share by 15-Minute Period", "insight-period"),
                graph_card("Position × Match Period Heatmap", "position-period-heatmap"),
            ],
            style={
                "display": "grid",
                "gridTemplateColumns": "0.8fr 1.2fr",
                "gap": "18px",
            },
        ),
    ]
)



def register_callbacks(app):
    @app.callback(
        Output("insight-time-text", "children"),
        Output("insight-position-text", "children"),
        Output("insight-defense-text", "children"),
        Output("insight-period", "figure"),
        Output("position-period-heatmap", "figure"),
        Input("page-selector", "value"),
    )
    def update_insights(_):
        period_counts = (
            goal_events["Goal Period"]
            .value_counts()
            .reindex(labels[:-1], fill_value=0)
        )
        top_period = period_counts.idxmax()
        top_period_goals = int(period_counts.max())
        top_period_pct = top_period_goals / len(goal_events) * 100 if len(goal_events) else 0

        pos_counts = goal_events["Position Group"].value_counts()
        top_position = pos_counts.idxmax()
        top_position_goals = int(pos_counts.max())
        top_position_pct = top_position_goals / len(goal_events) * 100 if len(goal_events) else 0

        late_count = int((goal_events["Minute Scored"] >= 76).sum())
        late_pct = late_count / len(goal_events) * 100 if len(goal_events) else 0

        time_text = html.P(
            [
                "The highest-volume scoring period in the current dataset is ",
                html.B(f"{top_period}"),
                f", with {top_period_goals} goals ({top_period_pct:.1f}% of all non-shootout goals).",
            ]
        )

        position_text = html.P(
            [
                html.B(top_position),
                f" contributes the largest share of goals: {top_position_goals} goals "
                f"({top_position_pct:.1f}% of the total). This is scoring contribution, not a true probability, "
                "because player minutes/exposure are not yet in the dataset.",
            ]
        )

        defense_text = html.P(
            [
                f"{late_count} goals ({late_pct:.1f}%) were scored from minute 76 onward. ",
                "This quantifies late-game scoring pressure, but substitutions and goals conceded by team are needed "
                "before concluding that coaches should replace defenders late in matches.",
            ]
        )

        period_df = period_counts.reset_index()
        period_df.columns = ["Goal Period", "Goals"]
        period_df["Share"] = period_df["Goals"] / period_df["Goals"].sum() * 100

        fig_period = px.bar(
            period_df,
            x="Goal Period",
            y="Share",
            text=period_df["Share"].map(lambda x: f"{x:.1f}%"),
        )
        fig_period.update_traces(marker_color=BLUE, textposition="outside")
        fig_period = format_fig(fig_period)
        fig_period.update_yaxes(title="% of Goals")

        heat = pd.crosstab(
            goal_events["Position Group"],
            goal_events["Goal Period"],
        )
        heat = heat.reindex(columns=labels[:-1], fill_value=0)

        fig_heat = px.imshow(
            heat,
            text_auto=True,
            aspect="auto",
            color_continuous_scale=[[0, PALE_BLUE], [0.55, BLUE], [1, GOLD]],
            labels=dict(x="Match Period", y="Position Group", color="Goals"),
        )
        fig_heat.update_layout(
            paper_bgcolor=WHITE,
            font=dict(color=TEXT),
            margin=dict(l=60, r=30, t=25, b=45),
        )

        return time_text, position_text, defense_text, fig_period, fig_heat
