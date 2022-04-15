import logging
from typing import List, Tuple, Set
from sportsipy.ncaab.roster import Player
from sportsipy.ncaab.teams import Team, Teams
import pandas as pd
from tenacity import retry, wait_exponential, before_log, stop_after_attempt, retry_if_exception_type

logging.basicConfig()
logger = logging.getLogger()
all_player_dfs: List[pd.DataFrame] = []
all_career_dfs: List[pd.DataFrame] = []
all_seasons: Set[int] = set()

years = tuple(range(2010, 2021))
start_year = years[0]
end_year = years[-1]

ncaa_career_fn = f'ncaa-player-career-stats-{start_year}-{end_year}.csv'
ncaa_players_yearly_fn = f'ncaa-players-season-stats-{start_year}-{end_year}.csv'
player_yearly_primary_key = ['player_id', 'team_abbreviation', 'season']


def get_year_tups(season_str_tuples: List[Tuple[str]]) -> List[Tuple[int, int]]:
    year_tup_list = []
    for season_str_tup in season_str_tuples:
        season_str = season_str_tup[0]
        ugly_year_list = season_str.split('-')  # '2017-18' -> ['2017', '18']
        pretty_year_one = int(ugly_year_list[0])
        pretty_year_two = int(f'20{ugly_year_list[1]}')
        year_tup_list.append((pretty_year_one, pretty_year_two))
    return year_tup_list


def run():
    for year in years:
        process_year(year)

    sorted_seasons = sorted(all_seasons)
    season_abs_year_map = {season: abs_year for abs_year, season in enumerate(sorted_seasons)}

    for df in all_player_dfs:
        df['abs_season'] = [season_abs_year_map[pkey[2]] for pkey in df.index.tolist()]
        df['abs_season_order'] = df['abs_season'] + df['season_order']

    pd.concat(all_player_dfs).to_csv(ncaa_players_yearly_fn)
    pd.concat(all_career_dfs).to_csv(ncaa_career_fn)


@retry(
    retry=retry_if_exception_type(IOError),
    wait=wait_exponential(min=30, max=60),
    stop=(stop_after_attempt(5)),
    before=before_log(logger, logging.INFO))
def process_year(year: int):
    print('Pulling data for year: ', year)
    teams_this_year = Teams(year)
    for team in teams_this_year:
        process_team(team)


@retry(
    retry=retry_if_exception_type(IOError),
    wait=wait_exponential(min=30, max=60),
    stop=(stop_after_attempt(5)),
    before=before_log(logger, logging.INFO))
def process_team(team: Team):
    print('Pulling data for team: ', team)
    for player in team.roster.players:
        process_player(player)


@retry(
    retry=retry_if_exception_type(IOError),
    wait=wait_exponential(min=30, max=60),
    stop=(stop_after_attempt(5)),
    before=before_log(logger, logging.INFO))
def process_player(player: Player):
    player_id = player.player_id
    print('Processing data for player: ', player_id)
    player_df: pd.DataFrame = player.dataframe
    player_career_df: pd.DataFrame = player_df.loc['Career']
    player_df = player_df.drop(index='Career')
    player_career_df.rename(index={'Career': player_id}, inplace=True)
    player_years: Set[int] = set()
    player_seasons: Set[str] = set()
    primary_key_list: List[Tuple[str]] = player_df.index.values.tolist()  # Ex: [('2017-18',),... ('Career',)]
    year_tup_list: List[Tuple[int, int]] = get_year_tups(primary_key_list)
    for year_tup in year_tup_list:
        season = f'{year_tup[0]}-{year_tup[1]}'
        player_seasons.add(season)
        player_years.update(year_tup)
        all_seasons.update(player_seasons)
    player_seasons: Tuple[str, ...] = tuple(sorted(player_seasons))
    player_years: Tuple[int, ...] = tuple(sorted(player_years))
    player_df = get_updated_player_df(player_df, player_seasons)
    player_df.set_index(player_yearly_primary_key, verify_integrity=True, inplace=True)
    player_career_df = get_updated_career_df(player_career_df, player_seasons, player_years)
    all_career_dfs.append(player_career_df)
    all_player_dfs.append(player_df)


def get_updated_player_df(player_df: pd.DataFrame, player_seasons: Tuple[str, ...]):
    num_seasons = len(player_seasons)
    player_df.loc[:, 'season'] = player_seasons
    zero_to_numseasons_minusone_list = list(range(num_seasons))
    player_df.loc[:, 'season_order'] = zero_to_numseasons_minusone_list
    return player_df


def get_updated_career_df(
        player_career_df: pd.DataFrame,
        player_seasons: Tuple[str, ...],
        player_years: Tuple[int, ...]) -> pd.DataFrame:
    '''
    This updates the single row Career dataframe so that it can be added for an "all players career" dataframe
    :param player_career_df: Single row dataframe from 'Career' row
    :param player_years: Variable Tuple of Strings for the years. Usually 6 total year options on 4 seasons.
           Not every player lasts through all of college
           Ex: ('2017', '2018', '2019', '2020')
    :return: Updated Dataframe
    '''
    first_year = min(player_years)
    last_year = max(player_years)
    num_seasons = len(player_seasons)
    num_years = last_year - first_year
    span_span = f'{first_year}-{last_year}'
    player_career_df.loc[:, 'num_seasons'] = num_seasons
    player_career_df.loc[:, 'num_years'] = num_years
    player_career_df.loc[:, 'span'] = span_span
    return player_career_df


run()
