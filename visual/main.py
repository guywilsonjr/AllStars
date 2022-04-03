import os
# Sys needed to do logging correctly. why do logging? https://stackoverflow.com/questions/6918493/in-python-why-use-logging-instead-of-print
import logging
import sys
# icream logging even better https://github.com/gruns/icecream
from icecream import ic
import pandas as pd

# Use Plotly Dash for nice visuals
from dash import dcc, Dash, html, Input, Output
from data_tools import Dataset
# Get current directory

from visual.distributions import Distributions


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

    distributions: Distributions = None
    app: Dash = None

    # Constructor
    def __init__(self, data_file_path: str, default_feature: str) -> None:
        self.data_file_path = data_file_path
        self.default_feature = default_feature
        self.setup()

    def setup(self):
        self.setup_app()
        self.setup_dataset()
        self.setup_distributions()
        self.setup_layout()
        self.setup_tab_switch_callback()

    def setup_app(self):
        self.default_feature = default_feature
        self.app = Dash(__name__, serve_locally=True)
        self.app.enable_dev_tools(debug=True)

    def setup_dataset(self):
        self.dataset = Dataset(self.app, pd.read_csv(self.data_file_path))

    def setup_distributions(self):
        self.distributions = Distributions(app=self.app, dataset=self.dataset, default_feature=self.default_feature)
        self.distributions.setup()

    def setup_layout(self) -> None:
        self.app.layout = html.Div(
            children=[
                html.Div(children=[
                    dcc.Tabs(
                        id="window",
                        children=[self.distributions.tab],
                ),
            html.Div(id='tabs-content', children=[])])])

    def setup_tab_switch_callback(self):
        @self.app.callback(Output('window', 'children'),
                           Input('distributions', 'value'))
        def render_content(tab):
            if tab:
                orderd_html_elements = [html.H1(self.distributions.label, style={'text-align': 'center'})] + tab.children
            else:
                orderd_html_elements = [html.H1(self.distributions.label, style={'text-align': 'center'})] + self.distributions.tab.children
            return html.Div(orderd_html_elements)


graph = MainApplication(initial_default_file_path, default_feature)

# Unnecessary, but good practice. See stack overflow for why
if __name__ == '__main__':
    graph.app.run_server(debug=True, port=8080)
else:
    server = graph.app.server


