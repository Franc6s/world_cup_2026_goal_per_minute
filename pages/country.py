import pandas as pd
from dash import dcc, html, Input, Output
import plotly.express as px

from data import goal_events
from theme import *
from components import card, graph_card, format_fig, country_flag


countries = sorted(goal_events["Player Country"].dropna().unique())


country_layout = html.Div(
    [
        html.H1(
            "Country Profile",
            style={
                "margin": 0,
                "color": NAVY,
            },
        ),

        html.P(
            "Team scoring profile, goal scorers, coach information, fixtures represented in the goal dataset, and scoring timing.",
            style={
                "color": MUTED,
            },
        ),

        dcc.Dropdown(
            id="country-dropdown",
            options=[
                {
                    "label": c,
                    "value": c,
                }
                for c in countries
            ],
            value=countries[0] if countries else None,
            clearable=False,
            style={
                "width": "330px",
                "marginBottom": "20px",
            },
        ),

        html.Div(
            id="country-header",
            style={
                "marginBottom": "18px",
            },
        ),

        # ====================================================
        # KPI CARDS
        # ====================================================

        html.Div(
            [
                card(
                    "Goals Scored",
                    value_id="country-goals",
                ),
                card(
                    "Matches With Goals",
                    value_id="country-matches",
                ),
                card(
                    "Goal Scorers",
                    value_id="country-scorers",
                ),
                card(
                    "Avg Goal Minute",
                    value_id="country-avg-minute",
                ),
                card(
                    "Player With Most Goals",
                    value_id="country-top-scorer",
                ),
            ],
            style={
                "display": "grid",
                "gridTemplateColumns": "repeat(5, 1fr)",
                "gap": "14px",
                "marginBottom": "18px",
            },
        ),

        # ====================================================
        # SCORERS + MATCH PERIOD
        # ====================================================

        html.Div(
            [
                graph_card(
                    "Top Goal Scorers",
                    "country-scorers-chart",
                ),
                graph_card(
                    "Goals by Match Period",
                    "country-period-chart",
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
        # TIMELINE + POSITION
        # ====================================================

        html.Div(
            [
                graph_card(
                    "Goal Timeline",
                    "country-timeline",
                ),
                graph_card(
                    "Goals by Position",
                    "country-position",
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
        # FIXTURES
        # ====================================================

        html.Div(
            [
                html.H3(
                    "Fixtures Represented in Goal Dataset",
                    style={
                        "color": NAVY,
                    },
                ),
                html.Div(
                    id="country-fixtures-table",
                ),
            ],
            style={
                "backgroundColor": WHITE,
                "padding": "18px",
                "border": f"1px solid {BORDER}",
                "borderRadius": "14px",
            },
        ),
    ]
)


def register_callbacks(app):

    @app.callback(
        Output("country-header", "children"),
        Output("country-goals", "children"),
        Output("country-matches", "children"),
        Output("country-scorers", "children"),
        Output("country-avg-minute", "children"),
        Output("country-top-scorer", "children"),
        Output("country-scorers-chart", "figure"),
        Output("country-period-chart", "figure"),
        Output("country-timeline", "figure"),
        Output("country-position", "figure"),
        Output("country-fixtures-table", "children"),
        Input("country-dropdown", "value"),
    )
    def update_country(country):

        dff = goal_events[
            goal_events["Player Country"] == country
        ].copy()

        # ========================================================
        # COUNTRY INFORMATION
        # ========================================================

        coach = (
            dff["Coach"].dropna().iloc[0]
            if dff["Coach"].notna().any()
            else "Not available"
        )

        coach_nat = (
            dff["Coach Nationality"].dropna().iloc[0]
            if dff["Coach Nationality"].notna().any()
            else "Not available"
        )

        confed = (
            dff["Confederation"].dropna().iloc[0]
            if dff["Confederation"].notna().any()
            else "—"
        )

        groups = ", ".join(
            sorted(
                dff["Group"]
                .dropna()
                .astype(str)
                .unique()
            )
        )

        groups = groups if groups else "—"

        # ========================================================
        # COUNTRY HEADER
        # ========================================================

        header = html.Div(
            [
                html.Div(
                    country_flag(country),
                    style={
                        "fontSize": "52px",
                        "marginRight": "16px",
                    },
                ),

                html.Div(
                    [
                        html.Div(
                            country,
                            style={
                                "fontSize": "29px",
                                "fontWeight": "900",
                                "color": NAVY,
                            },
                        ),

                        html.Div(
                            (
                                f"{confed}  •  "
                                f"Initial Group: {groups}  •  "
                                f"Coach: {coach} ({coach_nat})"
                            ),
                            style={
                                "color": MUTED,
                                "marginTop": "5px",
                            },
                        ),
                    ]
                ),
            ],
            style={
                "display": "flex",
                "alignItems": "center",
                "backgroundColor": WHITE,
                "padding": "16px 20px",
                "borderRadius": "14px",
                "border": f"1px solid {BORDER}",
            },
        )

        # ========================================================
        # KPI METRICS
        # ========================================================

        n_goals = len(dff)

        n_matches = dff["Match ID"].nunique()

        n_scorers = (
            dff[
                [
                    "Player First Name",
                    "Player Name",
                ]
            ]
            .drop_duplicates()
            .shape[0]
        )

        avg_min = dff["Minute Scored"].mean()

        # ========================================================
        # PLAYER WITH MOST GOALS
        # ========================================================

        top_scorer_df = (
            dff.groupby(
                [
                    "Player First Name",
                    "Player Name",
                ],
                dropna=False,
            )
            .size()
            .reset_index(name="Goals")
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

        if not top_scorer_df.empty:

            top_scorer_row = top_scorer_df.iloc[0]

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
                f"{top_scorer_name} — "
                f"{top_scorer_goals} Goals"
            )

        else:
            top_scorer_display = "—"

        # ========================================================
        # TOP GOAL SCORERS
        # ========================================================

        scorers = (
            dff.groupby(
                [
                    "Player First Name",
                    "Player Name",
                ],
                dropna=False,
            )
            .size()
            .reset_index(name="Goals")
            .sort_values(
                "Goals",
                ascending=True,
            )
        )

        scorers["Player"] = (
            scorers["Player First Name"].fillna("")
            + " "
            + scorers["Player Name"].fillna("")
        ).str.strip()

        fig_scorers = px.bar(
            scorers.tail(12),
            x="Goals",
            y="Player",
            orientation="h",
            text="Goals",
        )

        fig_scorers.update_traces(
            marker_color=BLUE,
        )

        fig_scorers = format_fig(
            fig_scorers
        )

        # ========================================================
        # GOALS BY MATCH PERIOD
        # ========================================================

        period = (
            dff["Goal Period"]
            .value_counts()
            .reindex(
                labels[:-1],
                fill_value=0,
            )
            .reset_index()
        )

        period.columns = [
            "Goal Period",
            "Goals",
        ]

        fig_period = px.bar(
            period,
            x="Goal Period",
            y="Goals",
            text="Goals",
        )

        fig_period.update_traces(
            marker_color=GOLD,
        )

        fig_period = format_fig(
            fig_period
        )

        # ========================================================
        # GOAL TIMELINE
        # ========================================================

        fig_timeline = px.scatter(
            dff,
            x="Minute Scored",
            y="Fixture",
            hover_data=[
                "Player First Name",
                "Player Name",
                "Fixture Format",
                "Stadium Name",
            ],
        )

        fig_timeline.update_traces(
            marker=dict(
                size=12,
                color=GOLD,
                line=dict(
                    width=1,
                    color=NAVY,
                ),
            )
        )

        fig_timeline.update_xaxes(
            range=[
                0,
                120,
            ],
            dtick=15,
        )

        fig_timeline = format_fig(
            fig_timeline
        )

        # ========================================================
        # GOALS BY POSITION
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

        fig_pos = px.pie(
            pos,
            names="Position Group",
            values="Goals",
            hole=0.55,
        )

        fig_pos.update_layout(
            paper_bgcolor=WHITE,
            margin=dict(
                l=20,
                r=20,
                t=20,
                b=20,
            ),
            font=dict(
                color=TEXT,
            ),
        )

        # ========================================================
        # FIXTURES TABLE
        # ========================================================

        fixture_cols = [
            "Date",
            "Fixture",
            "Fixture Format",
            "Group",
            "Stadium Name",
            "City Venue",
        ]

        fixture_df = (
            dff[
                fixture_cols
                + ["Match ID"]
            ]
            .drop_duplicates(
                "Match ID"
            )
            .sort_values(
                "Date"
            )
        )

        rows = []

        for _, row in fixture_df.iterrows():

            date_text = (
                row["Date"].strftime(
                    "%b %d, %Y"
                )
                if pd.notna(
                    row["Date"]
                )
                else "—"
            )

            rows.append(
                html.Tr(
                    [
                        html.Td(
                            date_text
                        ),
                        html.Td(
                            row["Fixture"]
                        ),
                        html.Td(
                            row["Fixture Format"]
                        ),
                        html.Td(
                            row["Group"]
                        ),
                        html.Td(
                            row["Stadium Name"]
                        ),
                        html.Td(
                            row["City Venue"]
                        ),
                    ]
                )
            )

        table = html.Table(
            [
                html.Thead(
                    html.Tr(
                        [
                            html.Th("Date"),
                            html.Th("Fixture"),
                            html.Th("Stage"),
                            html.Th("Group"),
                            html.Th("Stadium"),
                            html.Th("City"),
                        ]
                    )
                ),

                html.Tbody(
                    rows
                ),
            ],
            style={
                "width": "100%",
                "borderCollapse": "collapse",
            },
        )

        # ========================================================
        # RETURN
        # ========================================================

        return (
            header,
            f"{n_goals:,}",
            f"{n_matches:,}",
            f"{n_scorers:,}",
            (
                f"{avg_min:.1f}'"
                if pd.notna(avg_min)
                else "—"
            ),
            top_scorer_display,
            fig_scorers,
            fig_period,
            fig_timeline,
            fig_pos,
            table,
        )