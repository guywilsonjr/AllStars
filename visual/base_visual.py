from abc import abstractmethod
from pydantic import PrivateAttr
import plotly.graph_objects as go
from dash import dcc


class BaseVisual:

    _fig: go.Figure = PrivateAttr()
    _graph = PrivateAttr()
    _tab: dcc.Tab = PrivateAttr()
    _tab_id: str
    _label: str
    '''
    Abstract base class for Visuals
    '''

    @property
    def tab(self) -> dcc.Tab:
        return self._tab

    @property
    def tab_id(self) -> str:
        return self._tab_id

    @property
    def label(self) -> str:
        return self._label

    @abstractmethod
    def setup(self) -> str:
        raise NotImplementedError
