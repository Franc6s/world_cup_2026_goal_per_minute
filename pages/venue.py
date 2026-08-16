from dash import dcc, html, Input, Output
import plotly.express as px

from data import goal_events, venue_matches
from theme import *
from components import card, graph_card, format_fig

venues = sorted(goal_events["Stadium Name"].dropna().unique())

venue_layout = html.Div(
    [
        html.H1("Venue Profile", style={"margin": 0, "color": NAVY}),
        html.P(
            "Explore host cities, stadium scoring, attendance and goal timing.",
            style={"color": MUTED},
        ),

        dcc.Dropdown(
            id="venue-dropdown",
            options=[{"label": v, "value": v} for v in venues],
            value=venues[0] if venues else None,
            clearable=False,
            style={"width": "420px", "marginBottom": "20px"},
        ),

        html.Div(
            [
                card("Goals Scored", value_id="venue-goals"),
                card("Games Represented", value_id="venue-games"),
                card("Total Attendance", value_id="venue-attendance"),
                card("Avg Attendance", value_id="venue-avg-attendance"),
                card("Goals / Match", value_id="venue-gpm"),
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
                graph_card("World Cup Host Venues", "venue-map", 470),
                graph_card("Goals by Stadium", "venue-ranking", 470),
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
                graph_card("Attendance vs Match Goals", "attendance-scatter"),
                graph_card("Goal Timing at Selected Venue", "venue-timing"),
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
        Output("venue-goals", "children"),
        Output("venue-games", "children"),
        Output("venue-attendance", "children"),
        Output("venue-avg-attendance", "children"),
        Output("venue-gpm", "children"),
        Output("venue-map", "figure"),
        Output("venue-ranking", "figure"),
        Output("attendance-scatter", "figure"),
        Output("venue-timing", "figure"),
        Input("venue-dropdown", "value"),
    )
    def update_venue(selected_venue):
        dff = goal_events[goal_events["Stadium Name"] == selected_venue].copy()
        vm = venue_matches[venue_matches["Stadium Name"] == selected_venue].copy()

        n_goals = len(dff)
        n_games = dff["Match ID"].nunique()
        total_att = vm["Attendance"].sum()
        avg_att = vm["Attendance"].mean()
        gpm = n_goals / n_games if n_games else 0

        # Country-level host map. City/stadium detail is shown in hover.
        map_df = (
            venue_matches.groupby(["Country Venue", "City Venue", "Stadium Name"], dropna=False)
            .agg(
                Games=("Match ID", "nunique"),
                Attendance=("Attendance", "sum"),
            )
            .reset_index()
        )
        map_goals = (
            goal_events.groupby(["Country Venue", "City Venue", "Stadium Name"])
            .size()
            .reset_index(name="Goals")
        )
        map_df = map_df.merge(
            map_goals,
            on=["Country Venue", "City Venue", "Stadium Name"],
            how="left",
        )

        fig_map = px.scatter_geo(
            map_df,
            locations="Country Venue",
            locationmode="country names",
            size="Games",
            color="Goals",
            hover_name="Stadium Name",
            hover_data=["City Venue", "Games", "Goals", "Attendance"],
            projection="natural earth",
            color_continuous_scale=[[0, LIGHT_BLUE], [1, BLUE]],
        )
        fig_map.update_geos(
            showland=True,
            landcolor="#F2F5F8",
            showcountries=True,
            countrycolor="#CED7E0",
            showocean=True,
            oceancolor="#EAF3FA",
        )
        fig_map.update_layout(
            paper_bgcolor=WHITE,
            margin=dict(l=5, r=5, t=10, b=5),
            coloraxis_colorbar=dict(title="Goals"),
        )

        vr = (
            goal_events.groupby("Stadium Name")
            .size()
            .reset_index(name="Goals")
            .sort_values("Goals")
        )
        fig_rank = px.bar(
            vr,
            x="Goals",
            y="Stadium Name",
            orientation="h",
        )
        fig_rank.update_traces(marker_color=GOLD)
        fig_rank = format_fig(fig_rank)

        match_goal_counts = (
            goal_events.groupby("Match ID")
            .size()
            .reset_index(name="Goals")
        )
        match_att = (
            goal_events[
                ["Match ID", "Attendance", "Stadium Name", "Fixture"]
            ]
            .drop_duplicates("Match ID")
        )
        match_stats = match_att.merge(match_goal_counts, on="Match ID", how="left")

        fig_att = px.scatter(
            match_stats,
            x="Attendance",
            y="Goals",
            hover_name="Fixture",
            hover_data=["Stadium Name"],
            size="Goals",
            size_max=28,
        )
        fig_att.update_traces(marker=dict(color=BLUE, line=dict(width=1, color=GOLD)))
        fig_att = format_fig(fig_att)

        fig_timing = px.histogram(
            dff,
            x="Minute Scored",
            nbins=24,
        )
        fig_timing.update_traces(marker_color=BLUE)
        fig_timing.update_xaxes(range=[0, 120], dtick=15)
        fig_timing = format_fig(fig_timing)

        return (
            f"{n_goals:,}",
            f"{n_games:,}",
            f"{total_att:,.0f}" if pd.notna(total_att) else "—",
            f"{avg_att:,.0f}" if pd.notna(avg_att) else "—",
            f"{gpm:.2f}",
            fig_map,
            fig_rank,
            fig_att,
            fig_timing,
        )
