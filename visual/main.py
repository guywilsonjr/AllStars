import functools
import logging
import os
import sys
from typing import Dict, List

import pandas
from icecream import ic
import pandas as pd
import plotly as plotly
from dash import dcc, Dash, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go


def setup_logging():
    logging.basicConfig()
    logger = logging.getLogger(__name__)
    ic.configureOutput(includeContext=True, outputFunction=logger.info)
    logger.addHandler(logging.StreamHandler(sys.stdout))
    return logger
    # logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG)

logger = setup_logging()
df: pd.DataFrame = pd.read_csv('playerInfo2018.csv')
dropdown_label_key: str = 'label'
dropdown_value_key: str = 'value'
default_view: str = 'points'


class DCCGraph:
    app: Dash
    df: pd.DataFrame
    dropdown_component: dcc.Dropdown
    dropdown_options: List[Dict[str, str]]
    dropdown_id: str = 'dropdown'
    hist_id: str = 'hist'

    def __init__(
        self,
        df: pd.DataFrame,
        default_col: str
    ) -> None:
        self.rev = {i: col for i, col in enumerate(df.columns)}
        self.df = df
        self.default_col = default_col
        self.setup_dropdown()
        self.setup_layout()

        @functools.lru_cache
        @self.app.callback(
            Output(component_id=self.hist_id, component_property='figure'),
            Input(component_id=self.dropdown_id, component_property='value')
        )
        def update_dropdown(dropdown_selection: str) -> plotly.graph_objs.Figure:
            ic(f'Updating output after receiving dropdown value: {dropdown_selection}')
            return self.create_histogram(col=dropdown_selection)

    def create_histogram(self, col: str, percentile: int=66):
        # TODO: create variable size partitions
        column_data: pandas.Series = self.df[col]
        hist_title = f'{col} Distribution'.replace('_', ' ').title()

        half_quantile = column_data.quantile(.5)
        first_half = df[df[col] < half_quantile][col]
        second_half = df[df[col] >= half_quantile][col]

        fig = go.Figure()
        fig.add_trace(go.Histogram(x=first_half))
        fig.add_trace(go.Histogram(x=second_half))

        fig.update_layout(barmode='stack')
        return fig

    def setup_layout(self) -> None:
        default_fig = px.histogram(df[self.default_col])
        self.app = Dash(__name__)
        self.app.layout = html.Div(children=[
            html.Div(children='''Main Window.'''),
            dcc.Graph(
                id='hist',
                figure=default_fig
            ),
            self.dropdown_component
        ])

    def setup_dropdown(self) -> None:
        self.dropdown_options = [{dropdown_label_key: col, dropdown_value_key: col} for i, col in enumerate(self.df.columns)]
        self.dropdown_component = dcc.Dropdown(
            id=self.dropdown_id,
            value=self.default_col,
            options=self.dropdown_options,
            persistence=True
        )


if __name__ == '__main__':
    graph = DCCGraph(df, default_view)
    graph.app.run_server(debug=True, port=9999)

