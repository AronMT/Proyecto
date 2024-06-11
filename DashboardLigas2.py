import pandas as pd
import plotly.express as px
import mysql.connector
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table, callback, Input, Output


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


combined_df = pd.concat([laliga_df, seriea_df, premier_df])

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Análisis Comparativo de Ligas de Fútbol", className='text-center mb-4'), width=12)
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
            dcc.Graph(id='scatter-plot-ligas')
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='histogram-pts-ligas')
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='boxplot-pts-ligas')
        ], width=12)
    ])
])

@app.callback(
    Output('datatable-ligas', 'data'),
    [Input('league-dropdown', 'value')]
)
def update_table(selected_leagues):
    filtered_df = combined_df[combined_df['Liga'].isin(selected_leagues)]
    return filtered_df.to_dict('records')

@app.callback(
    Output('scatter-plot-ligas', 'figure'),
    [Input('league-dropdown', 'value')]
)
def update_scatter_plot(selected_leagues):
    filtered_df = combined_df[combined_df['Liga'].isin(selected_leagues)]

    fig = px.scatter(filtered_df, x='GF', y='GC', color='Liga', symbol='Equipo',
                     title='Goles a Favor vs Goles en Contra por Equipo')
    return fig

@app.callback(
    Output('histogram-pts-ligas', 'figure'),
    [Input('league-dropdown', 'value')]
)
def update_histogram(selected_leagues):
    filtered_df = combined_df[combined_df['Liga'].isin(selected_leagues)]

    fig = px.histogram(filtered_df, x='PTS', color='Liga', barmode='overlay',
                       title='Distribución de Puntos por Liga')
    return fig

@app.callback(
    Output('boxplot-pts-ligas', 'figure'),
    [Input('league-dropdown', 'value')]
)
def update_boxplot(selected_leagues):
    filtered_df = combined_df[combined_df['Liga'].isin(selected_leagues)]

    fig = px.box(filtered_df, x='Liga', y='PTS', color='Liga',
                 title='Variabilidad de Puntos por Equipo en cada Liga')
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
