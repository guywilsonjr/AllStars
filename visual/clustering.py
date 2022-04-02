from dataclasses import dataclass
import pandas as pd
from dash import Dash, dcc, html
from dash.dependencies import Input, Output

from visual.tabs import DashTab

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


clustering_id = 'clustering-tab'
clustering_label = 'Clustering'

@dataclass
class ClusteringTab(DashTab):
    data: pd.DataFrame

clustering_tab = ClusteringTab(id=clustering_id, label=clustering_label, data=None)

