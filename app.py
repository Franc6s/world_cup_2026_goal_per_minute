from dash import Dash, html, Input, Output

from theme import OFF_WHITE
from components import sidebar
from pages.overview import overview_layout, register_callbacks as register_overview_callbacks
from pages.country import country_layout, register_callbacks as register_country_callbacks
from pages.confederation import confed_layout, register_callbacks as register_confed_callbacks
from pages.venue import venue_layout, register_callbacks as register_venue_callbacks
from pages.referee import referee_layout, register_callbacks as register_referee_callbacks
from pages.insights import insights_layout, register_callbacks as register_insights_callbacks


app = Dash(__name__, suppress_callback_exceptions=True)
app.title = "World Cup 2026 Goal Analytics"

app.layout = html.Div(
    [
        sidebar,
   html.Div(
    id="page-content",
    style={
        "marginLeft": "265px",
        "padding": "30px",
        "backgroundColor": OFF_WHITE,
        "minHeight": "100vh",
        "boxSizing": "border-box",
    },
),
    ],
    style={"fontFamily": "Arial, sans-serif", "backgroundColor": OFF_WHITE},
)


@app.callback(
    Output("page-content", "children"),
    Input("page-selector", "value"),
)
def render_page(page):
    if page == "country":
        return country_layout
    if page == "confederation":
        return confed_layout
    if page == "venue":
        return venue_layout
    if page == "referee":
        return referee_layout
    if page == "insights":
        return insights_layout
    return overview_layout


register_overview_callbacks(app)
register_country_callbacks(app)
register_confed_callbacks(app)
register_venue_callbacks(app)
register_referee_callbacks(app)
register_insights_callbacks(app)


if __name__ == "__main__":
    app.run(debug=True)
