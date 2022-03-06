import pandas as pd
from dash import dcc, Dash, html
import plotly.express as px


df = pd.read_csv('playerInfo2018.csv')
app = Dash(__name__)
fig = px.histogram(df['field_goals'])
app.layout = html.Div(children=[

    html.Div(children='''
        Main Window.
    '''),

    dcc.Graph(
        figure=fig
    )
])

fig.show()

if __name__ == '__main__':
    exit()
    app.run_server(debug=True)

