from typing import List, Union, Final, Optional

import pandas as pd
from dash import Dash
from flask_caching import Cache


IntType = [pd.Int8Dtype, pd.Int16Dtype, pd.Int32Dtype, pd.Int64Dtype]
FloatType = [pd.Float32Dtype, pd.Float64Dtype]
NumberType = IntType + FloatType
DataSlice = Union[str, List[str]]  # DataSlice is a new "type" = String or List of Strings


class Dataset:
    '''
    DataSet class holds data in class variable :param df:. Also holds different functions commonly used with operating on data
    '''
    cache: Cache
    df: pd.DataFrame
    columns: List[str]
    cache_key_prefix_fmt: Final[str] = '{}-Dataset'
    cache_key_prefix: str

    def get_data(self) -> pd.Series:
        pass

    def get_df_by_feature(self) -> pd.Series:
        pass

    def __init__(self, app: Dash, df: pd.DataFrame):
        self.cache_key_prefix = self.cache_key_prefix_fmt.format(app.config.name)
        self.cache = Cache(app.server,  config={"CACHE_TYPE": "SimpleCache", 'CACHE_KEY_PREFIX': self.cache_key_prefix})
        self.df = df

        self.numeric_df = self.df.select_dtypes(include=NumberType)
        self.columns = self.df.columns

        @self.cache.memoize(source_check=True)
        def get_feature_series(features: DataSlice) -> pd.Series:
            return self.df[features]

        @self.cache.memoize(source_check=True)
        def taste(features: Optional[DataSlice] = None, n: int=10) -> pd.Series:
            '''
            Get a taste of data
            :param features: List of specific features requested
            :type features: String | List[str]
            :param n: Number of data
            :type n: int
            :return: n data point series using :param features: if specified
            :rtype: pd.Series
            '''
            return self.numeric_df[features].head() if features else self.numeric_df.head(n)

        @self.cache.memoize(source_check=True)
        def taste_all(features: Optional[DataSlice] = None) -> pd.Series:
            return self.df[features].head() if features else self.df.head()

        self.taste = taste
        self.get_df_by_feature = get_feature_series


