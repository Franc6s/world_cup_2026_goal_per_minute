from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd

from data import goal_events, venue_matches
from theme import *
from components import card, graph_card, format_fig


# ============================================================
# VENUES
# ============================================================

venues = sorted(
    goal_events["Stadium Name"]
    .dropna()
    .unique()
)


# ============================================================
# CITY → STATE / PROVINCE
# ============================================================

CITY_STATE_MAP = {
    # --------------------------------------------------------
    # CANADA
    # --------------------------------------------------------
    "Toronto": "Ontario",
    "Vancouver": "British Columbia",

    # --------------------------------------------------------
    # MEXICO
    # --------------------------------------------------------
    "Guadalajara": "Jalisco",
    "Zapopan": "Jalisco",
    "Mexico City": "Mexico City",
    "Monterrey": "Nuevo León",

    # --------------------------------------------------------
    # UNITED STATES
    # --------------------------------------------------------
    "Arlington": "Texas",
    "Atlanta": "Georgia",
    "East Rutherford": "New Jersey",
    "Foxborough": "Massachusetts",
    "Houston": "Texas",
    "Inglewood": "California",
    "Kansas City": "Missouri",
    "Miami Gardens": "Florida",
    "Philadelphia": "Pennsylvania",
    "Santa Clara": "California",
    "Seattle": "Washington",
}


# ============================================================
# VENUE LAYOUT
# ============================================================

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

        # ====================================================
        # VENUE DROPDOWN
        # ====================================================

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
                    "Total Goals",
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
                    "State / Province",
                    value_id="venue-state",
                ),

                card(
                    "City Venue",
                    value_id="venue-city",
                ),
            ],
            style={
                "display": "grid",
                "gridTemplateColumns": "repeat(3, 1fr)",
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
                    "Host Country",
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


# ============================================================
# CALLBACKS
# ============================================================

def register_callbacks(app):

    @app.callback(
        Output("venue-goals", "children"),
        Output("venue-games", "children"),
        Output("venue-avg-attendance", "children"),
        Output("venue-country", "children"),
        Output("venue-state", "children"),
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

        # --------------------------------------------------------
        # COUNTRY VENUE
        # --------------------------------------------------------

        if dff["Country Venue"].notna().any():

            country_venue = (
                dff["Country Venue"]
                .dropna()
                .iloc[0]
            )

        else:

            country_venue = "—"

        # --------------------------------------------------------
        # CITY VENUE
        # --------------------------------------------------------

        if dff["City Venue"].notna().any():

            city_venue = (
                dff["City Venue"]
                .dropna()
                .iloc[0]
            )

        else:

            city_venue = "—"

        # --------------------------------------------------------
        # STATE / PROVINCE
        # --------------------------------------------------------

        state_venue = CITY_STATE_MAP.get(
            city_venue,
            "—",
        )

        # ========================================================
        # VENUE COUNTRY MAP
        # ========================================================
        #
        # The selected stadium determines the country displayed.
        # We intentionally use a country-level choropleth rather
        # than a city marker because latitude / longitude are not
        # currently in the dataset.
        # ========================================================

        selected_map_df = pd.DataFrame(
            {
                "Country Venue": [
                    country_venue
                ],
                "State Venue": [
                    state_venue
                ],
                "City Venue": [
                    city_venue
                ],
                "Stadium Name": [
                    selected_venue
                ],
                "Goals": [
                    n_goals
                ],
                "Games": [
                    n_games
                ],
                "Average Attendance": [
                    avg_attendance
                ],
            }
        )

        fig_map = px.choropleth(
            selected_map_df,

            locations="Country Venue",

            locationmode="country names",

            color="Goals",

            hover_name="Stadium Name",

            hover_data={
                "Country Venue": True,
                "State Venue": True,
                "City Venue": True,
                "Goals": True,
                "Games": True,
                "Average Attendance": ":,.0f",
            },

            color_continuous_scale=[
                [0, LIGHT_BLUE],
                [1, BLUE],
            ],
        )

        fig_map.update_geos(
            fitbounds="locations",
            visible=True,

            showland=True,
            landcolor="#F2F5F8",

            showcountries=True,
            countrycolor="#CED7E0",

            showocean=True,
            oceancolor="#EAF3FA",

            showcoastlines=True,
            coastlinecolor="#CED7E0",
        )

        fig_map.update_layout(
            paper_bgcolor=WHITE,

            margin=dict(
                l=5,
                r=5,
                t=10,
                b=5,
            ),

            coloraxis_showscale=False,
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

        fig_rank.update_xaxes(
            title="Goals",
            dtick=1,
        )

        fig_rank.update_yaxes(
            title="",
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
            (
                f"{avg_attendance:,.0f}"
                if pd.notna(avg_attendance)
                else "—"
            ),
            country_venue,
            state_venue,
            city_venue,
            fig_map,
            fig_rank,
            fig_timing,
        )