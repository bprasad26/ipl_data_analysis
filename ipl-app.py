from dash_core_components.Dropdown import Dropdown
from dash_core_components.Graph import Graph
from dash_core_components.Markdown import Markdown
from dash_html_components.Div import Div
from dash_html_components.H2 import H2
from dash_html_components.I import I
from dash_html_components.Label import Label
from dash_html_components.P import P
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

batting_agg = load_data("batting_all_time.csv")
# batting_agg = batting_agg.merge(batting[["PLAYER", "Team", "Nationality"]], on="PLAYER")
batting_metrics_list = [
    "Runs",
    "HS",
    "Avg",
    "BF",
    "SR",
    "100",
    "50",
    "4s",
    "6s",
    "Mat",
    "Inns",
    "NO",
]

team_list = [
    "All Teams",
    "Sunrisers Hyderabad",
    "Kings Xi Punjab",
    "Mumbai Indians",
    "Delhi Capitals",
    "Kolkata Knight Riders",
    "Royal Challengers Bangalore",
    "Chennai Super Kings",
    "Rajasthan Royals",
]


heading_markdown = """
# IPL Stats (2008-2019)
### by Bhola Prasad
#### Website - [Life With Data](https://www.lifewithdata.com/)
"""

# year list
year_list = [year for year in range(2019, 2007, -1)]

# players runs distribution plot
runs_dist_plot = px.histogram(batting, x="Runs")
runs_dist_plot.update_layout(title="Distribution of Player Runs(2008-2019)")

# players runs kde plot
import plotly.figure_factory as ff

unique_teams = batting["Team"].unique()

hist_data = [
    batting[batting["Team"] == team]["Runs"] for team in unique_teams if team != "Nan"
]
group_labels = ["SRH", "KXIP", "MI", "DC", "KKR", "RCB", "CSK", "RR"]
colors = ["Orange", "Silver", "Blue", "Black", "Gold", "Red", "Yellow", "Green"]

runs_kde_plot = ff.create_distplot(
    hist_data, group_labels, show_hist=False, show_rug=False, colors=colors
)
runs_kde_plot.update_layout(
    title="Kde Plot of Runs", xaxis=dict(title="Runs"), yaxis=dict(title="Density")
)


app = dash.Dash()


tabs_styles = {"height": "44px"}
tab_style = {
    "borderBottom": "1px solid #d6d6d6",
    "padding": "6px",
    "fontWeight": "bold",
}

tab_selected_style = {
    "borderTop": "1px solid #d6d6d6",
    "borderBottom": "1px solid #d6d6d6",
    "backgroundColor": "#119DFF",
    "color": "white",
    "padding": "6px",
}


app.layout = html.Div(
    [
        html.H1("IPL Stats (2008-2019)"),
        html.H3("by Bhola Prasad"),
        dcc.Markdown("#### Website - [Life With Data](https://www.lifewithdata.com/)"),
        ##### Points Table
        html.Div(
            [
                html.H2("Points Table"),
                html.Div(
                    [
                        html.Label("Select a Season"),
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
        ####### Team Wins and Losses Table
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
        ###### Batting stats
        html.H1("Batting Records"),
        html.Div(
            [
                html.H2("Player Runs Over Time"),
                html.Label("Select Players"),
                html.P("Use dropdown to select multiple players or remove them."),
                dcc.Dropdown(
                    id="select-player-ts",
                    options=[
                        {"label": player, "value": player}
                        for player in batting_players_list
                    ],
                    value=[
                        "Virat Kohli",
                        "Rohit Sharma",
                        "MS Dhoni",
                        "David Warner",
                        "KL Rahul",
                    ],
                    multi=True,
                ),
                # Players Runs Time-Series Chart
                dcc.Graph(id="players-runs-time-series"),
            ],
            style={"margin": "40px 0", "width": "80%"},
        ),
        ###### Runs Distributions
        html.H2("Runs Distributions"),
        # Histogram of Runs Distributions
        html.Div(
            [
                html.Div(
                    [
                        html.P(
                            "We can see that the distribution is right skewed. Many "
                            "players makes low or medium runs, while few players makes "
                            "lots of runs. The median of this distribution is 126 which "
                            "means that 50% of the players makes less than 126 runs and  "
                            "50% more than this. 406 is the 90th percentile, meaning 90% "
                            "of the players makes less than 406 runs. So, any players who "
                            "is making more than 400 runs in a season is really doing well. "
                            "They are in the top 10%."
                        )
                    ],
                    style={
                        "width": "30%",
                        "display": "inline-block",
                        "margin-top": "60px",
                    },
                ),
                html.Div(
                    [dcc.Graph(id="runs-dist-plot", figure=runs_dist_plot)],
                    style={"width": "65%", "float": "right", "display": "inline-block"},
                ),
            ],
            style={"margin": "40px", "height": 500},
        ),
        # Kernal density estimation of Runs distributions
        html.Div(
            [
                html.Div(
                    [
                        html.P(
                            "After segmenting the runs distribution by team, "
                            "it is clear that percentage of players making runs "
                            "within the 300 range is lower for csk compared to other "
                            "teams and the higher within the range 300 to 600, which is "
                            "what you want.Less percentage at the lower end and higher at "
                            "the middle and upper end. On average, csk players make 235 "
                            "runs,compared to 187 runs by Mumbai Indians which is the second "
                            "highest."
                        )
                    ],
                    style={
                        "width": "30%",
                        "display": "inline-block",
                        "margin-top": "100px",
                    },
                ),
                html.Div(
                    [dcc.Graph(id="runs-kde-plot", figure=runs_kde_plot,)],
                    style={"width": "65%", "float": "right", "display": "inline-block"},
                ),
            ],
            style={"margin": "40px", "height": 500},
        ),
        # Batting Leaderboard - All Time
        html.H2("Batting Leaderboard"),
        html.P(""),
        html.H3("All Time Records"),
        html.Div(
            [
                dcc.Tabs(
                    [
                        dcc.Tab(
                            label="Chart",
                            children=[
                                html.P(""),
                                html.Div(
                                    [
                                        html.Div(
                                            [
                                                html.Label("Select a Metric"),
                                                dcc.Dropdown(
                                                    id="all-time-metric-selector",
                                                    options=[
                                                        {
                                                            "label": metric,
                                                            "value": metric,
                                                        }
                                                        for metric in batting_metrics_list
                                                    ],
                                                    value="Runs",
                                                ),
                                            ],
                                            style={
                                                "width": "35%",
                                                "display": "inline-block",
                                            },
                                        ),
                                        html.Div(
                                            [
                                                html.Label("Select Team"),
                                                dcc.Dropdown(
                                                    id="all-time-team-selector",
                                                    options=[
                                                        {"label": team, "value": team,}
                                                        for team in team_list
                                                    ],
                                                    value="All Teams",
                                                ),
                                            ],
                                            style={
                                                "width": "35%",
                                                "float": "right",
                                                "display": "inline-block",
                                            },
                                        ),
                                    ]
                                ),
                                html.Div([dcc.Graph(id="all-time-graph")]),
                            ],
                        ),
                        dcc.Tab(
                            label="Table",
                            children=[
                                dash_table.DataTable(
                                    id="all-time-records",
                                    columns=[
                                        {"name": i, "id": i}
                                        for i in batting_agg.columns
                                    ],
                                    data=batting_agg.to_dict("records"),
                                    sort_action="native",
                                    style_cell={"textAlign": "left"},
                                    style_data_conditional=[
                                        {
                                            "if": {"row_index": "odd"},
                                            "backgroundColor": "rgb(248, 248, 248)",
                                        },
                                    ],
                                    page_current=0,
                                    page_size=20,
                                    page_action="native",
                                )
                            ],
                        ),
                    ]
                )
            ],
            style={"width": "75%"},
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
    fig.update_layout(
        xaxis=dict(title="Season"), yaxis=dict(title="Runs"), height=550,
    )
    return fig


# All time Graph
@app.callback(
    Output("all-time-graph", "figure"),
    [
        Input("all-time-metric-selector", "value"),
        Input("all-time-team-selector", "value"),
    ],
)
def update_all_time_graph(metric, team):
    df = batting_agg
    if team == "All Teams":
        df = df.sort_values(by=metric, ascending=False)
        top_15 = df[:15]
        fig = go.Figure()
        fig.add_trace(go.Bar(x=top_15[metric], y=top_15["PLAYER"], orientation="h"))
        fig.update_layout(
            title="Top {} Players {} (2008-2019)".format(team, metric),
            xaxis=dict(title="{}".format(metric)),
            yaxis=dict(autorange="reversed"),
            height=550,
        )
        return fig

    else:
        team_df = batting[batting["Season"] == 2019][batting["Team"] == team]
        # find all the unique players
        unique_player_list = team_df["PLAYER"].unique()
        # select only those players
        df = df[df["PLAYER"].isin(unique_player_list)]
        df = df.sort_values(by=metric, ascending=False)
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df[metric], y=df["PLAYER"], orientation="h",))
        fig.update_layout(
            title="Top {} Players {} (2008-2019)".format(team, metric),
            xaxis=dict(title="{}".format(metric)),
            yaxis=dict(autorange="reversed"),
            height=550,
        )
        return fig


# sort the all time table based on the metric
@app.callback(
    Output("all-time-records", "data"),
    [
        Input("all-time-metric-selector", "value"),
        Input("all-time-team-selector", "value"),
    ],
)
def update_all_time_table(metric, team):
    df = batting_agg
    if team == "All Teams":
        df = df.sort_values(by=metric, ascending=False)
        return df.to_dict("records")

    else:
        team_df = batting[batting["Season"] == 2019][batting["Team"] == team]
        # find all the unique players
        unique_player_list = team_df["PLAYER"].unique()
        # select only those players
        df = df[df["PLAYER"].isin(unique_player_list)]
        df = df.sort_values(by=metric, ascending=False)
        return df.to_dict("records")


if __name__ == "__main__":
    app.run_server(debug=True)

