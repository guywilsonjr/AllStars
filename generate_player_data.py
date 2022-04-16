import logging
import multiprocessing
import os
from concurrent.futures import ALL_COMPLETED

import boto3
from typing import List, Tuple, Set
import concurrent.futures

from sportsipy.ncaab.roster import Player
from sportsipy.ncaab.teams import Team, Teams
import pandas as pd
from tenacity import retry, wait_exponential, before_log, stop_after_attempt, retry_if_exception_type
from multiprocessing.managers import SharedMemoryManager
smm = SharedMemoryManager()
smm.start()  # Start the process that manages the shared memory blocks


q = multiprocessing.Queue()
num_cpus = os.cpu_count()
logging.basicConfig()
logger = logging.getLogger()
all_player_dfs: List[str] = []

all_seasons: Set[int] = set()
s3_bucket_name = 'nbarisingallstars'

years = tuple(range(2010, 2021))
num_years = len(years)
num_proc_workers = num_cpus - 1
num_workers_per_year = 400 // (num_proc_workers/num_years)
start_year = years[0]
ncaa_team_yearly_raw_fn_fmt = 'data/ncaa/team/yearly/{}/raw/ncaa-{}-stats.csv'

end_year = years[-1]

player_yearly_primary_key = ['player_id', 'team_abbreviation', 'season']
pre_existing_files = []
num_years = len(years)


def load_existing_files():
    bucket = boto3.resource('s3').Bucket(s3_bucket_name)
    existing_objs = bucket.objects.all()
    pre_existing_files.extend([str(obj.key) for obj in existing_objs])


load_existing_files()
print('Got preexisting files: ', pre_existing_files)


def upload_file_to_s3_if_not_exists(
        fn: str,
        csv_str: str,
        msg_if_exists: str,
        pre_msg: str,
        post_msg: str,
        existing_files
):


    s3 = boto3.resource("s3")

    bucket = s3.Bucket(s3_bucket_name)
    if fn in existing_files:
        print(msg_if_exists)
        return
    else:
        existing_files.add(fn)

    for s3_object in bucket.objects.filter(Prefix=fn):
        print(msg_if_exists)
        return

    print(pre_msg)
    bucket.put_object(Body=csv_str, Key=fn)
    print(post_msg)


def upload_player_data_if_not_exists(
        player_id: str,
        yearly_df: pd.DataFrame,
        career_df: pd.DataFrame,
        raw_df: pd.DataFrame,
        existing_files
        ):
    ncaa_career_fn_fmt = 'data/ncaa/player/career/ncaa-player-career-stats-{}.csv'
    ncaa_players_yearly_fn_fmt = 'data/ncaa/player/yearly/ncaa-players-season-stats-{}.csv'
    ncaa_players_raw_fn_fmt = 'data/ncaa/player/raw/ncaa-players-season-stats-{}.csv'
    existing_file_msg_fmt = 'Already Uploaded {} data on player: {}. Skipping'
    pre_upload_msg_fmt = 'Uploading {} data on player: {}'
    post_upload_msg_fmt = '{} data Upload on player: {} complete'

    existing_yearly_msg = existing_file_msg_fmt.format('Yearly', player_id)
    existing_career_msg = existing_file_msg_fmt.format('Career', player_id)
    existing_raw_msg = existing_file_msg_fmt.format('Raw', player_id)

    career_fn = ncaa_career_fn_fmt.format(player_id)
    yearly_fn = ncaa_players_yearly_fn_fmt.format(player_id)
    raw_fn = ncaa_players_raw_fn_fmt.format(player_id)

    career_pre_msg = pre_upload_msg_fmt.format('Career', player_id)
    career_post_msg = post_upload_msg_fmt.format('Career', player_id)
    yearly_pre_msg = pre_upload_msg_fmt.format('Yearly', player_id)
    yearly_post_msg = post_upload_msg_fmt.format('Yearly', player_id)
    raw_pre_msg = pre_upload_msg_fmt.format('Raw', player_id)
    raw_post_msg = post_upload_msg_fmt.format('Raw', player_id)

    career_exists = career_fn in existing_files
    yearly_exists = yearly_fn in existing_files
    raw_exists = career_fn in existing_files
    all_exist = all([career_exists, yearly_exists, raw_exists])
    if all_exist:
        print(f'All Exist for player: {player_id}. Skipping')
        return
    coro_args = []
    if not career_exists:
        coro_args.append({
        'fn': career_fn,
        'csv_str': career_df.to_csv(),
        'msg_if_exists': existing_career_msg,
        'pre_msg': career_pre_msg,
        'post_msg': career_post_msg,
        'existing_files': existing_files}
        )
    if not yearly_exists:
        coro_args.append({
            'fn': yearly_fn,
            'csv_str': yearly_df.to_csv(),
            'msg_if_exists': existing_yearly_msg,
            'pre_msg': yearly_pre_msg,
            'post_msg': yearly_post_msg,
            'existing_files': existing_files
        })
    if not raw_exists:
        coro_args.append({
            'fn': raw_fn,
            'csv_str': raw_df.to_csv(),
            'msg_if_exists': existing_raw_msg,
            'pre_msg': raw_pre_msg,
            'post_msg': raw_post_msg,
            'existing_files': existing_files}
        )
    return [upload_file_to_s3_if_not_exists(**coro_arg_set) for coro_arg_set in coro_args]


def upload_team_yearlydf_if_not_exists(team: str, df: pd.DataFrame, year: int, existing_files):
    ncaa_team_yearly_fn = ncaa_team_yearly_raw_fn_fmt.format(year, team).replace(' ', '')
    return upload_file_to_s3_if_not_exists(
        ncaa_team_yearly_fn,
        df.to_csv(),
        f'File: {ncaa_team_yearly_fn} already exists',
        f'Uploading File: {ncaa_team_yearly_fn}',
        f'Upload Complete for file: {ncaa_team_yearly_fn}',
        existing_files
    )


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
    print('Creating threadpool for ', num_years, 'years')

    with multiprocessing.Pool(processes=num_proc_workers) as executor:
        with multiprocessing.Manager() as manager:

            print('Threadpool created')
            years = [[i] for i in range(2010, 2021)]
            existing_files = manager.list([pre_existing_files])
            ress = executor.starmap(process_year, years, existing_files)
            for res in ress:
                print(res)


    # TODO: COMPILE THE DATA AT THE END
    '''
    sorted_seasons = sorted(all_seasons)
    season_abs_year_map = {season: abs_year for abs_year, season in enumerate(sorted_seasons)}

    
    for df in all_player_dfs:
        df['abs_season'] = [season_abs_year_map[pkey[2]] for pkey in df.index.tolist()]
        df['abs_season_order'] = df['abs_season'] + df['season_order']
        '''


@retry(
    retry=retry_if_exception_type(IOError),
    wait=wait_exponential(min=30, max=60),
    stop=(stop_after_attempt(5)),
    before=before_log(logger, logging.INFO))
def process_year(year: str, existing_files):
    year = int(year)
    jitter = 0
    teams_this_year = Teams(year)
    num_teams = len(teams_this_year)
    print('Year ', year, ': Creating threadpool for ', num_teams, 'teams')

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers_per_year) as executor:
        print('Threadpool created for year: ', year)

        team_year_tups = [(team, year, existing_files) for team in teams_this_year]
        print(team_year_tups)
        ress = executor.map(process_team, team_year_tups)
        for res in ress:
            print(res)

        print('Processing completed for year: ', year)


@retry(
    retry=retry_if_exception_type(IOError),
    wait=wait_exponential(min=30, max=60),
    stop=(stop_after_attempt(5)),
    before=before_log(logger, logging.INFO))
def process_team(team_year: Tuple[Team, int]):
    team = team_year[0]
    year = team_year[1]
    existing_files = team_year[2]
    ncaa_team_yearly_fn = ncaa_team_yearly_raw_fn_fmt.format(year, team).replace(' ', '')
    if ncaa_team_yearly_fn in existing_files:
        msg = f'File: {ncaa_team_yearly_fn}  already exists. Skipping'
        print(msg)
        return msg
    print('Pulling data for team: ', team)
    jitter = 1
    for player in team.roster.players:
        process_player(player, existing_files)

    print('Uploading Team DF data')
    upload_team_yearlydf_if_not_exists(team.name, team.dataframe, year, existing_files)
    print('Proccesing data for team: ', team, 'Complete')


@retry(
    retry=retry_if_exception_type(IOError),
    wait=wait_exponential(min=30, max=60),
    stop=(stop_after_attempt(5)),
    before=before_log(logger, logging.INFO))
def process_player(player: Player, existing_files):
    player_id = player.player_id
    for file in existing_files:
        if player_id in file:
            return
    print('Processing data for player: ', player_id)
    raw_df: pd.DataFrame = player.dataframe
    player_career_df: pd.DataFrame = raw_df.loc['Career']
    player_career_df = player_career_df.rename(index={'Career': player_id})
    player_df = raw_df.drop(index='Career')

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
    player_df = get_updated_player_df(player_df, player_seasons, )
    player_df = player_df.set_index(player_yearly_primary_key, verify_integrity=True)
    player_career_df = get_updated_career_df(player_career_df, player_seasons, player_years)
    print('Uploading player data for player: ', player_id)
    upload_player_data_if_not_exists(player_id, player_df, player_career_df, raw_df, existing_files)
    print('Proccesing player: ', player_id, 'Complete')


def get_updated_player_df(player_df: pd.DataFrame, player_seasons: Tuple[str, ...]):
    print('updating')
    num_seasons = len(player_seasons)
    df = player_df
    df['season'] = player_seasons
    zero_to_numseasons_minusone_list = list(range(num_seasons))
    df['season_order'] = zero_to_numseasons_minusone_list
    return df


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
    df = player_career_df
    df['num_seasons'] = num_seasons
    df['num_years'] = num_years
    df['span'] = span_span
    return df


run()
