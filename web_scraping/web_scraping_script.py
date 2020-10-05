# import libraries
import requests
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup as bs
import time
import random
import re
import os


# Important Note ---
# change the value for which you want to scrape the data defaults to 2008-2019
year_list = [year for year in range(2019, 2007, -1)]


# project paths
project_root_dir = os.path.normpath(os.getcwd() + os.sep + os.pardir)
file_path = os.path.join(project_root_dir, "data")
os.makedirs(file_path, exist_ok=True)

# function for loading data
def load_data(filename, file_path=file_path):
    csv_path = os.path.join(file_path, filename)
    return pd.read_csv(csv_path)


# function for saving data as csv file
def save_dataframe(df, filename, file_path=file_path):
    """
    This function takes a dataframe and save it as a csv file.
    
    df: dataframe to save
    filename: Name to use for the csv file eg: 'my_file.csv'
    file_path = where to save the file
    """
    path = os.path.join(file_path, filename)
    df.to_csv(path, index=False)


def get_batting_data(year):
    """This function gets the data from ipl official website,
    extract all the table data and return it as a pandas dataframe.
    """
    try:
        # get the html from the website
        url = "https://www.iplt20.com/stats/{}/most-runs".format(year)
        response = requests.get(url)
        batting_html = response.text

        # parse the html
        batting_soup = bs(batting_html, features="lxml")
        # get the table data
        batting_table_data = batting_soup.find(class_="js-table")

        # get the column names
        col_names = []
        for header in batting_table_data.find_all("th"):
            col_names.append(header.text.strip())

        # create the dataframe
        a_list = []
        for data in batting_table_data.find_all("td"):
            a_list.append(" ".join(data.text.split()))

        n = 14
        final = [a_list[i : i + n] for i in range(0, len(a_list), n)]
        df = pd.DataFrame(final)
        df.columns = col_names

        # Add the nationality of each player in the dataframe
        nationality_list = []
        for index, data in enumerate(batting_table_data.find_all("tr")[1:]):
            try:
                nationality_list.append(data["data-nationality"])
            except Exception as e:
                print(e)
                print(index)
                # add none
                nationality_list.append(None)
        df["Nationality"] = nationality_list

        # Add the player link for more info in the dataframe
        base_url = "https://www.iplt20.com"
        player_link_list = []
        try:
            # get all the links and add it to the list
            for data in batting_table_data.find_all("a"):
                player_link_list.append(base_url + data["href"])

            # create a column with None value
            df[15] = None
            # iterate through each row and create a player name pattern
            for index, row in df.iterrows():
                player_name = row["PLAYER"].replace(" ", "-")
                player_regex = re.compile(r"{}".format(player_name), re.IGNORECASE)
                for item in player_link_list:
                    # if the pattern matches any links
                    if player_regex.search(item) != None:
                        # then append it to that row of the df
                        df.iloc[index, 15] = item
            # rename the column
            df.rename(columns={15: "Player Link"}, inplace=True)

            # extract the player team name from the link and add to the df
            team_regex = r"teams/(\w+-\w+-?\w+)"
            df["Team"] = df["Player Link"].str.extract(team_regex, flags=re.IGNORECASE)
            df["Team"] = df["Team"].apply(lambda x: str(x).title().replace("-", " "))

            # convert data types from string to numeric
            df["POS"] = pd.to_numeric(df["POS"], errors="coerce").fillna(0)
            df["Mat"] = pd.to_numeric(df["Mat"], errors="coerce").fillna(0)
            df["Inns"] = pd.to_numeric(df["Inns"], errors="coerce").fillna(0)
            df["NO"] = pd.to_numeric(df["NO"], errors="coerce").fillna(0)
            df["Runs"] = pd.to_numeric(df["Runs"], errors="coerce").fillna(0)
            df["HS"] = pd.to_numeric(
                df["HS"].str.replace("*", ""), errors="coerce"
            ).fillna(0)
            df["Avg"] = pd.to_numeric(df["Avg"], errors="coerce").fillna(0)
            df["BF"] = pd.to_numeric(df["BF"], errors="coerce").fillna(0)
            df["SR"] = pd.to_numeric(df["SR"], errors="coerce").fillna(0)
            df["100"] = pd.to_numeric(df["100"], errors="coerce").fillna(0)
            df["50"] = pd.to_numeric(df["50"], errors="coerce").fillna(0)
            df["4s"] = pd.to_numeric(df["4s"], errors="coerce").fillna(0)
            df["6s"] = pd.to_numeric(df["6s"], errors="coerce").fillna(0)

            # Add season year
            df["Season"] = year
        except Exception as e:
            print(e)
            print(year)

    except Exception as e:
        print(e)
        print(year)

    # return the dataframe
    return df


def combine_all_years_data(function, year_list):
    """
    Common function for combining data for all the years for a 
    given table from ipl website or any other. All table have
    different functions to get the data from the websites.
    """
    try:
        # create an empty list to hold all the dataframes
        df_list = []
        # loop through each year and extract the data
        for year in year_list:
            # call the function to get the data for that year
            df = function(year)
            # append the data to the df list
            df_list.append(df)
            # add some random pause
            time.sleep(1 + 2 * random.random())

        # concat all the dataframes
        df = pd.concat(df_list, ignore_index=True)

    except Exception as e:
        print(e)
        print(year)

    # return the dataframe
    return df


def get_points_table_data(year):
    """This Function takes the year value and extract the points table data
    from HowStat and return it as a Pandas Dataframe.
    """

    try:
        url = "http://www.howstat.com/cricket/Statistics/IPL/PointsTable.asp?s={}".format(
            year
        )
        response = requests.get(url)
    except Exception as e:
        print(e)
        print(year)

    try:
        # get the html text
        points_html_str = response.text
        # parse it using BeautifulSoup
        points_soup = bs(points_html_str, features="lxml")
        # Get all the Table data
        table_data = points_soup.find(class_="TableLined")

        # create an empty list
        a_list = []
        # loop through all the table data and extract the desired value and append
        # it to the empty list
        for data in table_data.find_all("td"):
            a_list.append(data.text.strip())

        # total item to put in a list as we have 10 columns
        n = 10
        # create a list of list each contains 10 items
        final = [a_list[i : i + n] for i in range(0, len(a_list), n)]

        # create a dataframe from the list of list
        df = pd.DataFrame(final)
        # set the column names which is in the 0th index
        df.columns = df.iloc[0]
        # drop the column names from the 0th index
        df = df.drop(df.index[0])

        # convert the data types of all the following columns
        col_to_convert = ["Mat", "Won", "Lost", "Tied", "N/R", "Points", "Net R/R"]
        # function for converting string to numerical values
        def convert_to_float(val):
            return float(val)

        # do the conversion for each column
        for col in col_to_convert:
            df[col] = df[col].apply(convert_to_float)

        # add season year
        df["Season"] = year

    except Exception as e:
        print(e)
        print("year:", year)
        print("Status Code:", response.status_code)

    # return the dataframe
    return df


def get_series_matches_data(year):
    """This function takes the year value and returns the series match
    data.
    """

    try:
        url = "http://howstat.com/cricket/Statistics/IPL/SeriesMatches.asp?s={}".format(
            year
        )
        response = requests.get(url)
    except Exception as e:
        print(e)
        print(year)

    try:
        # get the html text
        series_match_html = response.text
        # parse the html text
        series_soup = bs(series_match_html, features="lxml")
        # get the table data
        series_table_data = series_soup.find(class_="TableLined")
        # an empty list and append all the data to it
        a_list = []
        for data in series_table_data.find_all("td"):
            a_list.append(data.text.strip())

        n = 4
        final = [a_list[i : i + n] for i in range(0, len(a_list), n)]
        df = pd.DataFrame(final)
        df.columns = df.iloc[0]
        df = df.drop(df.index[0])

        # convert to datetime object
        df["Date"] = pd.to_datetime(df["Date"])
        # split the match number and teams names
        df[["Match Number", "Teams"]] = df["Match"].str.split(":", expand=True)
        # get the team A and team B names
        df[["Team A", "Team B"]] = df["Teams"].str.split("v", expand=True)

        # matching pattern for team names
        team_regex = r"""
        (Rajasthan\sRoyals|Kings\sXI\sPunjab|Chennai\sSuper\sKings|Delhi\sCapitals|Mumbai\sIndians|
        Kolkata\sKnight\sRiders|Royal\sChallengers\sBangalore|Deccan\sChargers|Kochi\sTuskers\sKerala|
        Pune\sWarriors|Sunrisers\sHyderabad|Gujarat\sLions|Rising\sPune\sSupergiant|No\sresult|Match\sabandoned)
        """
        # Extract the data
        df["winner"] = df["Result"].str.extract(
            team_regex, flags=re.VERBOSE | re.IGNORECASE
        )
        df["Wins By Runs"] = (
            df["Result"]
            .str.extract(r"(\d{1,3})\s(Runs|Run)", flags=re.IGNORECASE)
            .fillna(0)
            .iloc[:, 0]
        )
        df["Wins By Wickets"] = (
            df["Result"]
            .str.extract(r"(\d{1,2})\s(Wickets|Wicket)", flags=re.IGNORECASE)
            .fillna(0)
            .iloc[:, 0]
        )
        df["Season"] = df["Date"].dt.year

        # columns to drop
        cols_to_drop = ["Match", "Teams", "Result"]
        df = df.drop(cols_to_drop, axis=1)

        # convert strings to int
        df["Wins By Runs"] = df["Wins By Runs"].astype("int")
        df["Wins By Wickets"] = df["Wins By Wickets"].astype("int")

    except Exception as e:
        print(e)
        print(year)
        print(response.status_code)

    # return the dataframe
    return df


def get_fastest_fifties_data(year):
    """
    Get the fastest fifties data.
    """
    try:
        url = "https://www.iplt20.com/stats/{}/fastest-fifties".format(year)
        response = requests.get(url)
        fifties_html = response.text
        fifties_soup = bs(fifties_html, features="lxml")
        # get the table data
        fifties_table_data = fifties_soup.find(class_="js-table")

        # get the column names
        col_names = []
        for header in fifties_table_data.find_all("th"):
            col_names.append(header.text.strip())

        a_list = []
        for data in fifties_table_data.find_all("td"):
            a_list.append(" ".join(data.text.split()))

        n = 9
        final = [a_list[i : i + n] for i in range(0, len(a_list), n)]
        df = pd.DataFrame(final)
        df.columns = col_names

        # convert to datetime object
        df["Match Date"] = pd.to_datetime(df["Match Date"])

        # convert data types
        df["POS"] = pd.to_numeric(df["POS"], errors="coerce").fillna(0)
        df["BF"] = pd.to_numeric(df["BF"], errors="coerce").fillna(0)
        df["6s"] = pd.to_numeric(df["6s"], errors="coerce").fillna(0)
        df["4s"] = pd.to_numeric(df["4s"], errors="coerce").fillna(0)
        df["Runs"] = pd.to_numeric(df["Runs"], errors="coerce").fillna(0)

        # Add season year
        df["Season"] = year

    except Exception as e:
        print(e)
        print(year)

    return df


def get_fastest_centuries_data(year):
    """
    Extract fastest centuries data for this year.
    """
    try:
        url = "https://www.iplt20.com/stats/{}/fastest-centuries".format(year)
        response = requests.get(url)
        centuries_html = response.text
        centuries_soup = bs(centuries_html, features="lxml")
        # get the table data
        centuries_table_data = centuries_soup.find(class_="js-table")

        # get the column names
        col_names = []
        for header in centuries_table_data.find_all("th"):
            col_names.append(header.text.strip())

        a_list = []
        for data in centuries_table_data.find_all("td"):
            a_list.append(" ".join(data.text.split()))

        n = 9
        final = [a_list[i : i + n] for i in range(0, len(a_list), n)]
        df = pd.DataFrame(final)
        df.columns = col_names

        # convert to datetime object
        df["Match Date"] = pd.to_datetime(df["Match Date"])

        # convert data from string to numeric
        df["POS"] = pd.to_numeric(df["POS"], errors="coerce").fillna(0)
        df["BF"] = pd.to_numeric(df["BF"], errors="coerce").fillna(0)
        df["6s"] = pd.to_numeric(df["6s"], errors="coerce").fillna(0)
        df["4s"] = pd.to_numeric(df["4s"], errors="coerce").fillna(0)
        df["Runs"] = pd.to_numeric(df["Runs"], errors="coerce").fillna(0)

        # add season year
        df["Season"] = year

    except Exception as e:
        print(e)
        print(year)

    return df


def get_dot_balls_data(year):
    """This function gets the dot balls data for a particular year."""
    url = "https://www.iplt20.com/stats/{}/most-dot-balls".format(year)
    response = requests.get(url)
    dots_html = response.text
    dots_soup = bs(dots_html, features="lxml")
    dots_table_data = dots_soup.find(class_="js-table")
    # get the column names
    col_names = []
    for header in dots_table_data.find_all("th"):
        col_names.append(header.text.strip())

    a_list = []
    for data in dots_table_data.find_all("td"):
        a_list.append(" ".join(data.text.split()))

    n = 13
    final = [a_list[i : i + n] for i in range(0, len(a_list), n)]
    df = pd.DataFrame(final)
    df.columns = col_names

    # select only player name and Dots data
    df = df[["PLAYER", "Dots"]]
    # convert data type
    df["Dots"] = pd.to_numeric(df["Dots"], errors="coerce").fillna(0)
    return df


def get_maidens_data(year):
    """This function gets the player name and maidens
    data for a particular year.
    """
    try:
        url = "https://www.iplt20.com/stats/{}/most-maidens".format(year)
        response = requests.get(url)
        maidens_html = response.text
        maidens_soup = bs(maidens_html, features="lxml")
        maidens_table_data = maidens_soup.find(class_="js-table")
        # get the column names
        col_names = []
        for header in maidens_table_data.find_all("th"):
            col_names.append(header.text.strip())

        a_list = []
        for data in maidens_table_data.find_all("td"):
            a_list.append(" ".join(data.text.split()))

        n = 13
        final = [a_list[i : i + n] for i in range(0, len(a_list), n)]
        df = pd.DataFrame(final)
        df.columns = col_names

        # select only player name and maid column
        df = df[["PLAYER", "Maid"]]
        # change data type
        df["Maid"] = pd.to_numeric(df["Maid"], errors="coerce").fillna(0)

    except Exception as e:
        print(e)
        print(year)

    return df


def get_dots_maidens(year):
    """
    Combine the dots, maidens and data into a single df.
    """
    try:
        dots_df = get_dot_balls_data(year)
        maidens_df = get_maidens_data(year)
        # hats_df = get_hat_tricks_data(year)

        df = pd.merge(left=dots_df, right=maidens_df, how="left", on=["PLAYER"])
        # df = pd.merge(left=df, right=hats_df,how='left',on=['PLAYER'])
        # fill missing values
        df.fillna(0, inplace=True)
    except Exception as e:
        print(e)
        print(year)

    return df


def get_bowling_data(year):
    try:
        url = "https://www.iplt20.com/stats/{}/most-wickets".format(year)
        response = requests.get(url)
        bowling_html = response.text
        bowling_soup = bs(bowling_html, features="lxml")

        # get the table data
        bowling_table_data = bowling_soup.find(class_="js-table")

        # get the column names
        col_names = []
        for header in bowling_table_data.find_all("th"):
            col_names.append(header.text.strip())

        a_list = []
        for data in bowling_table_data.find_all("td"):
            a_list.append(" ".join(data.text.split()))

        n = 13
        final = [a_list[i : i + n] for i in range(0, len(a_list), n)]
        df = pd.DataFrame(final)
        df.columns = col_names

        # Add the nationality of each player in the dataframe
        nationality_list = []
        for index, data in enumerate(bowling_table_data.find_all("tr")[1:]):
            try:
                nationality_list.append(data["data-nationality"])
            except Exception as e:
                print(e)
                print(index)
                # add none
                nationality_list.append(None)
        df["Nationality"] = nationality_list

        # Add the player link for more info in the dataframe
        base_url = "https://www.iplt20.com"
        player_link_list = []

        # get all the links and add it to the list
        for data in bowling_table_data.find_all("a"):
            player_link_list.append(base_url + data["href"])

        # create a column with None value
        df[14] = None
        # iterate through each row and create a player name pattern
        for index, row in df.iterrows():
            player_name = row["PLAYER"].replace(" ", "-")
            player_regex = re.compile(r"{}".format(player_name), re.IGNORECASE)
            for item in player_link_list:
                # if the pattern matches any links
                if player_regex.search(item) != None:
                    # then append it to that row of the df
                    df.iloc[index, 14] = item
        # rename the column
        df.rename(columns={14: "Player Link"}, inplace=True)

        # extract the player team name from the link and add to the df
        team_regex = r"teams/(\w+-\w+-?\w+)"
        df["Team"] = df["Player Link"].str.extract(team_regex, flags=re.IGNORECASE)
        df["Team"] = df["Team"].apply(lambda x: str(x).title().replace("-", " "))

        # convert data types from string to numeric
        df["POS"] = pd.to_numeric(df["POS"], errors="coerce").fillna(0)
        df["Mat"] = pd.to_numeric(df["Mat"], errors="coerce").fillna(0)
        df["Inns"] = pd.to_numeric(df["Inns"], errors="coerce").fillna(0)
        df["Ov"] = pd.to_numeric(df["Ov"], errors="coerce").fillna(0)
        df["Runs"] = pd.to_numeric(df["Runs"], errors="coerce").fillna(0)
        df["Wkts"] = pd.to_numeric(df["Wkts"], errors="coerce").fillna(0)
        df["BBI"] = pd.to_numeric(df["BBI"], errors="coerce").fillna(0)
        df["Avg"] = pd.to_numeric(df["Avg"], errors="coerce").fillna(0)
        df["Econ"] = pd.to_numeric(df["Econ"], errors="coerce").fillna(0)
        df["SR"] = pd.to_numeric(df["SR"], errors="coerce").fillna(0)
        df["4w"] = pd.to_numeric(df["4w"], errors="coerce").fillna(0)
        df["5w"] = pd.to_numeric(df["5w"], errors="coerce").fillna(0)

        # extract the dots balls and maidens data
        df2 = get_dots_maidens(year)

        # combine both the dataframes
        df = pd.merge(left=df, right=df2, how="left", on=["PLAYER"])
        # fill missing values
        df.fillna(0, inplace=True)

        # add season year
        df["Season"] = year

    except Exception as e:
        print(e)
        print(year)

    # return dataframe
    return df


def get_wins_losses_data():
    win_losses = pd.read_html(
        "https://en.wikipedia.org/wiki/List_of_Indian_Premier_League_records_and_statistics"
    )
    # select the win losses table
    win_losses_df = win_losses[3]
    # drop the last
    win_losses_df.drop(win_losses_df.index[-1], inplace=True)
    # change names of the teams
    val_dict = {
        "CSK": "Chennai Super Kings",
        "DC": "Delhi Capitals",
        "KXIP": "Kings XI Punjab",
        "KKR": "Kolkata Knight Riders",
        "MI": "Mumbai Indians",
        "RR": "Rajasthan Royals",
        "RCB": "Royal Challengers Banglore",
        "SRH": "Sunrisers Hyderabad",
    }

    win_losses_df["Team"] = win_losses_df["Team"].map(val_dict)
    # rename the column
    win_losses_df.rename(columns={"Win\xa0%": "Win %"}, inplace=True)
    # columns list
    cols_list = [
        "Matches",
        "Won",
        "Lost",
        "No Result",
        "Tied and won",
        "Tied and lost",
        "Win %",
        "Titles",
    ]
    # convert data types
    for col in cols_list:
        win_losses_df[col] = pd.to_numeric(win_losses_df[col], errors="coerce").fillna(
            0
        )

    return win_losses_df


def batting_all_time_record(df):
    """This Function create the aggregated all the season data
    into a single dataframe.
    """
    agg_dict = {
        "Mat": "sum",
        "Inns": "sum",
        "NO": "sum",
        "Runs": "sum",
        "HS": "max",
        "Avg": "mean",
        "BF": "sum",
        "SR": "mean",
        "100": "sum",
        "50": "sum",
        "4s": "sum",
        "6s": "sum",
    }
    batting_all_time = (
        batting.groupby("PLAYER")
        .aggregate(agg_dict)
        .reset_index()
        .sort_values(by="Runs", ascending=False)
    )
    batting_all_time = batting_all_time.round(2)

    batting_all_time.index = np.arange(0, len(batting_all_time))

    return batting_all_time


def get_bowling_data_all_time():
    try:
        url = "https://www.iplt20.com/stats/all-time/most-wickets"
        response = requests.get(url)
        bowling_html = response.text
        bowling_soup = bs(bowling_html, "lxml")

        # get the table data
        bowling_table_data = bowling_soup.find(class_="js-table")

        # get the column names
        col_names = []
        for header in bowling_table_data.find_all("th"):
            col_names.append(header.text.strip())

        a_list = []
        for data in bowling_table_data.find_all("td"):
            a_list.append(" ".join(data.text.split()))

        n = 13
        final = [a_list[i : i + n] for i in range(0, len(a_list), n)]
        df = pd.DataFrame(final)
        df.columns = col_names

        # Add the nationality of each player in the dataframe
        nationality_list = []
        for index, data in enumerate(bowling_table_data.find_all("tr")[1:]):
            try:
                nationality_list.append(data["data-nationality"])
            except Exception as e:
                print(e)
                print(index)
                # add none
                nationality_list.append(None)
        df["Nationality"] = nationality_list

        # Add the player link for more info in the dataframe
        base_url = "https://www.iplt20.com"
        player_link_list = []

        # get all the links and add it to the list
        for data in bowling_table_data.find_all("a"):
            player_link_list.append(base_url + data["href"])

        # create a column with None value
        df[14] = None
        # iterate through each row and create a player name pattern
        for index, row in df.iterrows():
            player_name = row["PLAYER"].replace(" ", "-")
            player_regex = re.compile(r"{}".format(player_name), re.IGNORECASE)
            for item in player_link_list:
                # if the pattern matches any links
                if player_regex.search(item) != None:
                    # then append it to that row of the df
                    df.iloc[index, 14] = item
        # rename the column
        df.rename(columns={14: "Player Link"}, inplace=True)

        # extract the player team name from the link and add to the df
        team_regex = r"teams/(\w+-\w+-?\w+)"
        df["Team"] = df["Player Link"].str.extract(team_regex, flags=re.IGNORECASE)
        df["Team"] = df["Team"].apply(lambda x: str(x).title().replace("-", " "))

        # convert data types from string to numeric
        df["POS"] = pd.to_numeric(df["POS"], errors="coerce").fillna(0)
        df["Mat"] = pd.to_numeric(df["Mat"], errors="coerce").fillna(0)
        df["Inns"] = pd.to_numeric(df["Inns"], errors="coerce").fillna(0)
        df["Ov"] = pd.to_numeric(df["Ov"], errors="coerce").fillna(0)
        df["Runs"] = pd.to_numeric(
            df["Runs"].str.replace(",", ""), errors="coerce"
        ).fillna(0)
        df["Wkts"] = pd.to_numeric(df["Wkts"], errors="coerce").fillna(0)
        # df['BBI'] = pd.to_numeric(df['BBI'], errors='coerce').fillna(0)
        df["Avg"] = pd.to_numeric(df["Avg"], errors="coerce").fillna(0)
        df["Econ"] = pd.to_numeric(df["Econ"], errors="coerce").fillna(0)
        df["SR"] = pd.to_numeric(df["SR"], errors="coerce").fillna(0)
        df["4w"] = pd.to_numeric(df["4w"], errors="coerce").fillna(0)
        df["5w"] = pd.to_numeric(df["5w"], errors="coerce").fillna(0)

    except Exception as e:
        print(e)
        print(year)

    # return dataframe
    return df


if __name__ == "__main__":

    # get the points table data
    print()
    print("Getting Points table data.")
    points_table_df = combine_all_years_data(get_points_table_data, year_list)
    # save the data
    save_dataframe(points_table_df, "points_table.csv", file_path)
    print("completed")
    print()

    # get series matches data
    print("Getting Series Matches Data.")
    series_matches_df = combine_all_years_data(get_series_matches_data, year_list)
    save_dataframe(series_matches_df, "series_matches.csv", file_path)
    print("Completed")
    print()

    # get batting data
    print("Getting Batting Data")
    batting_df = combine_all_years_data(get_batting_data, year_list)
    save_dataframe(batting_df, "batting.csv", file_path)
    print("Completed")
    print()

    # create batting aggregated data
    print("Creating batting aggregated data")
    batting = load_data("batting.csv")
    batting_all_time = batting_all_time_record(batting)
    save_dataframe(batting_all_time, "batting_all_time.csv", file_path)
    print("Completed")
    print()

    # get fastest fifties data
    print("Getting Fastest Fifties Data.")
    fastest_fifties_df = combine_all_years_data(get_fastest_fifties_data, year_list)
    save_dataframe(fastest_fifties_df, "fastest_fifties.csv", file_path)
    print("Completed")
    print()

    # get fastest centuries data
    print("Getting Fastest Centuries Data.")
    fastest_centuries_df = combine_all_years_data(get_fastest_centuries_data, year_list)
    save_dataframe(fastest_centuries_df, "fastest_centuries.csv", file_path)
    print("Completed")
    print()

    # get wins losses data
    print("Getting Wins Losses Data")
    wins_losses_df = get_wins_losses_data()
    save_dataframe(wins_losses_df, "wins_losses.csv", file_path)
    print("Completed")
    print()

    # get bowling data
    print("Getting Bowling Data")
    bowling_df = combine_all_years_data(get_bowling_data, year_list)
    save_dataframe(bowling_df, "bowling.csv", file_path)
    print("Completed.")
    print()

    # get bowling data all time
    print("Getting bowling aggregated data")
    bowling_all_time = get_bowling_data_all_time()
    save_dataframe(bowling_all_time, "bowling_all_time.csv", file_path)
    print("Completed")
    print()
    print("I am done! Have Fun :)")

