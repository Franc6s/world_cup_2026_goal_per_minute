import pandas as pd
from dash import dcc, html, Input, Output
import plotly.express as px

from data import goal_events, labels
from theme import *
from components import card, graph_card, format_fig


overview_layout = html.Div(
    [
        html.Div(
            [
                html.Div(
                    [
                        html.H1(
                            "Tournament Overview",
                            style={
                                "margin": 0,
                                "color": NAVY,
                                "fontSize": "31px",
                            },
                        ),
                        html.P(
                            "Explore when goals are scored, who scores them, and how scoring varies across the tournament.",
                            style={
                                "marginTop": "7px",
                                "color": MUTED,
                            },
                        ),
                    ]
                ),
            ],
            style={
                "marginBottom": "20px",
            },
        ),

        # ====================================================
        # KPI CARDS
        # ====================================================

        html.Div(
            [
                card(
                    "Total Goals",
                    value_id="kpi-total-goals",
                ),
                card(
                    "Matches Represented",
                    value_id="kpi-matches",
                ),
                card(
                    "Unique Scorers",
                    value_id="kpi-scorers",
                ),
                card(
                    "Average Scorer Age",
                    value_id="kpi-age",
                ),
                card(
                    "Goals in the Last Quarter",
                    value_id="kpi-late",
                ),
            ],
            style={
                "display": "grid",
                "gridTemplateColumns": "repeat(5, 1fr)",
                "gap": "14px",
                "marginBottom": "20px",
            },
        ),

        # ====================================================
        # GOAL MINUTE FILTER
        # ====================================================

        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            "Goal Minute Filter",
                            style={
                                "fontWeight": "800",
                                "color": NAVY,
                            },
                        ),
                        html.Div(
                            "Move the handles to filter every overview visualization by scoring minute.",
                            style={
                                "fontSize": "12px",
                                "color": MUTED,
                                "marginTop": "4px",
                            },
                        ),
                        dcc.RangeSlider(
                            id="minute-slider",
                            min=0,
                            max=120,
                            step=1,
                            value=[0, 120],
                            marks={
                                0: "0",
                                15: "15",
                                30: "30",
                                45: "45",
                                60: "60",
                                75: "75",
                                90: "90",
                                105: "105",
                                120: "120",
                            },
                            tooltip={
                                "placement": "bottom",
                                "always_visible": False,
                            },
                        ),
                    ],
                    style={
                        "backgroundColor": WHITE,
                        "padding": "18px 22px",
                        "border": f"1px solid {BORDER}",
                        "borderRadius": "14px",
                    },
                )
            ],
            style={
                "marginBottom": "20px",
            },
        ),

        # ====================================================
        # CONFEDERATION + GOAL SHARE
        # ====================================================

        html.Div(
            [
                graph_card(
                    "Goals by Confederation",
                    "confed-bubble",
                ),
                graph_card(
                    "Share of Tournament Goals",
                    "goal-pie",
                ),
            ],
            style={
                "display": "grid",
                "gridTemplateColumns": "1.25fr 0.75fr",
                "gap": "18px",
                "marginBottom": "18px",
            },
        ),

        # ====================================================
        # GOAL TIMING
        # ====================================================

        html.Div(
            [
                graph_card(
                    "When Are Goals Scored?",
                    "goal-timeline",
                ),
                graph_card(
                    "Goal Minute Distribution",
                    "goal-box",
                ),
            ],
            style={
                "display": "grid",
                "gridTemplateColumns": "1.25fr 0.75fr",
                "gap": "18px",
                "marginBottom": "18px",
            },
        ),

        # ====================================================
        # AGE + POSITION
        # ====================================================

        html.Div(
            [
                graph_card(
                    "Scoring Contribution by Player Age",
                    "age-scatter",
                ),
                graph_card(
                    "Goals by Position Group",
                    "position-bar",
                ),
            ],
            style={
                "display": "grid",
                "gridTemplateColumns": "1fr 1fr",
                "gap": "18px",
            },
        ),
    ]
)


def register_callbacks(app):

    @app.callback(
        Output("kpi-total-goals", "children"),
        Output("kpi-matches", "children"),
        Output("kpi-scorers", "children"),
        Output("kpi-age", "children"),
        Output("kpi-late", "children"),
        Output("confed-bubble", "figure"),
        Output("goal-pie", "figure"),
        Output("goal-timeline", "figure"),
        Output("goal-box", "figure"),
        Output("age-scatter", "figure"),
        Output("position-bar", "figure"),
        Input("minute-slider", "value"),
    )
    def update_overview(minute_range):

        lo, hi = minute_range

        dff = goal_events[
            goal_events["Minute Scored"].between(
                lo,
                hi,
                inclusive="both",
            )
        ].copy()

        # ========================================================
        # KPI METRICS
        # ========================================================

        total_goals = len(dff)

        matches = dff["Match ID"].nunique()

        scorers = (
            dff["Player First Name"]
            .fillna("")
            .str.cat(
                dff["Player Name"].fillna(""),
                sep=" ",
            )
            .str.strip()
            .nunique()
        )

        avg_age = dff["Player Age"].mean()

        late_goals = (
            dff["Minute Scored"] >= 76
        ).sum()

        # ========================================================
        # CONFEDERATION BUBBLE
        # ========================================================

        conf = (
            dff.groupby(
                "Confederation",
                dropna=False,
            )
            .agg(
                Goals=(
                    "Goal_ID",
                    "count",
                ),
                Scorers=(
                    "Player Name",
                    "nunique",
                ),
                Teams=(
                    "Player Country",
                    "nunique",
                ),
                Avg_Age=(
                    "Player Age",
                    "mean",
                ),
            )
            .reset_index()
        )

        fig_conf = px.scatter(
            conf,
            x="Confederation",
            y="Goals",
            size="Scorers",
            color="Confederation",
            color_discrete_map=CONFED_COLORS,
            hover_data={
                "Goals": True,
                "Scorers": True,
                "Teams": True,
                "Avg_Age": ":.1f",
                "Confederation": False,
            },
            size_max=62,
        )

        fig_conf = format_fig(
            fig_conf
        )

        fig_conf.update_traces(
            marker=dict(
                line=dict(
                    width=1.5,
                    color=WHITE,
                )
            )
        )

        # ========================================================
        # PIE CHART
        # ========================================================

        fig_pie = px.pie(
            conf,
            names="Confederation",
            values="Goals",
            hole=0.58,
            color="Confederation",
            color_discrete_map=CONFED_COLORS,
        )

        fig_pie.update_layout(
            paper_bgcolor=WHITE,
            font=dict(
                color=TEXT,
            ),
            margin=dict(
                l=20,
                r=20,
                t=20,
                b=20,
            ),
            showlegend=True,
        )

        fig_pie.update_traces(
            textposition="inside",
            textinfo="percent+label",
        )

        # ========================================================
        # GOAL TIMELINE / PERIODS
        # ========================================================

        period_order = labels[:-1]

        period_counts = (
            dff["Goal Period"]
            .value_counts()
            .reindex(
                period_order,
                fill_value=0,
            )
            .reset_index()
        )

        period_counts.columns = [
            "Goal Period",
            "Goals",
        ]

        fig_timeline = px.bar(
            period_counts,
            x="Goal Period",
            y="Goals",
            text="Goals",
        )

        fig_timeline.update_traces(
            marker_color=BLUE,
            textposition="outside",
        )

        fig_timeline = format_fig(
            fig_timeline
        )

        fig_timeline.update_yaxes(
            title="Goals",
        )

        fig_timeline.update_xaxes(
            title="Match minute",
        )

        # ========================================================
        # BOX PLOT
        # ========================================================

        fig_box = px.box(
            dff,
            x="Confederation",
            y="Minute Scored",
            color="Confederation",
            color_discrete_map=CONFED_COLORS,
            points="all",
            hover_data=[
                "Player First Name",
                "Player Name",
                "Player Country",
                "Fixture",
            ],
        )

        fig_box = format_fig(
            fig_box
        )

        fig_box.update_layout(
            showlegend=False
        )

        # ========================================================
        # AGE VS GOALS
        # ========================================================

        player_age = (
            dff.groupby(
                [
                    "Player First Name",
                    "Player Name",
                    "Player Country",
                    "Player Age",
                    "Position Group",
                ],
                dropna=False,
            )
            .size()
            .reset_index(
                name="Goals"
            )
        )

        player_age["Player"] = (
            player_age["Player First Name"].fillna("")
            + " "
            + player_age["Player Name"].fillna("")
        ).str.strip()

        fig_age = px.scatter(
            player_age,
            x="Player Age",
            y="Goals",
            size="Goals",
            color="Position Group",
            hover_name="Player",
            hover_data=[
                "Player Country",
            ],
            size_max=35,
        )

        fig_age = format_fig(
            fig_age
        )

        # ========================================================
        # POSITION
        # ========================================================

        pos = (
            dff["Position Group"]
            .value_counts()
            .reset_index()
        )

        pos.columns = [
            "Position Group",
            "Goals",
        ]

        fig_pos = px.bar(
            pos.sort_values(
                "Goals"
            ),
            x="Goals",
            y="Position Group",
            orientation="h",
            text="Goals",
        )

        fig_pos.update_traces(
            marker_color=GOLD,
            textposition="outside",
        )

        fig_pos = format_fig(
            fig_pos
        )

        # ========================================================
        # RETURN
        # ========================================================

        return (
            f"{total_goals:,}",
            f"{matches:,}",
            f"{scorers:,}",
            (
                f"{avg_age:.1f}"
                if pd.notna(avg_age)
                else "—"
            ),
            f"{late_goals:,}",
            fig_conf,
            fig_pie,
            fig_timeline,
            fig_box,
            fig_age,
            fig_pos,
        )