from typing import List, Dict, Final
import plotly
from icecream import ic
from pydantic import BaseModel, PrivateAttr
import pandas as pd
import plotly.graph_objects as go
from dash import dcc, Dash, Output, Input

from data_tools import Dataset


class Histograms(BaseModel):
    class Config:
        arbitrary_types_allowed = True
    app: Dash
    dataset: Dataset
    default_feature: str
    _dropdown_options: List[Dict[str, str]] = PrivateAttr()
    _selected_dropdown: List[Dict[str, str]] = PrivateAttr()
    _dropdown_component: dcc.Dropdown = PrivateAttr()
    _fig: go.Figure = PrivateAttr()
    _graph = PrivateAttr()
    _tab: dcc.Tab = PrivateAttr()


    '''
    ex) Dash dropdown component https://dash.plotly.com/dash-core-components/dropdown
    Graphing Constants 
    '''

    _label: Final[str] = 'Histograms'
    _tab_id: Final[str] = 'histograms'
    _graph_id: Final[str] = 'histogram'
    _dropdown_id: Final[str] = 'dropdown'
    _dropdown_label_key: Final[str] = 'label'
    _dropdown_value_key: Final[str] = 'value'
    _graph_update_prop: Final[str] = 'figure'

    @property
    def tab(self):
        return self._tab

    @property
    def tab_id(self):
        return self._tab_id

    @property
    def label(self):
        return self._label

    def setup(self) -> None:
        self._setup_dropdown()
        self.setup_graph()
        self.setup_data_load_on_dropdown_selection()
        self.setup_tab()

    def setup_graph(self) -> None:
        default_fig = self.create_histogram(self.default_feature)
        self._graph = dcc.Graph(
            id=self._graph_id,
            figure=default_fig),

    def create_histogram(self, col: str, percentile: int = 50) -> go.Figure:
        '''
        Create Histogram
        Currently not using percentile parameter
        Splits dataset into halfs and add traces
        '''
        # TODO: create variable size partitions
        column_data: pd.Series = self.dataset.get_df_by_feature(col)
        hist_title = f'{col}'.replace('_', ' ').title()

        half_quantile = column_data.quantile(.5)
        first_half = self.dataset.df[column_data < half_quantile][col]
        second_half = self.dataset.df[column_data >= half_quantile][col]


        fig = go.Figure()
        fig.add_trace(go.Histogram(x=first_half, name='Bottom 50%'))
        fig.add_trace(go.Histogram(x=second_half, name='Top 50%'))

        fig.update_layout(barmode='stack', title=hist_title, title_x=0.5, legend=dict())
        self._fig = fig
        return self._fig

    def _setup_dropdown(self) -> None:
        """
        See: https://dash.plotly.com/dash-core-components/dropdown

        Setup dropdown options as list of dictionary like ex):
        [{'label': 'points', 'value': 'points'}}
        using list comprehension
        https://www.geeksforgeeks.org/python-list-comprehension/
        https://docs.python.org/3/library/functions.html?highlight=enumerate#enumerate

        """
        self._dropdown_options: List[Dict[str, str]] = [{self._dropdown_label_key: col, self._dropdown_value_key: col} for col in self.dataset.columns]
        self._dropdown_component = dcc.Dropdown(
            id=self._dropdown_id,
            value=self.default_feature,
            options=self._dropdown_options,
            persistence=True
        )

    def setup_data_load_on_dropdown_selection(self) -> None:
        # This is the trigger function that updates the graph on dropdown change
        @self.app.callback(Output(component_id=self._graph_id, component_property=self._graph_update_prop),
                           Input(component_id=self._dropdown_id, component_property=self._dropdown_value_key))
        def trigger_update_on_dropdown_change(dropdown_selection: str) -> plotly.graph_objs.Figure:
            self._selected_dropdown = dropdown_selection

            ic(f'Updating output after receiving dropdown value: {self._selected_dropdown}')
            return self.create_histogram(self._selected_dropdown)

    def setup_tab(self) -> None:
        """
        The Tab object encapsulates the histogram and dropdown into one portable component
        """
        self._tab = dcc.Tab(
            id=self._tab_id,
            label=self._label,
            children=[dcc.Graph(id='histogram'),
            self._dropdown_component])

