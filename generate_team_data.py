from typing import List
import pandas as pd
from sportsipy.ncaab.teams import Teams


df_list: List[pd.DataFrame] = [team.dataframe for team in Teams()]
pd.concat(df_list).to_csv('allteams.csv')
