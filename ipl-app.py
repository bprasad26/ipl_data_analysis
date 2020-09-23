from dash_core_components.Graph import Graph
from dash_core_components.Markdown import Markdown
from dash_html_components.Div import Div
from dash_html_components.I import I
from pandas._config.config import options
from pandas.core.indexes import multi
from pandas.io.formats import style
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import os

# function for loading data
file_path = os.path.join(os.getcwd(), "data")


def load_data(filename, file_path=file_path):
    csv_path = os.path.join(file_path, filename)
    return pd.read_csv(csv_path)


# read the data
points_table = load_data("points_table.csv")
points_table["Net R/R"] = points_table["Net R/R"].round(3)
wins_losses = load_data("wins_losses.csv")
wins_losses.sort_values(by=["Titles", "Win %"], ascending=[False, False], inplace=True)
batting = load_data("batting.csv")
batting.iloc[batting[batting["PLAYER"] == "Rohit Sharma"].index, 16] = "Mumbai Indians"
batting_players_list = list(batting["PLAYER"].unique())
heading_markdown = """
# IPL Stats (2008-2019)
### by Bhola Prasad
#### Website - [Life With Data](https://www.lifewithdata.com/)
"""

# year list
year_list = [year for year in range(2019, 2007, -1)]

app = dash.Dash()

app.layout = html.Div(
    [
        html.H1("IPL Stats (2008-2019)"),
        html.H3("by Bhola Prasad"),
        dcc.Markdown("#### Website - [Life With Data](https://www.lifewithdata.com/)"),
        # Points Table
        html.Div(
            [
                html.H2("Points Table"),
                html.Div(
                    [
                        html.B("Select a Season"),
                        dcc.Dropdown(
                            id="points-year-selector",
                            options=[
                                {"label": str(year), "value": year}
                                for year in year_list
                            ],
                            value=2019,
                        ),
                        # points table data
                        dash_table.DataTable(
                            id="points-table",
                            columns=[
                                {"name": i, "id": i} for i in points_table.columns
                            ],
                            data=points_table.to_dict("records"),
                            sort_action="native",
                            style_cell={"textAlign": "left"},
                            style_data_conditional=[
                                {
                                    "if": {"row_index": "odd"},
                                    "backgroundColor": "rgb(248, 248, 248)",
                                },
                                {
                                    "if": {"column_id": "Team"},
                                    "backgroundColor": "#3D9970",
                                    "color": "white",
                                },
                                {
                                    "if": {
                                        "column_id": "Points",
                                        "row_index": [0, 1, 2, 3],
                                    },
                                    "backgroundColor": "#3D9970",
                                    "color": "white",
                                },
                            ],
                        ),
                    ],
                    style={"width": "70%", "display": "inline-block"},
                ),
                html.Div(
                    style={"width": "20%", "float": "right", "display": "inline-block"}
                ),
            ]
        ),
        # Team Wins and Losses Table
        html.Div(
            [
                html.H2("Team Wins, losses and draws"),
                # Wins, losses and draws data
                dash_table.DataTable(
                    id="wins-losses-table",
                    columns=[{"name": i, "id": i} for i in wins_losses.columns],
                    data=wins_losses.to_dict("records"),
                    sort_action="native",
                    style_cell={"textAlign": "left"},
                    style_data_conditional=[
                        {
                            "if": {"row_index": "odd"},
                            "backgroundColor": "rgb(248, 248, 248)",
                        },
                        {
                            "if": {"column_id": "Team"},
                            "backgroundColor": "#3D9970",
                            "color": "white",
                        },
                        {
                            "if": {"column_id": "Win %", "row_index": [0, 1]},
                            "backgroundColor": "#3D9970",
                            "color": "white",
                        },
                        {
                            "if": {"column_id": "Titles", "row_index": [0, 1]},
                            "backgroundColor": "#3D9970",
                            "color": "white",
                        },
                    ],
                ),
            ],
            style={"margin": "40px 0", "width": "70%", "display": "inline-block"},
        ),
        # Batting stats
        html.H1("Batting Records"),
        html.Div(
            [
                html.H2("Players Runs Over Time"),
                html.B("Select Players"),
                html.P("You can select Multiple players or remove them."),
                dcc.Dropdown(
                    id="select-player-ts",
                    options=[
                        {"label": player, "value": player}
                        for player in batting_players_list
                    ],
                    value=["Virat Kohli", "Rohit Sharma", "MS Dhoni", "David Warner"],
                    multi=True,
                ),
                # Players Runs Time-Series Chart
                dcc.Graph(id="players-runs-time-series"),
            ],
            style={"margin": "40px 0", "width": "80%"},
        ),
    ]
)


# update the points table
@app.callback(Output("points-table", "data"), [Input("points-year-selector", "value")])
def update_points_table(year):
    dff = points_table[points_table["Season"] == year]
    return dff.to_dict("records")


# update players runs time series chart
@app.callback(
    Output("players-runs-time-series", "figure"), [Input("select-player-ts", "value")]
)
def update_players_runs_ts(player_names):
    fig = go.Figure()
    for player in player_names:
        fig.add_trace(
            go.Scatter(
                x=batting[batting["PLAYER"] == player]["Season"],
                y=batting[batting["PLAYER"] == player]["Runs"],
                mode="lines",
                name=player,
            )
        )
    fig.update_layout(xaxis=dict(title="Season"), yaxis=dict(title="Runs"), height=550)
    return fig


if __name__ == "__main__":
    app.run_server(debug=True)

