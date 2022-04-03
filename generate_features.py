from typing import List, Dict
import pandas as pd
from constants import team_prefix, player_prefix


feat_fn_format = 'features.{}.list'
team_feat_fn = feat_fn_format.format(team_prefix)
player_feat_fn = feat_fn_format.format(player_prefix)

team_csv_fn = 'allteams.csv'
player_csv_fn ='allplayerinfo.csv'
prefix_to_fn_map: Dict[str, str] = {team_prefix: team_csv_fn, player_prefix: player_csv_fn}


def write_feats_to_file(file_name: str, feature_list: List[str]) -> None:
    with open(file_name, 'w') as team_feat_file:
        newline_separated_list: str = '\n'.join(feature_list)
        team_feat_file.write(newline_separated_list)


def generate_featurelist_files(prefix: str, csv_fn: str):
    '''
    Generates featurelist files for a given prefix after loading dataset from a csv file
    :param prefix: 'team' or 'player
    :param csv_fn: Filename of csv to pull dataset from
    '''

    df = pd.read_csv(csv_fn)
    feats = list(df.columns)[1:]
    featlist_fn = feat_fn_format.format(prefix)
    write_feats_to_file(featlist_fn, feats)


if __name__ == '__main__':
    for data_type, fn in prefix_to_fn_map.items():
        generate_featurelist_files(data_type, fn)
