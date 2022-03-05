from sportsipy.nba.boxscore import Boxscore
from dash import dcc, Dash, html
import plotly.express as px

game_data = Boxscore('201806080CLE')

df = game_data.dataframe
print(df.columns)
app = Dash(__name__)
fig = px.bar(df, x="home_three_point_field_goal_attempts", y="home_points", color="winning_name", barmode="group")
app.layout = html.Div(children=[

    html.Div(children='''
        Main Window.
    '''),

    dcc.Graph(
        figure=fig
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)

