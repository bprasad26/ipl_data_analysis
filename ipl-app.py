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


external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
# read the data
points_table = load_data("points_table.csv")
points_table["Net R/R"] = points_table["Net R/R"].round(3)

wins_losses = load_data("wins_losses.csv")
wins_losses.sort_values(by=["Titles", "Win %"], ascending=[False, False], inplace=True)

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
    "Runs",
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


# plot strike rate
strike_rate_graph = px.scatter(
    batting[batting["Team"] != "Nan"],
    x="SR",
    y="Runs",
    color="Team",
    hover_name="PLAYER",
    hover_data=["Season"],
    trendline="ols",
)
strike_rate_graph.update_layout(
    title="Runs Vs Strike Rate", xaxis=dict(title="Strike Rate")
)


# plot 4s
fours_graph = px.scatter(
    batting[batting["Team"] != "Nan"],
    x="4s",
    y="Runs",
    color="Team",
    hover_name="PLAYER",
    hover_data=["Season"],
    trendline="ols",
)
fours_graph.update_layout(title="Runs Vs 4s")


# plot 6s graph
sixes_graph = px.scatter(
    batting[batting["Team"] != "Nan"],
    x="6s",
    y="Runs",
    color="Team",
    hover_name="PLAYER",
    hover_data=["Season"],
    trendline="ols",
)
sixes_graph.update_layout(title="Runs Vs 6s")


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

# scatter matrix plots
scatter_matrix_all = px.scatter_matrix(
    bowling, dimensions=["Wkts", "Dots", "SR", "Avg", "Econ"]
)
scatter_matrix_all.update_layout(height=550)

# players who have bowled more than 30 overs in a season
more_than_30_ov = bowling[bowling["Ov"] > 30]
scatter_matrix_30 = px.scatter_matrix(
    more_than_30_ov, dimensions=["Wkts", "Dots", "SR", "Avg", "Econ"]
)
scatter_matrix_30.update_layout(height=550)


app = dash.Dash()

server = app.server


app.layout = html.Div(
    [
        html.H1("IPL Stats (2008-2019)"),
        html.H3("by Bhola Prasad"),
        dcc.Markdown("#### Website - [Life With Data](https://www.lifewithdata.com/)"),
        ##### Points Table
        html.Div(
            [
                html.Div([], style={"height": "100px"}),
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
        html.Div([], style={"height": "45px"}),
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
        html.Div([], style={"height": "45px"}),
        html.H1("Batting Records"),
        html.Div(
            [
                html.Div([], style={"height": "25px"}),
                html.H2("Player Runs Per Season"),
                html.B("Select Players"),
                html.P("Use dropdown to select multiple players or remove them."),
                dcc.Dropdown(
                    id="select-player-ts",
                    options=[
                        {"label": player, "value": player}
                        for player in batting_players_list
                    ],
                    value=["Virat Kohli", "Rohit Sharma", "David Warner", "KL Rahul",],
                    multi=True,
                ),
                # Players Runs Time-Series Chart
                dcc.Graph(id="players-runs-time-series"),
            ],
            style={"margin": "40px 0", "width": "80%"},
        ),
        ###### Runs Distributions
        html.Div([], style={"height": "45px"}),
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
        html.Div([], style={"height": "25px"}),
        html.H3("All Time Records"),
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
        html.H3("Season Records"),
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
        # Player Performance
        html.Div([], style={"height": "80px"}),
        html.H2(
            "Why Strike Rate might not be the best predictor of player performance?"
        ),
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
                                    label="Strike Rate",
                                    children=[
                                        dcc.Graph(
                                            id="strike-rate-graph",
                                            figure=strike_rate_graph,
                                        )
                                    ],
                                ),
                                dcc.Tab(
                                    label="4s",
                                    children=[
                                        dcc.Graph(id="4s-graph", figure=fours_graph)
                                    ],
                                ),
                                dcc.Tab(
                                    label="6s",
                                    children=[
                                        dcc.Graph(id="6s-graph", figure=sixes_graph)
                                    ],
                                ),
                            ],
                        )
                    ]
                ),
                html.Div(
                    [
                        html.P(
                            "If you look at the Runs vs Strike Rate graph, you can see that as the strike "
                            "rate increases the runs made by the players does not increases. The vast majority "
                            "of the data is clustered around strike rate of 110 to 170. Which basically telling us "
                            "that a person could have a higher strike rate in a match or in a season but may end up "
                            "with low score. Let's see, how is that possible? "
                        ),
                        html.P(
                            "Let's say a player go out in the field and played only 2 balls. In one, he hit a six run "
                            "and in the second he got out. Now, he has a strike rate of 300. So, even though he has a "
                            "very high strike rate, he ended up with a very low score. Compared this to another player "
                            "who made 40 runs in the match with a strike rate of, let's 130. Even though the second player "
                            "have less than 50% of the strike rate of the first person, he is still doing a lot better."
                            "So, never judge two players based only on strike rate, always try to find out how much runs each "
                            "have made before making any decisions."
                        ),
                        html.B("Some other alternative metrics?"),
                        html.P(
                            "Some very good alternative metrics are the number of 4s or 6s a players hits in a match or "
                            "in a Season. Because even if you don't know how much runs each players have made, if you know "
                            "that one player hits only 5 fours in a season and another players hits 30 fours in a season "
                            "then you will instantly know that the second player is doing much better than the first one. "
                            "If you look at the 4s and 6s graph, you can see that as the number of 4s and 6s increases the "
                            "runs also increase. If a player is hitting more 4s and 6s, there are good chances that he is making "
                            "more runs. One more added benefit of using this metric is that hitting more 4s and 6s also increases "
                            "the strike rate of the player. Another great thing about this metric is hitting 4s and 6s is not an easy "
                            "task. A player have to be very skillful to do it consistently, which also tells you that the player has "
                            "good batting abilities."
                        ),
                    ],
                    style={"width": "85%"},
                ),
            ],
            style={"width": "75%"},
        ),
        # Bowling Records
        html.Div([], style={"height": "45px"}),
        html.H1("Bowling Records"),
        html.Div([], style={"height": "25px"}),
        html.H2("Player Wickets Per Season"),
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
            style={"width": "75%"},
        ),
        html.Div([], style={"height": "45px"}),
        html.H2("Wickets Distributions"),
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
                    style={"width": "65%", "float": "right", "display": "inline-block"},
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
                    [dcc.Graph(id="team-wickets-dist", figure=team_wickets_dist,)],
                    style={"width": "65%", "float": "right", "display": "inline-block"},
                ),
            ],
            style={"margin": "40px", "height": 500},
        ),
        # Bowling Leaderboard
        html.H2("Bowling Leaderboard"),
        html.Div([], style={"height": "25px"}),
        html.H3("All Time Records"),
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
                                    style_cell={"textAlign": "left"},
                                    style_data_conditional=[
                                        {
                                            "if": {"row_index": "odd"},
                                            "backgroundColor": "rgb(248, 248, 248)",
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
        html.H3("Season Records"),
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
        html.H2("When to use which bowling metrics apart from wickets?"),
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
                                    label="All Data",
                                    children=[
                                        dcc.Graph(
                                            id="scatter-matrix-all",
                                            figure=scatter_matrix_all,
                                        )
                                    ],
                                ),
                                dcc.Tab(
                                    label="> 30 overs",
                                    children=[
                                        dcc.Graph(
                                            id="scatter-matrix-30",
                                            figure=scatter_matrix_30,
                                        )
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),
                html.Div(
                    [
                        html.P(
                            "If you look at the above figure,you can see that as the number of dots ball increases "
                            "the number of wickets taken also increases. It is very hard to say that this is the cause "
                            "of it based on only correlation but there might be some truth because a players can only have "
                            "lots of dot balls if the player is highly skillful. Or it could be that players who throws less "
                            "overs tends to have less dot balls and also less wickets which make it feels like there is a some "
                            "relationship between them. Or perhaps, throwing more dot balls puts lots of pressure on the batsaman "
                            "and the batsman started to play reckless shots to release it and got out which we see all the time in "
                            "cricket. Nevertheless, having higher dot balls is always good for the bowler and for the team."
                        ),
                        html.P(
                            "Avg, Econ and SR shows negative correlation which we are expecting but the relationship "
                            "is weak. So, decreasing the Avg, Econ, SR might not increases the number of wickets taken "
                            "as much as we expect. But having lower value for all these metrics is always good. "
                        ),
                        html.P(
                            "We can also see that there is a very strong positive correlation between Strike rate(SR) "
                            "and Avg(bowling average). The reason could be that if on average a player takes less balls "
                            "to take wickets, the number of runs conceded per wickets might also will be lower and if "
                            "a bowler is taking more balls to take wickets, the average number of runs conceded might also "
                            "increase. But we can't say for sure. "
                        ),
                        html.P(
                            "Look in the other tab. When we seperated the bowlers who balls less than 30 overs in a season, "
                            "the relationship between the number of wickets taken and the number of dot balls still have a strong "
                            "positive relation but not as much as we are getting earlier. But the negative correlation between Avg "
                            "and SR with the Wickets taken do increase a lot. On the other hand, Econ still have weaker relationship "
                            "with wickets. "
                        ),
                        html.P(
                            "In bowling, as having a lower strike rate is better, a strike rate lower than 15 or 10 is a good cut off to "
                            "find good bowlers. And for bowling average, a player having a bowling average less than 20 is good."
                        ),
                    ],
                    style={"width": "85%"},
                ),
            ],
            style={"width": "75%"},
        ),
        # summary
        html.Div([], style={"height": "80px"}),
        html.H2("Summary"),
        html.Div([], style={"height": "25px"}),
        html.Div(
            [
                html.P(
                    "1. Even though Mumbai Indians won 1 more IPL title than Chennai Super Kings, "
                    "On average CSK players tends to perform better than MI players. Not only the "
                    "Players average runs are higher but also the number of wickets taken. Also "
                    "CSK has a higher match winning percentage than MI. "
                ),
                html.P(
                    "2. If a batsman is making more than 400 runs in a season and a bowler taking more "
                    "than 15 wickets in a season then their performance is really very good. They are doing "
                    "exceptionally well compared to others. "
                ),
                html.P(
                    "3. Apart from runs, measuring a batsman performance alone based on the Strike rate "
                    "might not be the best idea. A better metric would be the average/total number of "
                    "4s or 6s a batsman hits in a season respectively."
                ),
                html.P(
                    "4. And if we look at bowling metrics apart from wickets, it is much better to use "
                    "Dot balls, Bowling strike rate(SR) and bowling average(avg) if you are interested in "
                    "finding bowlers who can take more wickets for you than using Economy rate.Economy Rate "
                    "only tells you if a bowler is more or less economical. It is what it is."
                ),
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
    fig.add_shape(
        # Line Horizontal
        type="line",
        x0=2008,
        y0=406,
        x1=2019,
        y1=406,
        line=dict(color="LightSeaGreen", width=2, dash="dashdot",),
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
        xaxis=dict(title="Season"), yaxis=dict(title="Runs"), height=550,
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
        fig.add_trace(go.Bar(x=top_15[metric], y=top_15["PLAYER"], orientation="h",))
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
        fig.add_trace(go.Bar(x=df[metric], y=df["PLAYER"], orientation="h",))
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
    rev_metrics = ["Econ", "Avg", "SR", "Runs"]
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
        fig.add_trace(go.Bar(x=df[metric], y=df["PLAYER"], orientation="h",))
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
    rev_metrics = ["Econ", "Avg", "SR", "Runs"]
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
    rev_metrics = ["Econ", "Avg", "SR", "Runs"]
    if metric in rev_metrics:
        asc = True
    else:
        asc = False

    if team == "All Teams":
        df = df.sort_values(by=metric, ascending=asc)
        top_15 = df[:15]
        fig = go.Figure()
        fig.add_trace(go.Bar(x=top_15[metric], y=top_15["PLAYER"], orientation="h",))
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
        fig.add_trace(go.Bar(x=df[metric], y=df["PLAYER"], orientation="h",))
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
    rev_metrics = ["Econ", "Avg", "SR", "Runs"]
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
    app.run_server()

