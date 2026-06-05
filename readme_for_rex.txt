as part of data collection, i will be doing the squad_form.csv and cup_finish.csv which are quite heavy.
I need your help in filling out the world cup csv, you can do it for the year 2018 for now.
Just leave the squad_form and previous_cup_finish column empty for now while doing the rest of the csv.

Important info:

team,year,host,confederation,elo_rating,,win_percentage_since_last_cup,goals_scored_per_game,goals_conceded_per_game,wc_appearances,previous_cup_finish,previous_wc_finish,squad_form,finish_stage

1. team - Team name
2. year - world cup year
3. host - 0 for not host, 1 for host (2014 was hosted by Brazil, 2018 was hosted by Russia, 2022 was hosted by Qatar)
4. elo_rating - https://eloratings.net/ go to this site, use yearly rating in the right hand side column to collect elo ratings of each team in the concerned year.
win_percentage_since_last_cup - go to sofascore, choose the required nation, go to matches, scroll to the last world cup game the team played BEFORE the current one,
count number of matches TILL the first game of the current wc, count no of wins, draws and losses in those matches, and calculate win %, formula : (no of wins/total games)*100
5. goals_scored_per_game - in THOSE SAME MATCHES as mentioned in the above row, count no of goals scored by the nation, divide it by no of games played.
6. goals_conceded_per_game - in THOSE SAME MATCHES as mentioned in the above row, count no of goals conceded by the nation, divide it by no of games played.
7. wc_appearances -  https://en.wikipedia.org/wiki/National_team_appearances_in_the_FIFA_World_Cup scroll down to the detailed table with year-wise entry for each team,
count the no of times the team had appeared at a world cup before the current tournament year (eg in 2014, count the no of times the team played at the 
world  cup before 2014.) "." means the team didnt qualify, "x" means the team was banned entry, count the number of times the team qualified.
8. previous_cup_finish - to be collected from previous_cup_finish.csv
9. previous_wc_finish - this is for the tournament BEFORE the current tournament. Also found in the same site mentioned in the previous row, "R1" for group stage exit, "R2" for round of 16 exit, "QF" for quarter final exit,
"4th" for 4th place finish, "3rd" for 3rd place finish, "2nd" for final loss, "1st" for winning the tournament. 
10. squad_form - to be collected from the squad_form.csv file
11. finish_stage - this is the tournament finish stage for the CURRENT tournament.