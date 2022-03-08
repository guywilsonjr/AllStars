from typing import List
from sportsipy.ncaab.teams import Teams
import pandas as pd

year = '2020'
teams = Teams(year)
team_player_df_list: List[pd.DataFrame] = [player.dataframe for team in teams for player in team.roster.players()]
pd.concat(team_player_df_list).to_csv(f'allPlayer-{year}.csv')
