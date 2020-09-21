# Data Descriptions - 

### 1. Batting.csv

* Pos - The position of a player in a particular season based on total runs.
* Player - The name of the player.
* Mat - Total matches in which a player was included in the playing 11.
* Inns - The number of innings in which the batsman actually batted.
* NO - The number of times the batsman was not out at the conclusion of an innings they batted in.
* Runs - Total Runs scored in a particular season.
* HS - The highest score ever made by the batsman in the season.
* Avg - Batting Average - The total number of runs divided by the total number of innings in which the batsman was out. Ave = Runs/[I – NO] (also Avge or Avg.).
* BF - Balls Faced - The total number of balls received, including no-balls but not including wides.
* SR - Strike Rate - The average number of runs scored per 100 balls faced. (SR = [100 * Runs]/BF).
* 100 - Number of times 100 runs(centuries) scored by a player.
* 50 - Number of times 50 runs(half-centuries) scored by a player.
* 4s - Number of times a player hits a 4.
* 6s - Number of times a player hits a 6.
* Nationality - Whether the palyed is indian or overseas.
* Team - The team the player belongs to.
* Season - The year the record belongs to.


### Bowling.csv
* Pos - The position of a player in a particular season based on Total wickets.
* Player - The name of the player.
* Mat - Total matches in which a player was included in the playing 11.
* Inns - The number of innings in which the bowler actually bowled.
* Ov - Overs - The number of overs bowled. The notation is (x.y) meaning x overs plus y balls have been bowled.
* Runs - The number of runs conceded by the bowler.
* Wkts - The number of wickets taken.
* BBI - BBI stands for Best Bowling in Innings and only gives the score for one innings. (If only the BB rate is given it's considered the BBI rate).
* Avg - Bowling Average -The average number of runs conceded per wicket. (Ave = Runs/W).
* Econ - Economy rate -The average number of runs conceded per over. (Econ = Runs/Overs bowled).
* SR - The average number of balls bowled per wicket taken. (SR = Balls/W).
* 4w - Four Wickets in an innings. The number of innings in which the bowler took exactly four wickets.
* 5w - Five Wickets in an innings. The number of innings in which the bowler took at least five wickets.
* Nationality - Whether the palyed is indian or overseas.
* Dots - Number of dot balls delivered by the bowler.
* Maid - The number of overs in which the bowler did not concede any runs.
* Season - The year the record belongs to.


### Fastest_Centuries.csv 
* Pos - The position of a player in a particular season based on higest runs in that inning.
* Player - The name of the player.
* Against - scored against which team.
* Venue - Where the match was played.
* Match Date - The date of the match.
* BF - Total balls faced to achieve the fastest century.
* 6s - Number of times a player hits a 6.
* 4s - Number of times a player hits a 4.
* Runs - Total runs scored in that match.
* Season - The year the record belongs to.

### fastest_fifties.csv
* Pos - The position of a player in a particular season based on higest runs in that inning.
* Player - The name of the player.
* Against - scored against which team.
* Venue - Where the match was played.
* Match Date - The date of the match.
* BF - Total balls faced to achieve the fastest fifty.
* 6s - Number of times a player hits a 6.
* 4s - Number of times a player hits a 4.
* Runs - Total runs scored in that match.
* Season - The year the record belongs to.

### Points_table.csv 
* Team - The name of the team.
* Mat - Total matches played by the team.
* Won - Total mathes won.
* Lost - Total matches lost.
* Tied - Total matches in which a match tied.
* N/R - 
* Points - Total points scored
* Net R/R - Net run rate - A method of ranking teams with equal points in limited overs league competitions.
* For - 
* Against - 
* Season - The year.

### Series_matches.csv
* Date - The date of the match.
* Ground/ Location- Where the match is played.
* Match Number - match serial number
* Team A - Name of the team A
* Team B - Name of the team B
* Winner - Which team won the match.
* Wins_by_runs - Wins by how much runs. In this case, wins_by_wickets will be 0.
* Wins_by_wickets - wins by how much wickets. In this case, wins_by_runs will be 0.\
* Season - The year the match belongs to.




