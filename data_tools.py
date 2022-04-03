from typing import List, Union

import pandas as pd
from dash import Dash

DataSlice = Union[str, List[str]]
from flask_caching import Cache


class Dataset:
    cache: Cache
    df: pd.DataFrame
    columns: List[str]

    def __init__(self, app: Dash, df: pd.DataFrame):
        self.cache = Cache(app.server,  config={"CACHE_TYPE": "SimpleCache"})
        self.df = df
        self.columns = self.df.columns

        @self.cache.memoize(timeout=1, source_check=True)
        def get_df_by_feature(features: DataSlice) -> pd.Series:
            return self.df[features]

        self.get_df_by_feature = get_df_by_feature

