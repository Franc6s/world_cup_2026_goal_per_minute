from dash import dcc, html, Input, Output
import plotly.express as px

from data import goal_events
from theme import *
from components import card, graph_card, format_fig

confederations = sorted(goal_events["Confederation"].dropna().unique())

confed_layout = html.Div(
    [
        html.H1("Confederation Profile", style={"margin": 0, "color": NAVY}),
        html.P(
            "Compare scoring volume, timing, countries, age profiles, and player positions within each confederation.",
            style={"color": MUTED},
        ),

        dcc.Dropdown(
            id="confed-dropdown",
            options=[{"label": c, "value": c} for c in confederations],
            value=confederations[0] if confederations else None,
            clearable=False,
            style={"width": "300px", "marginBottom": "20px"},
        ),

        html.Div(
            [
                card("Total Goals", value_id="confed-goals"),
                card("Countries Scoring", value_id="confed-teams"),
                card("Goal Scorers", value_id="confed-scorers"),
                card("Avg Scorer Age", value_id="confed-age"),
                card("Avg Goal Minute", value_id="confed-minute"),
            ],
            style={
                "display": "grid",
                "gridTemplateColumns": "repeat(5, 1fr)",
                "gap": "14px",
                "marginBottom": "18px",
            },
        ),

        html.Div(
            [
                graph_card("Goals by Country", "confed-country-bar"),
                graph_card("Goal Timing by Country", "confed-box"),
            ],
            style={
                "display": "grid",
                "gridTemplateColumns": "1fr 1fr",
                "gap": "18px",
                "marginBottom": "18px",
            },
        ),

        html.Div(
            [
                graph_card("Scorer Age vs Goals", "confed-age-scatter"),
                graph_card("Position Contribution", "confed-position"),
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
        Output("confed-goals", "children"),
        Output("confed-teams", "children"),
        Output("confed-scorers", "children"),
        Output("confed-age", "children"),
        Output("confed-minute", "children"),
        Output("confed-country-bar", "figure"),
        Output("confed-box", "figure"),
        Output("confed-age-scatter", "figure"),
        Output("confed-position", "figure"),
        Input("confed-dropdown", "value"),
    )
    def update_confed(confed):
        dff = goal_events[goal_events["Confederation"] == confed].copy()

        n_goals = len(dff)
        n_teams = dff["Player Country"].nunique()
        n_scorers = dff["Player Name"].nunique()
        avg_age = dff["Player Age"].mean()
        avg_min = dff["Minute Scored"].mean()

        countries_df = (
            dff.groupby("Player Country")
            .size()
            .reset_index(name="Goals")
            .sort_values("Goals")
        )
        fig_country = px.bar(
            countries_df,
            x="Goals",
            y="Player Country",
            orientation="h",
            text="Goals",
        )
        fig_country.update_traces(marker_color=BLUE)
        fig_country = format_fig(fig_country)

        fig_box = px.box(
            dff,
            x="Player Country",
            y="Minute Scored",
            points="all",
            hover_data=["Player First Name", "Player Name", "Fixture"],
        )
        fig_box.update_traces(marker_color=GOLD, line_color=BLUE)
        fig_box = format_fig(fig_box)

        country_age = (
            dff.groupby("Player Country")
            .agg(
                Goals=("Goal_ID", "count"),
                Avg_Scorer_Age=("Player Age", "mean"),
                Scorers=("Player Name", "nunique"),
            )
            .reset_index()
        )
        fig_age = px.scatter(
            country_age,
            x="Avg_Scorer_Age",
            y="Goals",
            size="Scorers",
            hover_name="Player Country",
            size_max=42,
        )
        fig_age.update_traces(marker=dict(color=BLUE, line=dict(width=1.5, color=GOLD)))
        fig_age = format_fig(fig_age)

        pos = (
            dff.groupby(["Player Country", "Position Group"])
            .size()
            .reset_index(name="Goals")
        )
        fig_pos = px.bar(
            pos,
            x="Player Country",
            y="Goals",
            color="Position Group",
            barmode="stack",
        )
        fig_pos = format_fig(fig_pos)

        return (
            f"{n_goals:,}",
            f"{n_teams:,}",
            f"{n_scorers:,}",
            f"{avg_age:.1f}" if pd.notna(avg_age) else "—",
            f"{avg_min:.1f}'" if pd.notna(avg_min) else "—",
            fig_country,
            fig_box,
            fig_age,
            fig_pos,
        )
