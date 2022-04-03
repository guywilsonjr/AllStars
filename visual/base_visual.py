from abc import abstractmethod

from dash import dcc


class BaseVisual:
    '''
    Abstract base class for Visuals
    '''
    @property
    @abstractmethod
    def tab(self) -> dcc.Tab:
        pass

    @property
    @abstractmethod
    def tab_id(self) -> str:
        pass

    @property
    @abstractmethod
    def label(self) -> str:
        pass
