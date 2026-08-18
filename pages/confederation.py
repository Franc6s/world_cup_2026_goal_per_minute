from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd

from data import goal_events
from theme import *
from components import card, graph_card, format_fig


CONFEDERATIONS_FULL_NAMES = {
    "AFC": "Asian Football Confederation",
    "CAF": "Confédération Africaine de Football",
    "CONCACAF": "Confederation of North, Central America and Caribbean Association Football",
    "CONMEBOL": "Confederación Sudamericana de Fútbol",
    "OFC": "Oceania Football Confederation",
    "UEFA": "Union of European Football Associations",
}


confederations = sorted(
    goal_events["Confederation"]
    .dropna()
    .unique()
)


confed_layout = html.Div(
    [
        html.H1(
            "Confederation Profile",
            style={
                "margin": 0,
                "color": NAVY,
            },
        ),

        html.P(
            "Compare scoring volume, timing, countries, age profiles, and player positions within each confederation.",
            style={
                "color": MUTED,
            },
        ),

        dcc.Dropdown(
            id="confed-dropdown",
            options=[
                {
                    "label": c,
                    "value": c,
                }
                for c in confederations
            ],
            value=confederations[0] if confederations else None,
            clearable=False,
            style={
                "width": "300px",
                "marginBottom": "8px",
            },
        ),

        # ====================================================
        # FULL CONFEDERATION NAME
        # ====================================================

        html.Div(
            id="confed-full-name",
            style={
                "fontSize": "14px",
                "fontWeight": "600",
                "color": MUTED,
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
                    value_id="confed-goals",
                ),

                card(
                    "Own Goals",
                    value_id="confed-own-goals",
                ),

                card(
                    "Countries Scoring",
                    value_id="confed-teams",
                ),

                card(
                    "Goal Scorers",
                    value_id="confed-scorers",
                ),

                card(
                    "Avg Scorer Age",
                    value_id="confed-age",
                ),

                card(
                    "Avg Goal Minute",
                    value_id="confed-minute",
                ),

                card(
                    "Top Scorer",
                    value_id="confed-top-scorer",
                ),
            ],
            style={
                "display": "grid",
                "gridTemplateColumns": "repeat(4, 1fr)",
                "gap": "14px",
                "marginBottom": "18px",
            },
        ),

        # ====================================================
        # COUNTRY TABLE
        # ====================================================

        html.Div(
            [
                html.Div(
                    "Countries",
                    style={
                        "fontSize": "17px",
                        "fontWeight": "800",
                        "color": NAVY,
                        "marginBottom": "12px",
                    },
                ),

                html.Div(
                    id="confed-country-table"
                ),
            ],
            style={
                "backgroundColor": WHITE,
                "padding": "16px",
                "borderRadius": "14px",
                "border": f"1px solid {BORDER}",
                "boxShadow": "0 4px 16px rgba(6, 26, 45, 0.05)",
                "marginBottom": "18px",
            },
        ),

        # ====================================================
        # COUNTRY GOALS + TIMING
        # ====================================================

        html.Div(
            [
                graph_card(
                    "Goals by Country",
                    "confed-country-bar",
                ),

                graph_card(
                    "Goal Timing by Country",
                    "confed-box",
                ),
            ],
            style={
                "display": "grid",
                "gridTemplateColumns": "1fr 1fr",
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
                    "Goals by Scorer Age",
                    "confed-age-scatter",
                ),

                graph_card(
                    "Position Contribution",
                    "confed-position",
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


# ============================================================
# CALLBACKS
# ============================================================

def register_callbacks(app):

    @app.callback(
        Output("confed-full-name", "children"),
        Output("confed-goals", "children"),
        Output("confed-own-goals", "children"),
        Output("confed-teams", "children"),
        Output("confed-scorers", "children"),
        Output("confed-age", "children"),
        Output("confed-minute", "children"),
        Output("confed-top-scorer", "children"),
        Output("confed-country-table", "children"),
        Output("confed-country-bar", "figure"),
        Output("confed-box", "figure"),
        Output("confed-age-scatter", "figure"),
        Output("confed-position", "figure"),
        Input("confed-dropdown", "value"),
    )
    def update_confed(confed):

        dff = goal_events[
            goal_events["Confederation"] == confed
        ].copy()

        # ========================================================
        # OWN GOALS
        # ========================================================

        own_goal_mask = (
            dff["Own Goal"]
            .fillna("No")
            .astype(str)
            .str.strip()
            .str.lower()
            .eq("yes")
        )

        own_goals = int(
            own_goal_mask.sum()
        )

        # All scoring analytics on this page exclude own goals.
        dff_scoring = dff[
            ~own_goal_mask
        ].copy()

        # ========================================================
        # CONFEDERATION NAME
        # ========================================================

        full_name = CONFEDERATIONS_FULL_NAMES.get(
            confed,
            confed,
        )

        # ========================================================
        # KPI METRICS
        # ========================================================

        n_goals = len(
            dff_scoring
        )

        n_teams = (
            dff_scoring["Player Country"]
            .nunique()
        )

        n_scorers = (
            dff_scoring[
                [
                    "Player First Name",
                    "Player Name",
                ]
            ]
            .drop_duplicates()
            .shape[0]
        )

        avg_age = (
            dff_scoring["Player Age"]
            .mean()
        )

        avg_min = (
            dff_scoring["Minute Scored"]
            .mean()
        )

        # ========================================================
        # TOP SCORER
        # ========================================================

        scorer_df = (
            dff_scoring.groupby(
                [
                    "Player First Name",
                    "Player Name",
                ],
                dropna=False,
            )
            .size()
            .reset_index(
                name="Goals"
            )
            .sort_values(
                [
                    "Goals",
                    "Player Name",
                ],
                ascending=[
                    False,
                    True,
                ],
            )
        )

        if not scorer_df.empty:

            top_scorer_row = (
                scorer_df.iloc[0]
            )

            first_name = (
                ""
                if pd.isna(
                    top_scorer_row["Player First Name"]
                )
                else str(
                    top_scorer_row["Player First Name"]
                )
            )

            last_name = (
                ""
                if pd.isna(
                    top_scorer_row["Player Name"]
                )
                else str(
                    top_scorer_row["Player Name"]
                )
            )

            top_scorer_name = (
                f"{first_name} {last_name}"
            ).strip()

            top_scorer_goals = int(
                top_scorer_row["Goals"]
            )

            top_scorer_display = (
                f"{top_scorer_name} "
                f"({top_scorer_goals} Goals)"
            )

        else:

            top_scorer_display = "()"

        # ========================================================
        # COUNTRY TABLE
        # ========================================================

        countries_df = (
            dff_scoring.groupby(
                "Player Country"
            )
            .agg(
                Goals=(
                    "Goal_ID",
                    "count",
                ),

                Goal_Scorers=(
                    "Player Name",
                    "nunique",
                ),
            )
            .reset_index()
            .sort_values(
                [
                    "Goals",
                    "Player Country",
                ],
                ascending=[
                    False,
                    True,
                ],
            )
        )

        country_rows = []

        for _, row in countries_df.iterrows():

            country_rows.append(
                html.Tr(
                    [
                        html.Td(
                            row["Player Country"],
                            style={
                                "padding": "8px 12px",
                                "borderBottom": f"1px solid {BORDER}",
                            },
                        ),

                        html.Td(
                            int(
                                row["Goals"]
                            ),
                            style={
                                "padding": "8px 12px",
                                "borderBottom": f"1px solid {BORDER}",
                                "textAlign": "center",
                            },
                        ),

                        html.Td(
                            int(
                                row["Goal_Scorers"]
                            ),
                            style={
                                "padding": "8px 12px",
                                "borderBottom": f"1px solid {BORDER}",
                                "textAlign": "center",
                            },
                        ),
                    ]
                )
            )

        country_table = html.Table(
            [
                html.Thead(
                    html.Tr(
                        [
                            html.Th(
                                "Country",
                                style={
                                    "padding": "8px 12px",
                                    "textAlign": "left",
                                    "color": NAVY,
                                },
                            ),

                            html.Th(
                                "Goals",
                                style={
                                    "padding": "8px 12px",
                                    "textAlign": "center",
                                    "color": NAVY,
                                },
                            ),

                            html.Th(
                                "Goal Scorers",
                                style={
                                    "padding": "8px 12px",
                                    "textAlign": "center",
                                    "color": NAVY,
                                },
                            ),
                        ]
                    )
                ),

                html.Tbody(
                    country_rows
                ),
            ],

            style={
                "width": "100%",
                "borderCollapse": "collapse",
                "fontSize": "14px",
            },
        )

        # ========================================================
        # GOALS BY COUNTRY
        # ========================================================

        country_goals = (
            dff_scoring.groupby(
                "Player Country"
            )
            .size()
            .reset_index(
                name="Goals"
            )
            .sort_values(
                "Goals"
            )
        )

        fig_country = px.bar(
            country_goals,
            x="Goals",
            y="Player Country",
            orientation="h",
            text="Goals",
        )

        fig_country.update_traces(
            marker_color=BLUE
        )

        fig_country = format_fig(
            fig_country
        )

        # ========================================================
        # GOAL TIMING BY COUNTRY
        # ========================================================

        fig_box = px.box(
            dff_scoring,
            x="Player Country",
            y="Minute Scored",
            points="all",
            hover_data=[
                "Player First Name",
                "Player Name",
                "Fixture",
            ],
        )

        fig_box.update_traces(
            marker_color=GOLD,
            line_color=BLUE,
        )

        fig_box = format_fig(
            fig_box
        )

        # ========================================================
        # GOALS BY EXACT PLAYER AGE
        # ========================================================

        age_goals = (
            dff_scoring
            .dropna(
                subset=[
                    "Player Age"
                ]
            )
            .groupby(
                "Player Age"
            )
            .size()
            .reset_index(
                name="Goals"
            )
            .sort_values(
                "Player Age"
            )
        )

        fig_age = px.scatter(
            age_goals,
            x="Player Age",
            y="Goals",
            size="Goals",
            hover_data={
                "Player Age": True,
                "Goals": True,
            },
            size_max=35,
        )

        fig_age.update_traces(
            marker=dict(
                color=BLUE,
                line=dict(
                    width=1.5,
                    color=GOLD,
                ),
            )
        )

        fig_age.update_xaxes(
            title="Player Age",
            dtick=1,
        )

        fig_age.update_yaxes(
            title="Goals Scored",
        )

        fig_age = format_fig(
            fig_age
        )

        # ========================================================
        # POSITION CONTRIBUTION
        # ========================================================

        pos = (
            dff_scoring.groupby(
                [
                    "Player Country",
                    "Position Group",
                ]
            )
            .size()
            .reset_index(
                name="Goals"
            )
        )

        fig_pos = px.bar(
            pos,
            x="Player Country",
            y="Goals",
            color="Position Group",
            barmode="stack",
        )

        fig_pos = format_fig(
            fig_pos
        )

        # ========================================================
        # RETURN
        # ========================================================

        return (
            full_name,
            f"{n_goals:,}",
            f"{own_goals:,}",
            f"{n_teams:,}",
            f"{n_scorers:,}",
            (
                f"{avg_age:.1f}"
                if pd.notna(avg_age)
                else "—"
            ),
            (
                f"{avg_min:.1f}'"
                if pd.notna(avg_min)
                else "—"
            ),
            top_scorer_display,
            country_table,
            fig_country,
            fig_box,
            fig_age,
            fig_pos,
        )