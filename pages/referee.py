from dash import dcc, html, Input, Output
import plotly.express as px

from data import goal_events
from theme import *
from components import card, graph_card, format_fig

referees = sorted(goal_events["Referee Name"].dropna().unique())

referee_layout = html.Div(
    [
        html.H1("Referee Profile", style={"margin": 0, "color": NAVY}),
        html.P(
            "Descriptive scoring outcomes for matches represented in the goal dataset. These charts show association, not referee causation.",
            style={"color": MUTED},
        ),

        dcc.Dropdown(
            id="referee-dropdown",
            options=[{"label": r, "value": r} for r in referees],
            value=referees[0] if referees else None,
            clearable=False,
            style={"width": "380px", "marginBottom": "20px"},
        ),

        html.Div(
            [
                card("Goals", value_id="ref-goals"),
                card("Matches Represented", value_id="ref-matches"),
                card("Penalty Goals", value_id="ref-penalties"),
                card("Stoppage-Time Goals", value_id="ref-stoppage"),
            ],
            style={
                "display": "grid",
                "gridTemplateColumns": "repeat(4, 1fr)",
                "gap": "14px",
                "marginBottom": "18px",
            },
        ),

        html.Div(
            [
                graph_card(
                    "Goal Minutes in Selected Referee's Matches",
                    "ref-minute-box"
                ),
                graph_card(
                    "Goals by Fixture Stage",
                    "ref-stage-bar"
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
        Output("ref-goals", "children"),
        Output("ref-matches", "children"),
        Output("ref-penalties", "children"),
        Output("ref-stoppage", "children"),
        Output("ref-minute-box", "figure"),
        Output("ref-stage-bar", "figure"),
        Input("referee-dropdown", "value"),
    )
    def update_referee(referee):

        dff = goal_events[
            goal_events["Referee Name"] == referee
        ].copy()

        goals_count = len(dff)

        match_count = dff["Match ID"].nunique()

        penalties = (
            dff["Penalty"]
            .fillna("No")
            .astype(str)
            .str.lower()
            .eq("yes")
            .sum()
        )

        stoppage = (
            dff["Stoppage Time"]
            .fillna("No")
            .astype(str)
            .str.lower()
            .eq("yes")
            .sum()
        )

        # ========================================================
        # GOAL MINUTES
        # ========================================================

        fig_box = px.box(
            dff,
            y="Minute Scored",
            points="all",
            hover_data=[
                "Fixture",
                "Player First Name",
                "Player Name",
                "Player Country",
            ],
        )

        fig_box.update_traces(
            marker_color=GOLD,
            line_color=BLUE,
        )

        fig_box = format_fig(fig_box)

        # ========================================================
        # GOALS BY FIXTURE STAGE
        # ========================================================

        stage = (
            dff["Fixture Format"]
            .value_counts()
            .reset_index()
        )

        stage.columns = [
            "Fixture Format",
            "Goals",
        ]

        fig_stage = px.bar(
            stage,
            x="Fixture Format",
            y="Goals",
            text="Goals",
        )

        fig_stage.update_traces(
            marker_color=BLUE
        )

        fig_stage = format_fig(fig_stage)

        fig_stage.update_yaxes(
            dtick=1
        )

        # ========================================================
        # RETURN
        # ========================================================

        return (
            f"{goals_count:,}",
            f"{match_count:,}",
            f"{penalties:,}",
            f"{stoppage:,}",
            fig_box,
            fig_stage,
        )