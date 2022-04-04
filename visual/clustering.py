from typing import Final
from pydantic import PrivateAttr, BaseModel
import plotly.figure_factory as ff
import plotly.graph_objs as go
from dash import dcc, Dash

from data_tools import Dataset
from base_visual import BaseVisual


clustering_id = 'clustering-_tab'
clustering_label = 'Clustering'


class Clustering(BaseModel, BaseVisual):
    class Config:
        arbitrary_types_allowed = True

    app: Dash
    dataset: Dataset


    _label: Final[str] = 'Clustering'
    _tab_id: Final[str] = 'clustering-tab'
    _fig: go.Figure = PrivateAttr()
    _graph = PrivateAttr()
    _graph_id: Final[str] = 'clustering'
    _tab: dcc.Tab = PrivateAttr()

    def setup(self):
        self.setup_tab()

    def setup_graph(self):
        dendrogram_data = self.dataset.taste()
        self._fig = ff.create_dendrogram(X=dendrogram_data)
        self._graph = dcc.Graph(
            id=self._graph_id,
            figure=self._fig
        )

    def setup_tab(self):
        self.setup_graph()
        self._tab = dcc.Tab(
            id=self._tab_id,
            label=self._label,
            children=[self._graph])
