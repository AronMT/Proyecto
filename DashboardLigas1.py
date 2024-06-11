import pandas as pd
import plotly.express as px
import mysql.connector
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table, callback, Input, Output


# Conexión a la base de datos MySQL
def get_data(liga):
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='12345',
        database='ligas',
        auth_plugin='mysql_native_password'
    )
    query = f'''
    SELECT Equipo.nombre AS Equipo, Temporada.Temporada, JJ, JG, JE, JP, GF, GC, DF, PTS, Liga.nombre AS Liga
    FROM Equipo_Temporada 
    JOIN Equipo ON Equipo_Temporada.idEquipo = Equipo.idEquipo
    JOIN Temporada ON Equipo_Temporada.idTemporada = Temporada.idTemporada
    JOIN Liga ON Equipo.idLiga = Liga.idLiga
    WHERE Liga.nombre = '{liga}'
    '''
    df = pd.read_sql(query, connection)
    connection.close()
    return df

laliga_df = get_data('La Liga')
seriea_df = get_data('Serie A')
premier_df = get_data('Premier League')

# Combinar los datos en un solo DataFrame
combined_df = pd.concat([laliga_df, seriea_df, premier_df])

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Comparación de Ligas de Fútbol", className='text-center mb-4'), width=12)
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id='league-dropdown',
                options=[
                    {'label': 'La Liga', 'value': 'La Liga'},
                    {'label': 'Serie A', 'value': 'Serie A'},
                    {'label': 'Premier League', 'value': 'Premier League'}
                ],
                multi=True,
                placeholder="Select leagues",
                value=['La Liga', 'Serie A', 'Premier League']
            )
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col([
            dash_table.DataTable(
                id='datatable-ligas',
                columns=[{"name": i, "id": i} for i in combined_df.columns],
                data=combined_df.to_dict('records'),
                page_size=10,
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'left'},
                style_header={'backgroundColor': 'rgb(30, 30, 30)', 'color': 'white'},
                style_data={'backgroundColor': 'rgb(50, 50, 50)', 'color': 'white'}
            )
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='bar-chart-ligas')
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id='team-dropdown',
                multi=True,
                placeholder="Select teams"
            )
        ], width=6),
        dbc.Col([
            dcc.Dropdown(
                id='season-dropdown',
                multi=True,
                placeholder="Select seasons"
            )
        ], width=6)
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='line-chart-ligas')
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='pie-chart-gf-ligas')
        ], width=12)
    ])
])

@app.callback(
    Output('team-dropdown', 'options'),
    [Input('league-dropdown', 'value')]
)
def update_team_dropdown(selected_leagues):
    filtered_df = combined_df[combined_df['Liga'].isin(selected_leagues)]
    teams = filtered_df['Equipo'].unique()
    return [{'label': team, 'value': team} for team in teams]

@app.callback(
    Output('season-dropdown', 'options'),
    [Input('league-dropdown', 'value')]
)
def update_season_dropdown(selected_leagues):
    filtered_df = combined_df[combined_df['Liga'].isin(selected_leagues)]
    seasons = filtered_df['Temporada'].unique()
    return [{'label': season, 'value': season} for season in seasons]

@app.callback(
    Output('datatable-ligas', 'data'),
    [Input('league-dropdown', 'value')]
)
def update_table(selected_leagues):
    filtered_df = combined_df[combined_df['Liga'].isin(selected_leagues)]
    return filtered_df.to_dict('records')

@app.callback(
    Output('bar-chart-ligas', 'figure'),
    [Input('league-dropdown', 'value'),
     Input('team-dropdown', 'value'),
     Input('season-dropdown', 'value')]
)
def update_bar_chart(selected_leagues, selected_teams, selected_seasons):
    filtered_df = combined_df[combined_df['Liga'].isin(selected_leagues)]
    if selected_teams:
        filtered_df = filtered_df[filtered_df['Equipo'].isin(selected_teams)]
    if selected_seasons:
        filtered_df = filtered_df[filtered_df['Temporada'].isin(selected_seasons)]

    fig = px.bar(filtered_df, x='Equipo', y='PTS', color='Liga', barmode='group',
                 title='Puntos por Equipo en Ligas Seleccionadas')
    return fig

@app.callback(
    Output('line-chart-ligas', 'figure'),
    [Input('league-dropdown', 'value'),
     Input('team-dropdown', 'value'),
     Input('season-dropdown', 'value')]
)
def update_line_chart(selected_leagues, selected_teams, selected_seasons):
    filtered_df = combined_df[combined_df['Liga'].isin(selected_leagues)]
    if selected_teams:
        filtered_df = filtered_df[filtered_df['Equipo'].isin(selected_teams)]
    if selected_seasons:
        filtered_df = filtered_df[filtered_df['Temporada'].isin(selected_seasons)]

    fig = px.line(filtered_df, x='Temporada', y='PTS', color='Equipo',
                  title='Evolución de Puntos por Temporada en Ligas Seleccionadas')
    return fig


@app.callback(
    Output('pie-chart-gf-ligas', 'figure'),
    [Input('league-dropdown', 'value'),
     Input('team-dropdown', 'value'),
     Input('season-dropdown', 'value')]
)
def update_pie_chart(selected_leagues, selected_teams, selected_seasons):
    filtered_df = combined_df[combined_df['Liga'].isin(selected_leagues)]
    if selected_teams:
        filtered_df = filtered_df[filtered_df['Equipo'].isin(selected_teams)]
    if selected_seasons:
        filtered_df = filtered_df[filtered_df['Temporada'].isin(selected_seasons)]

    fig = px.pie(filtered_df, values='GF', names='Equipo',
                 title='Distribución de Goles a Favor (GF) por Equipo en Ligas Seleccionadas')
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
