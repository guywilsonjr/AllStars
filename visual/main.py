import functools
import logging
import os
import sys
from typing import Dict, List
from icecream import ic
import pandas as pd
import plotly as plotly
from dash import dcc, Dash, html, Input, Output
import plotly.express as px


logging.basicConfig()
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))
# logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG)
ic.configureOutput(includeContext=True, outputFunction=logger.info)
df: pd.DataFrame = pd.read_csv('playerInfo2018.csv')
dropdown_label_key: str = 'label'
dropdown_value_key: str = 'value'
default_view: str = 'points'
env_pers_type: str = 'PERSISTENCE_TYPE'
env_pers: str = 'PERSISTENCE'
persistence_type: str = os.environ[env_pers_type] if env_pers_type in os.environ else 'local'
persistence_type: str = os.environ[env_pers] if env_pers in os.environ else True


class DCCGraph:
    app: Dash
    fig_cache: Dict[str, plotly.graph_objs.Figure]
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
            hist_title = f'{dropdown_selection} Distribution'.replace('_', ' ').title()
            return px.histogram(
                data_frame=df[dropdown_selection],
                title=hist_title,
                log_y=True
            )

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
    graph.app.run_server(debug=True)

