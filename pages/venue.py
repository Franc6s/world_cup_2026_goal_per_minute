from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
from data import goal_events, venue_matches
from theme import *
from components import card, graph_card, format_fig

venues = sorted(goal_events["Stadium Name"].dropna().unique())

venue_layout = html.Div(
    [
        html.H1(
            "Venue Profile",
            style={
                "margin": 0,
                "color": NAVY,
            },
        ),

        html.P(
            "Explore host cities, stadium scoring, attendance and goal timing.",
            style={
                "color": MUTED,
            },
        ),

        dcc.Dropdown(
            id="venue-dropdown",
            options=[
                {
                    "label": v,
                    "value": v,
                }
                for v in venues
            ],
            value=venues[0] if venues else None,
            clearable=False,
            style={
                "width": "420px",
                "marginBottom": "20px",
            },
        ),

        # ====================================================
        # KPI CARDS
        # ====================================================

        html.Div(
            [
                card(
                    "Total Goals Scored",
                    value_id="venue-goals",
                ),

                card(
                    "Games Represented",
                    value_id="venue-games",
                ),

                card(
                    "Average Attendance",
                    value_id="venue-avg-attendance",
                ),

                card(
                    "Country Venue",
                    value_id="venue-country",
                ),

                card(
                    "City Venue",
                    value_id="venue-city",
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
        # MAP + STADIUM RANKING
        # ====================================================

        html.Div(
            [
                graph_card(
                    "World Cup Host Venues",
                    "venue-map",
                    470,
                ),

                graph_card(
                    "Goals by Stadium",
                    "venue-ranking",
                    470,
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
        # GOALS PER QUARTER
        # ====================================================

        html.Div(
            [
                graph_card(
                    "Goals per Quarter",
                    "venue-timing",
                ),
            ],
            style={
                "display": "grid",
                "gridTemplateColumns": "1fr",
                "gap": "18px",
            },
        ),
    ]
)

def register_callbacks(app):

    @app.callback(
        Output("venue-goals", "children"),
        Output("venue-games", "children"),
        Output("venue-avg-attendance", "children"),
        Output("venue-country", "children"),
        Output("venue-city", "children"),
        Output("venue-map", "figure"),
        Output("venue-ranking", "figure"),
        Output("venue-timing", "figure"),
        Input("venue-dropdown", "value"),
    )
    def update_venue(selected_venue):

        # ========================================================
        # FILTER SELECTED VENUE
        # ========================================================

        dff = goal_events[
            goal_events["Stadium Name"] == selected_venue
        ].copy()

        vm = venue_matches[
            venue_matches["Stadium Name"] == selected_venue
        ].copy()

        # ========================================================
        # KPI METRICS
        # ========================================================

        n_goals = len(dff)

        n_games = dff["Match ID"].nunique()

        avg_attendance = vm["Attendance"].mean()

        # Country Venue
        if dff["Country Venue"].notna().any():

            country_venue = (
                dff["Country Venue"]
                .dropna()
                .iloc[0]
            )

        else:

            country_venue = "—"

        # City Venue
        if dff["City Venue"].notna().any():

            city_venue = (
                dff["City Venue"]
                .dropna()
                .iloc[0]
            )

        else:

            city_venue = "—"

        # ========================================================
        # VENUE MAP
        # ========================================================

        map_df = (
            venue_matches.groupby(
                [
                    "Country Venue",
                    "City Venue",
                    "Stadium Name",
                ],
                dropna=False,
            )
            .agg(
                Games=(
                    "Match ID",
                    "nunique",
                ),

                Attendance=(
                    "Attendance",
                    "sum",
                ),
            )
            .reset_index()
        )

        # Goal totals by stadium
        map_goals = (
            goal_events.groupby(
                [
                    "Country Venue",
                    "City Venue",
                    "Stadium Name",
                ]
            )
            .size()
            .reset_index(
                name="Goals"
            )
        )

        map_df = map_df.merge(
            map_goals,
            on=[
                "Country Venue",
                "City Venue",
                "Stadium Name",
            ],
            how="left",
        )

        # Filter map to selected venue
        selected_map_df = map_df[
            map_df["Stadium Name"] == selected_venue
        ].copy()

        fig_map = px.scatter_geo(
            selected_map_df,

            locations="Country Venue",

            locationmode="country names",

            size="Games",

            color="Goals",

            hover_name="Stadium Name",

            hover_data={
                "Country Venue": True,
                "City Venue": True,
                "Games": True,
                "Goals": True,
                "Attendance": True,
            },

            projection="natural earth",

            color_continuous_scale=[
                [0, LIGHT_BLUE],
                [1, BLUE],
            ],
        )

        fig_map.update_geos(
            showland=True,
            landcolor="#F2F5F8",

            showcountries=True,
            countrycolor="#CED7E0",

            showocean=True,
            oceancolor="#EAF3FA",

            # Focus map on selected venue's country
            fitbounds="locations",
        )

        fig_map.update_layout(
            paper_bgcolor=WHITE,

            margin=dict(
                l=5,
                r=5,
                t=10,
                b=5,
            ),

            coloraxis_colorbar=dict(
                title="Goals"
            ),
        )

        # ========================================================
        # GOALS BY STADIUM
        # ========================================================

        venue_ranking = (
            goal_events.groupby(
                "Stadium Name"
            )
            .size()
            .reset_index(
                name="Goals"
            )
            .sort_values(
                "Goals"
            )
        )

        fig_rank = px.bar(
            venue_ranking,

            x="Goals",

            y="Stadium Name",

            orientation="h",

            text="Goals",
        )

        fig_rank.update_traces(
            marker_color=GOLD,
            textposition="outside",
        )

        fig_rank = format_fig(
            fig_rank
        )

        # ========================================================
        # GOALS PER QUARTER
        # ========================================================

        quarter_order = [
            "1–15",
            "16–30",
            "31–45",
            "46–60",
            "61–75",
            "76–90",
            "91–105",
            "106–120",
        ]

        venue_quarters = (
            dff["Goal Period"]
            .value_counts()
            .reindex(
                quarter_order,
                fill_value=0,
            )
            .reset_index()
        )

        venue_quarters.columns = [
            "Quarter",
            "Goals",
        ]

        fig_timing = px.bar(
            venue_quarters,

            x="Quarter",

            y="Goals",

            text="Goals",
        )

        fig_timing.update_traces(
            marker_color=BLUE,
            textposition="outside",
        )

        fig_timing.update_xaxes(
            title="Match Period"
        )

        fig_timing.update_yaxes(
            title="Goals Scored",
            dtick=1,
        )

        fig_timing = format_fig(
            fig_timing
        )

        # ========================================================
        # RETURN
        # ========================================================

        return (
            f"{n_goals:,}",
            f"{n_games:,}",
            f"{avg_attendance:,.0f}"
            if pd.notna(avg_attendance)
            else "—",
            country_venue,
            city_venue,
            fig_map,
            fig_rank,
            fig_timing,
        )

