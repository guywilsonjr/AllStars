import pandas as pd
import plotly as plotly
from dash import dcc, Dash, html, Input, Output
import plotly.express as px


df = pd.read_csv('playerInfo2018.csv')
app = Dash(__name__)


fig = px.histogram(df['field_goals'])

dropdown_label_key: str = 'label'
dropdown_value_key: str = 'value'

class DCCGraph:
    app: Dash
    fig: plotly.graph_objs.Figure
    df: pd.DataFrame

    def __init__(self, app, fig, df):
        self.app = app
        self.fig = fig
        self.df = df
        self.rev = {i: col for i, col in enumerate(df.columns)}
        app.layout = html.Div(children=[
            html.Div(children='''
                Main Window.
            '''),
            dcc.Graph(id='hist',
                figure=fig

            ),
            dcc.Dropdown(
                [{dropdown_label_key: col, dropdown_value_key: i} for i, col in enumerate(df.columns)],
                id='slider'
            )
        ])
        #fig.show()
        @app.callback(
            Output(component_id='hist', component_property='figure'),
            Input(component_id='slider', component_property='value')
        )
        def update_output_div(input_value):
            print(f'Got: {input_value}')
            col = self.rev[input_value]
            print(f'Using: {col}')
            return px.histogram(df[col])


if __name__ == '__main__':
    g.app.run_server(debug=True)

