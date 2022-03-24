import os
# Use functools.lru_cache implements a simple hashmap as a cache
import functools
# Sys needed to do logging correctly. why do logging? https://stackoverflow.com/questions/6918493/in-python-why-use-logging-instead-of-print
import logging
import sys
# icream logging even better https://github.com/gruns/icecream
from icecream import ic
# For using typehints: https://docs.python.org/3/library/typing.html
from typing import Dict, List
import pandas as pd

# Use Plotly and Dash for nice visuals
# Plotly: https://plotly.com/python/
# Dash: https://dash.plotly.com/installation
# Same company makes Plotly and Dash. Plotly for Open source pretty plots. Dash for dashboards containing plots.
import plotly as plotly
from dash import dcc, Dash, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go

# Get current directory
dir_path = os.path.dirname(os.path.realpath(__file__))
initial_default_file_path = dir_path + '/../playerInfo2018.csv'


def setup_logging():
    """
    Required for basic logging setup
    https://docs.python.org/3/howto/logging.html#logging-basic-tutorial
    """
    logging.basicConfig()
    logger = logging.getLogger(__name__)
    ic.configureOutput(includeContext=True, outputFunction=logger.info)
    logger.addHandler(logging.StreamHandler(sys.stdout))  # send logging to stdout
    return logger

logger = setup_logging()
df: pd.DataFrame = pd.read_csv(initial_default_file_path)


"""
Constants for Dash dropdown component
https://dash.plotly.com/dash-core-components/dropdown
"""
dropdown_label_key: str = 'label'
dropdown_value_key: str = 'value'


default_feature: str = 'points'


class MainApplication:
    """
    This is the main application. There are multiple pieces that are needed to draw the plots.
    The plotly library is based on html.

    App
    - Data(in dataframe form)
    - AppLayout
    - - Graph
    - - - Dropdown
    - - - Figure

    When this class is created with the given dataframe and default column the plots are initialized, but not yet displayed
    They become displayed when someone calls this objects `app.run_server` function
    """
    app: Dash
    df: pd.DataFrame
    dropdown_component: dcc.Dropdown
    dropdown_options: List[Dict[str, str]]
    dropdown_id: str = 'dropdown'
    hist_id: str = 'hist'

    def initialize(self, df: pd.DataFrame, default_col: str):
        self.df = df
        self.default_col = default_col
        self.setup_dropdown()
        self.setup_layout()

        # This is the trigger function that updates the graph on dropdown change
        @functools.lru_cache
        @self.app.callback(Output(component_id='hist', component_property='figure'), Input(component_id='dropdown', component_property='value'))
        def trigger_update_on_dropdown_change(dropdown_selection: str) -> plotly.graph_objs.Figure:
            ic(f'Updating output after receiving dropdown value: {dropdown_selection}')
            return self.create_histogram(col=dropdown_selection)

    def setup_layout(self) -> None:
        default_fig = px.histogram(df[self.default_col])
        self.app = Dash(__name__)
        self.app.layout = html.Div(children=[
            html.Div(children='''Survey Responses at'''),
            dcc.Graph(
                id='hist',
                figure=default_fig
            ),
            self.dropdown_component
        ])

    def setup_dropdown(self) -> None:
        """
        See: https://dash.plotly.com/dash-core-components/dropdown

        Setup dropdown options as list of dictionary like:
        [{'label': 'points', 'value': 'points'}}
        using list comprehension
        https://www.geeksforgeeks.org/python-list-comprehension/
        https://docs.python.org/3/library/functions.html?highlight=enumerate#enumerate

        """
        self.dropdown_options: List[Dict[str, str]] = [{dropdown_label_key: col, dropdown_value_key: col} for col in df.columns]
        self.dropdown_component = dcc.Dropdown(
            id=self.dropdown_id,
            value=self.default_col,
            options=self.dropdown_options,
            persistence=True
        )

    def create_histogram(self, col: str, percentile: int = 66):
        '''
        Create Histogram
        Currently not using percentile parameter
        Splits df into halfs and add traces
        '''
        # TODO: create variable size partitions
        column_data: pd.Series = self.df[col]
        hist_title = f'{col} Distribution'.replace('_', ' ').title()

        half_quantile = column_data.quantile(.5)
        first_half = df[df[col] < half_quantile][col]
        second_half = df[df[col] >= half_quantile][col]

        fig = go.Figure()
        fig.add_trace(go.Histogram(x=first_half))
        fig.add_trace(go.Histogram(x=second_half))

        fig.update_layout(barmode='stack')
        return fig

    # Constructor
    def __init__(self, df: pd.DataFrame, default_col: str) -> None:
        self.initialize(df, default_col)


# Unnecessary, but good practice. See stack overflow for why
if __name__ == '__main__':
    graph = MainApplication(df, default_feature)
    graph.app.run_server(debug=True, port=80)

