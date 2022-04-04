import os
# Sys needed to do logging correctly. why do logging? https://stackoverflow.com/questions/6918493/in-python-why-use-logging-instead-of-print
import logging
import sys
# icream logging even better https://github.com/gruns/icecream
from typing import List, Final

from icecream import ic
import pandas as pd

# Use Plotly Dash for nice visuals
from dash import dcc, Dash, html, Input, Output
from data_tools import Dataset
# Get current directory
from .base_visual import BaseVisual
from .clustering import Clustering

from .histograms import Histograms


dir_path = os.path.dirname(os.path.realpath(__file__))
initial_default_file_path = f'{dir_path }/../playerInfo2018.csv'
default_feature: str = 'points'


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

    data_file_path: str
    dataset: Dataset
    default_feature: str
    clustering: Clustering
    histograms: Histograms
    app: Dash
    app_name: Final[str] = 'Dashboard'
    tabs: List[dcc.Tab] = []

    # Constructor
    def __init__(self, data_file_path: str, default_feature: str) -> None:
        self.data_file_path = data_file_path
        self.default_feature = default_feature
        self.setup()

    def setup(self):
        self.setup_app()
        self.setup_dataset()
        self.setup_tabs()
        self.setup_tab_switch_callback()
        self.setup_layout()

    def setup_app(self):
        self.default_feature = default_feature
        self.app = Dash(self.app_name, compress=False, serve_locally=True)
        self.app.enable_dev_tools(debug=True)

    def setup_dataset(self):
        self.dataset = Dataset(self.app, pd.read_csv(self.data_file_path))

    def setup_tabs(self):
        self.setup_histograms()
        self.setup_clustering()

    def setup_histograms(self):
        self.histograms = Histograms(app=self.app, dataset=self.dataset, default_feature=self.default_feature)
        self.histograms.setup()
        self.tabs.append(self.histograms.tab)

    def setup_clustering(self):
        self.clustering = Clustering(app=self.app, dataset=self.dataset)
        self.clustering.setup()
        self.tabs.append(self.clustering.tab)

    def setup_layout(self) -> None:
        self.app.layout = html.Div(
            children=[html.H1('Dashboard', style={'textAlign': 'center'}),
                html.Div(children=[
                    dcc.Tabs(
                        id="window",
                        children=self.tabs,
                        value=self.histograms.tab_id
                ),
            html.Div(id='tabs-content', children=[])])])

    def setup_tab_switch_callback(self):
        @self.app.callback(Output('window', 'value'),
                           Input(str(self.histograms.tab_id), 'value'))
        def render_content(tab):
            return tab.tab_id if tab else self.histograms.tab_id


graph = MainApplication(initial_default_file_path, default_feature)
server = graph.app.server

# Unnecessary, but good practice. See stack overflow for why
if __name__ == '__main__':
    graph.app.run_server(debug=True, port=8080)



