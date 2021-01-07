import warnings

warnings.simplefilter(action="ignore", category=UserWarning)
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
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import os
import base64

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
wins_losses.drop("Span", axis=1, inplace=True)

# read batting data
batting = load_data("batting.csv")
batting.iloc[batting[batting["PLAYER"] == "Rohit Sharma"].index, 16] = "Mumbai Indians"
batting_players_list = list(batting["PLAYER"].unique())

# batting aggregated data
batting_agg = load_data("batting_all_time.csv")


# read bowling data
bowling = load_data("bowling.csv")
bowling = bowling.rename(columns={"Maid": "Maiden"})
bowling_players_list = list(bowling["PLAYER"].unique())
# create a new column
bowling["Runs/Inns"] = (bowling["Runs"] / bowling["Inns"]).round(2)

# read bowling aggregated data
bowling_agg = load_data("bowling_all_time.csv")
# copy the data that is not avialable in aggregated csv
bowling_subset = bowling[["PLAYER", "Dots", "Maiden"]].copy()
# calculate aggregates and join
bs_groupby = bowling_subset.groupby("PLAYER").sum().reset_index()
bowling_agg = pd.merge(
    left=bowling_agg, right=bs_groupby, left_on="PLAYER", right_on="PLAYER"
)
# delete un-necessary column
bowling_agg.drop("Player Link", axis=1, inplace=True)
# create a new column
bowling_agg["Runs/Inns"] = (bowling_agg["Runs"] / bowling_agg["Inns"]).round(2)


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

bowling_metrics_list = [
    "Wkts",
    "Econ",
    "Avg",
    "SR",
    "Runs/Inns",
    "Dots",
    "4w",
    "5w",
    "Maiden",
    "Ov",
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


# function for adding local images
def encode_image(image_file):
    encoded = base64.b64encode(open(image_file, "rb").read())
    return "data:image/png;base64,{}".format(encoded.decode())


# Batting Feature Importances figures

batting_bar = os.getcwd() + "/images/batting_bar.png"
batting_beeswarm = os.getcwd() + "/images/batting_beeswarm.png"
batting_bf = os.getcwd() + "/images/batting_bf.png"
batting_sr = os.getcwd() + "/images/batting_sr.png"

# Bowling Feature Importances figures
bowling_bar = os.getcwd() + "/images/bowling_bar.png"
bowling_beeswarm = os.getcwd() + "/images/bowling_beeswarm.png"
bowling_sr = os.getcwd() + "/images/bowling_sr.png"
bowling_dots = os.getcwd() + "/images/bowling_dots.png"


###### Bowling plots

# wickets histogram
wickets_histogram = px.histogram(bowling, x="Wkts")
wickets_histogram.update_layout(
    title="Number of Wickets In A Season(2008-2019)",
    yaxis=dict(title="Player Count"),
    xaxis=dict(title="Number Of Wickets"),
)

# wickets taken by teams distribution
team_wickets_dist = px.box(bowling[bowling["Team"] != "Nan"], x="Wkts", y="Team")
team_wickets_dist.update_layout(
    title="Wickets Taken Per Season (2008-2019)",
    yaxis=dict(title="Players Team"),
    xaxis=dict(title="Total Wickets"),
)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SOLAR])

server = app.server


app.layout = html.Div(
    [
        html.H1("IPL Stats (2008-2019)"),
        html.H4("by Bhola Prasad"),
        dcc.Markdown("##### Website - [Life With Data](https://www.lifewithdata.com/)"),
        ##### Points Table
        html.Div([], style={"height": "100px"}),
        html.H3("Points Table"),
        html.Div(
            [
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
                    ],
                    style={"width": "20%", "display": "inline-block"},
                ),
            ]
        ),
        html.Div(
            [
                html.Div(
                    [
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
                    style={"margin": "15px", "width": "70%"},
                )
            ]
        ),
        ####### Team Wins and Losses Table
        html.Div([], style={"height": "45px"}),
        html.H3("Team Records"),
        html.Div(
            [
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
            style={"margin": "15px", "width": "70%"},
        ),
        ###### Batting stats
        html.Div([], style={"height": "45px"}),
        html.H2("Batting Records"),
        html.Div(
            [
                html.Div([], style={"height": "25px"}),
                html.H4("Player Runs Per Season"),
                html.B("Select Players"),
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
                        "David Warner",
                        "KL Rahul",
                    ],
                    multi=True,
                ),
                # Players Runs Time-Series Chart
                dcc.Graph(id="players-runs-time-series"),
            ],
            style={"width": "70%"},
        ),
        ###### Runs Distributions
        html.Div([], style={"height": "45px"}),
        html.H3("Runs Distributions"),
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
                    style={"width": "60%", "float": "right", "display": "inline-block"},
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
                    [
                        dcc.Graph(
                            id="runs-kde-plot",
                            figure=runs_kde_plot,
                        )
                    ],
                    style={"width": "60%", "float": "right", "display": "inline-block"},
                ),
            ],
            style={"margin": "40px", "height": 500},
        ),
        # Batting Leaderboard - All Time
        html.H3("Batting Leaderboard"),
        html.Div([], style={"height": "25px"}),
        html.H4("All Time Records"),
        html.Div([], style={"height": "20px"}),
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
                                                        {
                                                            "label": team,
                                                            "value": team,
                                                        }
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
                                    style_table={"overflowX": "auto"},
                                    style_cell_conditional=[
                                        {
                                            "if": {"column_id": "PLAYER"},
                                            "textAlign": "center",
                                        },
                                    ],
                                    page_current=0,
                                    page_size=15,
                                    page_action="native",
                                )
                            ],
                        ),
                    ]
                )
            ],
            style={"width": "75%"},
        ),
        # Season Records
        html.Div([], style={"height": "45px"}),
        html.H4("Season Records"),
        html.Div([], style={"height": "20px"}),
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
                                                    id="season-metric-selector",
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
                                                "width": "25%",
                                                "float": "left",
                                                "padding-right": "25px",
                                                "display": "inline-block",
                                            },
                                        ),
                                        html.Div(
                                            [
                                                html.Label("Season"),
                                                dcc.Dropdown(
                                                    id="season-year-selector",
                                                    options=[
                                                        {
                                                            "label": str(year),
                                                            "value": year,
                                                        }
                                                        for year in range(
                                                            2019, 2007, -1
                                                        )
                                                    ],
                                                    value=2019,
                                                ),
                                            ],
                                            style={
                                                "width": "25%",
                                                "float": "middle",
                                                "display": "inline-block",
                                            },
                                        ),
                                        html.Div(
                                            [
                                                html.Label("Team"),
                                                dcc.Dropdown(
                                                    id="season-team-selector",
                                                    options=[
                                                        {"label": team, "value": team}
                                                        for team in team_list
                                                    ],
                                                    value="All Teams",
                                                ),
                                            ],
                                            style={
                                                "width": "25%",
                                                "float": "right",
                                                "display": "inline-block",
                                            },
                                        ),
                                    ],
                                ),
                                html.Div([dcc.Graph(id="season-graph")]),
                            ],
                        ),
                        dcc.Tab(
                            label="Table",
                            children=[
                                dash_table.DataTable(
                                    id="season-records",
                                    columns=[
                                        {"name": i, "id": i}
                                        for i in batting.columns
                                        if i != "Player Link"
                                    ],
                                    data=batting.to_dict("records"),
                                    sort_action="native",
                                    style_cell={"textAlign": "left"},
                                    style_data_conditional=[
                                        {
                                            "if": {"row_index": "odd"},
                                            "backgroundColor": "rgb(248, 248, 248)",
                                        },
                                    ],
                                    style_table={"overflowX": "auto"},
                                    style_cell_conditional=[
                                        {
                                            "if": {"column_id": "POS"},
                                            "textAlign": "center",
                                        },
                                    ],
                                    page_current=0,
                                    page_size=15,
                                    page_action="native",
                                )
                            ],
                        ),
                    ]
                )
            ],
            style={"width": "75%"},
        ),
        # Features importances
        html.Div([], style={"height": "80px"}),
        html.H4("Important features for predicting players runs."),
        html.Div([], style={"height": "25px"}),
        html.Div(
            [
                html.Div(
                    [
                        dcc.Tabs(
                            id="tabs-with-classes",
                            value="tab-1",
                            parent_className="custom-tabs",
                            className="custom-tabs-container",
                            children=[
                                dcc.Tab(
                                    label="Feature Importances",
                                    children=[html.Img(src=encode_image(batting_bar))],
                                ),
                                dcc.Tab(
                                    label="FI Beeswarm",
                                    children=[
                                        html.Img(src=encode_image(batting_beeswarm))
                                    ],
                                ),
                                dcc.Tab(
                                    label="Ball Faced",
                                    children=[html.Img(src=encode_image(batting_bf))],
                                ),
                                dcc.Tab(
                                    label="Strike Rate",
                                    children=[html.Img(src=encode_image(batting_sr))],
                                ),
                            ],
                        )
                    ],
                    style={"width": "88%"},
                ),
                html.Div([], style={"height": "25px"}),
                html.Div(
                    [
                        html.H5("Feature Importances: "),
                        html.P(
                            "BF - This is the most important feature in predicting how much runs a player will make and"
                            "as the number of ball faced increases the number of runs also increases, so spending more"
                            "time on the field is even much more important than having a very higher strike rate. "
                        ),
                        html.P(
                            "SR - Second most important feature is strike rate and having a higher strike rate is good."
                        ),
                        html.P(
                            "4s and 6s - Hitting 4s is slightly more important than hitting 6s in making runs in the long "
                            "run. The reason cloud be hitting 4s is much easier than hitting 6s so most of the time players "
                            "tends to have more 4s than 6s and when added together, in the long run 4s generate more runs."
                        ),
                        html.P(
                            "Avg - Batting avg is also important but not as much as the above mentioned metrics."
                        ),
                    ],
                    style={"width": "85%"},
                ),
            ],
            style={"width": "75%"},
        ),
        # Bowling Records
        html.Div([], style={"height": "45px"}),
        html.H2("Bowling Records"),
        html.Div([], style={"height": "25px"}),
        html.H4("Player Wickets Per Season"),
        html.Div(
            [
                html.B("Select Players"),
                html.P(""),
                dcc.Dropdown(
                    id="select-player-wkts-ts",
                    options=[
                        {"label": player, "value": player}
                        for player in bowling_players_list
                    ],
                    value=[
                        "Jasprit Bumrah",
                        "Rashid Khan",
                        "Kagiso Rabada",
                        "Sunil Narine",
                        "Deepak Chahar",
                    ],
                    multi=True,
                ),
                dcc.Graph(id="players-wickets-time-series"),
            ],
            style={"width": "70%"},
        ),
        html.Div([], style={"height": "45px"}),
        html.H4("Wickets Distributions"),
        # Histogram of Wickets Distributions
        html.Div(
            [
                html.Div(
                    [
                        html.P(
                            "Just like runs, wickets distribution is also right skewed, means "
                            "many players takes low or medium number of wickets, while few "
                            "players takes lots of wickets.The median of this distribution is 5 "
                            "which means that 50% of the players taks less than 5 wickets and  "
                            "50% more than 5 wickets. 15 is the 90th percentile, meaning 90% "
                            "of the players takes less than 15 wickets. So, any players who "
                            "is taking more than or equal to 15 wickets in a season is doing "
                            "exceptionally well. "
                        )
                    ],
                    style={
                        "width": "30%",
                        "display": "inline-block",
                        "margin-top": "60px",
                    },
                ),
                html.Div(
                    [dcc.Graph(id="wickets-hist-plot", figure=wickets_histogram)],
                    style={"width": "60%", "float": "right", "display": "inline-block"},
                ),
            ],
            style={"margin": "40px", "height": 500},
        ),
        # Team wickets distributions
        html.Div(
            [
                html.Div(
                    [
                        html.P(
                            "On average, Chennai Super Kings bowlers also performs better "
                            "than any other teams. Rajasthan Royals has some good balance in "
                            "their team which is why their median wickets is second highest "
                            "after CSK but overall gets outperformed by other teams. And there "
                            "is lot of variability in Sunrisers hyderabad team, they have really "
                            "some high wickets takers but the team is not much balanced which is "
                            "why they have a very low median value. Out of all Royal Challengers "
                            "Banglore and Delhi Capitals is performing very poorly. "
                        )
                    ],
                    style={
                        "width": "30%",
                        "display": "inline-block",
                        "margin-top": "100px",
                    },
                ),
                html.Div(
                    [
                        dcc.Graph(
                            id="team-wickets-dist",
                            figure=team_wickets_dist,
                        )
                    ],
                    style={"width": "60%", "float": "right", "display": "inline-block"},
                ),
            ],
            style={"margin": "40px", "height": 500},
        ),
        # Bowling Leaderboard
        html.H3("Bowling Leaderboard"),
        html.Div([], style={"height": "25px"}),
        html.H4("All Time Records"),
        html.Div([], style={"height": "20px"}),
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
                                                    id="all-time-metric-selector-bowling",
                                                    options=[
                                                        {
                                                            "label": metric,
                                                            "value": metric,
                                                        }
                                                        for metric in bowling_metrics_list
                                                    ],
                                                    value="Wkts",
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
                                                    id="all-time-team-selector-bowling",
                                                    options=[
                                                        {
                                                            "label": team,
                                                            "value": team,
                                                        }
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
                                html.Div([dcc.Graph(id="all-time-graph-bowling")]),
                            ],
                        ),
                        dcc.Tab(
                            label="Table",
                            children=[
                                dash_table.DataTable(
                                    id="all-time-records-bowling",
                                    columns=[
                                        {"name": i, "id": i}
                                        for i in bowling_agg.columns
                                    ],
                                    data=bowling_agg.to_dict("records"),
                                    sort_action="native",
                                    style_cell={
                                        "textAlign": "left",
                                    },
                                    style_data_conditional=[
                                        {
                                            "if": {"row_index": "odd"},
                                            "backgroundColor": "rgb(248, 248, 248)",
                                        },
                                    ],
                                    style_table={"overflowX": "auto"},
                                    style_cell_conditional=[
                                        {
                                            "if": {"column_id": "POS"},
                                            "textAlign": "center",
                                        },
                                    ],
                                    page_current=0,
                                    page_size=15,
                                    page_action="native",
                                )
                            ],
                        ),
                    ]
                )
            ],
            style={"width": "75%"},
        ),
        # Season Records -  Bowling
        html.Div([], style={"height": "45px"}),
        html.H4("Season Records"),
        html.Div([], style={"height": "20px"}),
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
                                                    id="season-metric-selector-bowling",
                                                    options=[
                                                        {
                                                            "label": metric,
                                                            "value": metric,
                                                        }
                                                        for metric in bowling_metrics_list
                                                    ],
                                                    value="Wkts",
                                                ),
                                            ],
                                            style={
                                                "width": "25%",
                                                "float": "left",
                                                "padding-right": "25px",
                                                "display": "inline-block",
                                            },
                                        ),
                                        html.Div(
                                            [
                                                html.Label("Season"),
                                                dcc.Dropdown(
                                                    id="season-year-selector-bowling",
                                                    options=[
                                                        {
                                                            "label": str(year),
                                                            "value": year,
                                                        }
                                                        for year in range(
                                                            2019, 2007, -1
                                                        )
                                                    ],
                                                    value=2019,
                                                ),
                                            ],
                                            style={
                                                "width": "25%",
                                                "float": "middle",
                                                "display": "inline-block",
                                            },
                                        ),
                                        html.Div(
                                            [
                                                html.Label("Team"),
                                                dcc.Dropdown(
                                                    id="season-team-selector-bowling",
                                                    options=[
                                                        {"label": team, "value": team}
                                                        for team in team_list
                                                    ],
                                                    value="All Teams",
                                                ),
                                            ],
                                            style={
                                                "width": "25%",
                                                "float": "right",
                                                "display": "inline-block",
                                            },
                                        ),
                                    ],
                                ),
                                html.Div([dcc.Graph(id="season-graph-bowling")]),
                            ],
                        ),
                        dcc.Tab(
                            label="Table",
                            children=[
                                dash_table.DataTable(
                                    id="season-records-bowling",
                                    columns=[
                                        {"name": i, "id": i}
                                        for i in bowling.columns
                                        if i != "Player Link"
                                    ],
                                    data=bowling.to_dict("records"),
                                    sort_action="native",
                                    style_cell={"textAlign": "left"},
                                    style_data_conditional=[
                                        {
                                            "if": {"row_index": "odd"},
                                            "backgroundColor": "rgb(248, 248, 248)",
                                        },
                                    ],
                                    style_table={"overflowX": "auto"},
                                    style_cell_conditional=[
                                        {
                                            "if": {"column_id": "POS"},
                                            "textAlign": "center",
                                        },
                                    ],
                                    page_current=0,
                                    page_size=15,
                                    page_action="native",
                                )
                            ],
                        ),
                    ]
                )
            ],
            style={"width": "75%"},
        ),
        # bowler Performance
        html.Div([], style={"height": "80px"}),
        html.H4("Important features for predicting bowlers wickets."),
        html.Div([], style={"height": "25px"}),
        html.Div(
            [
                html.Div(
                    [
                        dcc.Tabs(
                            id="tabs-with-classes-bowling",
                            parent_className="custom-tabs-bowling",
                            className="custom-tabs-container-bowling",
                            children=[
                                dcc.Tab(
                                    label="Feature Importance",
                                    children=[html.Img(src=encode_image(bowling_bar))],
                                ),
                                dcc.Tab(
                                    label="FI Beeswarm",
                                    children=[
                                        html.Img(src=encode_image(bowling_beeswarm))
                                    ],
                                ),
                                dcc.Tab(
                                    label="Strike Rate",
                                    children=[html.Img(src=encode_image(bowling_sr))],
                                ),
                                dcc.Tab(
                                    label="Dots",
                                    children=[html.Img(src=encode_image(bowling_dots))],
                                ),
                            ],
                        ),
                    ],
                    style={"width": "82.5%"},
                ),
                html.Div([], style={"height": "25px"}),
                html.Div(
                    [
                        html.H5("Faeture Importance: "),
                        html.P(
                            "Ov - This is the most important feature for predicting wickets, the reason could be that as you ball "
                            "more overs the chances of getting wickets also increase compared to someone who only balls few overs."
                        ),
                        html.P(
                            "SR - Second most important feature is the Strike rate which is the average no. of balls bowled "
                            "per wicket taken and it is negatively correlated with the wickets which means having a lower "
                            "value of SR is good. The most interesting thing to note here is that SR is more important than the Economy rate. "
                            "When people try to access a player performance, people often look at there Economy rate and If we "
                            "look at the above Feature importance plot, you can see that it has very little or not effect on the "
                            "no. of wickets taken which is really surprising."
                        ),
                        html.P(
                            "Dots- Another good feature is the number of dot balls a player balls. As the numbers of dot balls increase "
                            "the chances of taking wickets also increases."
                        ),
                        html.P(
                            "Avg - Bowling average is also an important feature. It is the average number of runs conceded per wickets and "
                            "it is negatively correlated with the wickets taken so having a lower Avg is good."
                        ),
                        html.P(
                            "Econ - Economy rate of a bowler is not so important compared to other metrics seen above if you are interested in "
                            "predicting wickets. It just tell you if a bowler is economically good or not means if he gives less or more Runs per over. "
                            "It doesn't say too much about a bowlers wicket taking capabilities."
                        ),
                    ],
                    style={"width": "80%"},
                ),
            ],
            style={"width": "80%"},
        ),
        # summary
        html.Div([], style={"height": "80px"}),
        html.H3("Summary"),
        html.Div([], style={"height": "25px"}),
        html.Div(
            [
                html.P(
                    "1. Although Mumbai Indians won more titles than CSK, On average CSK players performs "
                    "better than MI. The average runs scored and wickets taken by CSK players is higher. "
                ),
                html.P(
                    "2. If a batsman is making more than 400 runs in a season and a bowler taking more "
                    "than 15 wickets in a season then their performance is really very good. They are doing "
                    "exceptionally well compared to others. "
                ),
                html.P(
                    "3. The most important features for predicting players runs are Ball Faced, Strike rate, "
                    "4s, 6s and Batting avg(for more information look at the above FI section)."
                ),
                html.P(
                    "4. Whether a players is indian or from overseas, it doesn't have any effect on the performance, "
                    "both tends to perform equally. We can't say overseas players are better than indian players."
                ),
                html.P(
                    "4. Important features for predicting wickets are bowlers Strike rate, Dots, Bowling average and "
                    "Economy. Although Economy rate of a bowler is not so important compared to other metrics mentioned "
                    "if you are interested in predicting wickets. It just tell you if a bowler is economically good or not "
                    "means if he gives less or more Runs per over. It doesn't say too much about a bowlers wicket taking capabilities "
                    "(see the Bowlers FI section for more info)."
                ),
                html.Div([], style={"height": "20px"}),
            ],
            style={"width": "65%"},
        ),
    ],
    style={"margin-left": "20px"},
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
    fig.add_shape(
        # Line Horizontal
        type="line",
        x0=2008,
        y0=406,
        x1=2019,
        y1=406,
        line=dict(
            color="LightSeaGreen",
            width=2,
            dash="dashdot",
        ),
    ),
    fig.add_annotation(
        text=" 90% of the players<br>makes less than 400 runs<br>in a season.",
        x=2009,
        y=406,
        xref="x",
        yref="y",
        showarrow=True,
        ax=0,
        ay=-70,
    )

    fig.update_layout(
        xaxis=dict(title="Season"),
        yaxis=dict(title="Runs"),
        height=550,
    )

    return fig


# All time Batting Graph
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
        fig.add_trace(
            go.Bar(
                x=df[metric],
                y=df["PLAYER"],
                orientation="h",
            )
        )
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


# Season batting graph
@app.callback(
    Output("season-graph", "figure"),
    [
        Input("season-metric-selector", "value"),
        Input("season-year-selector", "value"),
        Input("season-team-selector", "value"),
    ],
)
def update_batting_season_graph(metric, season, team):
    df = batting[batting["Season"] == season]
    if team == "All Teams":
        df = df.sort_values(by=metric, ascending=False)
        top_15 = df[:15]
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=top_15[metric],
                y=top_15["PLAYER"],
                orientation="h",
            )
        )
        fig.update_layout(
            title="Top {} Players {} ({})".format(team, metric, season),
            xaxis=dict(title="{}".format(metric)),
            yaxis=dict(autorange="reversed"),
            height=550,
        )
        return fig
    else:
        df = df[df["Team"] == team]
        df = df.sort_values(by=metric, ascending=False)
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=df[metric],
                y=df["PLAYER"],
                orientation="h",
            )
        )
        fig.update_layout(
            title="Top {} Players {} ({})".format(team, metric, season),
            xaxis=dict(title="{}".format(metric)),
            yaxis=dict(autorange="reversed"),
            height=550,
        )
        return fig


# sort season batting table based on the metric and team, year
@app.callback(
    Output("season-records", "data"),
    [
        Input("season-metric-selector", "value"),
        Input("season-year-selector", "value"),
        Input("season-team-selector", "value"),
    ],
)
def update_season_batting_table(metric, season, team):
    df = batting[batting["Season"] == season]
    if team == "All Teams":
        df = df.sort_values(by=metric, ascending=False)
        return df.to_dict("records")

    else:
        df = df[df["Team"] == team]
        df = df.sort_values(by=metric, ascending=False)
        return df.to_dict("records")


######### Bowling stats

# players wickets time series
@app.callback(
    Output("players-wickets-time-series", "figure"),
    [Input("select-player-wkts-ts", "value")],
)
def update_players_wickets_ts(player_names):
    fig = go.Figure()
    for player in player_names:
        fig.add_trace(
            go.Scatter(
                x=bowling[bowling["PLAYER"] == player]["Season"],
                y=bowling[bowling["PLAYER"] == player]["Wkts"],
                mode="lines",
                name=player,
            )
        )

    fig.update_layout(
        title="Total Wickets In A Season(2008-2019)",
        yaxis=dict(title="Total Wickets"),
        xaxis=dict(title="Season"),
        height=550,
    )
    return fig


# All time Bowling Graph
@app.callback(
    Output("all-time-graph-bowling", "figure"),
    [
        Input("all-time-metric-selector-bowling", "value"),
        Input("all-time-team-selector-bowling", "value"),
    ],
)
def update_all_time_graph_bowling(metric, team):
    df = bowling_agg
    # Select only non-zero values
    df = df[df[metric] != 0]
    # reverse logic for these metrics, less is better
    rev_metrics = ["Econ", "Avg", "SR", "Runs/Inns"]
    if metric in rev_metrics:
        asc = True
    else:
        asc = False

    if team == "All Teams":
        df = df.sort_values(by=metric, ascending=asc)
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
        team_df = bowling[bowling["Season"] == 2019][bowling["Team"] == team]
        # find all the unique players
        unique_player_list = team_df["PLAYER"].unique()
        # select only those players
        df = df[df["PLAYER"].isin(unique_player_list)]
        df = df.sort_values(by=metric, ascending=asc)
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=df[metric],
                y=df["PLAYER"],
                orientation="h",
            )
        )
        fig.update_layout(
            title="Top {} Players {} (2008-2019)".format(team, metric),
            xaxis=dict(title="{}".format(metric)),
            yaxis=dict(autorange="reversed"),
            height=550,
        )
        return fig


# sort the all time bowling table based on the metric
@app.callback(
    Output("all-time-records-bowling", "data"),
    [
        Input("all-time-metric-selector-bowling", "value"),
        Input("all-time-team-selector-bowling", "value"),
    ],
)
def update_all_time_table_bowling(metric, team):
    df = bowling_agg
    # Select only non-zero values
    df = df[df[metric] != 0]
    # reverse logic for these metrics, less is better
    rev_metrics = ["Econ", "Avg", "SR", "Runs/Inns"]
    if metric in rev_metrics:
        asc = True
    else:
        asc = False

    if team == "All Teams":
        df = df.sort_values(by=metric, ascending=asc)
        return df.to_dict("records")

    else:
        team_df = bowling[bowling["Season"] == 2019][bowling["Team"] == team]
        # find all the unique players
        unique_player_list = team_df["PLAYER"].unique()
        # select only those players
        df = df[df["PLAYER"].isin(unique_player_list)]
        df = df.sort_values(by=metric, ascending=asc)
        return df.to_dict("records")


# Season bowling graph
@app.callback(
    Output("season-graph-bowling", "figure"),
    [
        Input("season-metric-selector-bowling", "value"),
        Input("season-year-selector-bowling", "value"),
        Input("season-team-selector-bowling", "value"),
    ],
)
def update_batting_season_graph(metric, season, team):
    df = bowling[bowling["Season"] == season]
    # Select only non-zero values
    df = df[df[metric] != 0]
    rev_metrics = ["Econ", "Avg", "SR", "Runs/Inns"]
    if metric in rev_metrics:
        asc = True
    else:
        asc = False

    if team == "All Teams":
        df = df.sort_values(by=metric, ascending=asc)
        top_15 = df[:15]
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=top_15[metric],
                y=top_15["PLAYER"],
                orientation="h",
            )
        )
        fig.update_layout(
            title="Top {} Players {} ({})".format(team, metric, season),
            xaxis=dict(title="{}".format(metric)),
            yaxis=dict(autorange="reversed"),
            height=550,
        )
        return fig
    else:
        df = df[df["Team"] == team]
        df = df.sort_values(by=metric, ascending=asc)
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=df[metric],
                y=df["PLAYER"],
                orientation="h",
            )
        )
        fig.update_layout(
            title="Top {} Players {} ({})".format(team, metric, season),
            xaxis=dict(title="{}".format(metric)),
            yaxis=dict(autorange="reversed"),
            height=550,
        )
        return fig


# sort season bowling table based on the metric and team, year
@app.callback(
    Output("season-records-bowling", "data"),
    [
        Input("season-metric-selector-bowling", "value"),
        Input("season-year-selector-bowling", "value"),
        Input("season-team-selector-bowling", "value"),
    ],
)
def update_season_batting_table(metric, season, team):
    df = bowling[bowling["Season"] == season]
    # Select only non-zero values
    df = df[df[metric] != 0]
    # reverse logic for these metrics, less is better
    rev_metrics = ["Econ", "Avg", "SR", "Runs/Inns"]
    if metric in rev_metrics:
        asc = True
    else:
        asc = False

    if team == "All Teams":
        df = df.sort_values(by=metric, ascending=asc)
        return df.to_dict("records")

    else:
        df = df[df["Team"] == team]
        df = df.sort_values(by=metric, ascending=asc)
        return df.to_dict("records")


if __name__ == "__main__":
    app.run_server(debug=True)
