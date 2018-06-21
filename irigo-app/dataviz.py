#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Eléments de visualisation (graphiques) appelés par app-irigo.py
"""
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import math
import json

from flask import make_response
from textwrap import dedent as d
from plotly.offline import init_notebook_mode, iplot
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Modules internes
from db import Session, Trajet, Etape, Ligne, Vehicule

def get_mapbox_access_token(folderpath='.', filename="mapbox.txt"):
    import os
    
    with open(os.path.join(folderpath, filename), 'r') as file:
        s = file.read()
    
    return s

def generate_table(dataframe, max_rows=10):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )

def get_dash():
    # Instanciation du Dash
    app = dash.Dash()

    # Ouverture d'une session vers la DB
    session = Session()

    # Récupération des trajets
    lastUts = session.query(Etape.record_timestamp) \
                     .order_by(Etape.id_etape.desc()) \
                     .first()[0]
    results = session.query(Etape.ecart, Trajet.latitude, Trajet.longitude,
                            Trajet.destination, Trajet.id_trajet) \
                     .select_from(Etape).join(Trajet) \
                     .filter(Etape.record_timestamp == lastUts)

    colors = []

    for result in results:
        if result.ecart > 60:
            color = 'red'
 
        if result.ecart < -60:
            color = 'purple'
        
        if abs(result.ecart) <= 60:
            color = 'green'
            
        colors.append(color)

    # Récupération du token mapbox
    mapbox_access_token = get_mapbox_access_token()
        
    # Contenu de l'app
    app.layout = html.Div([
        html.H1('Irigo app', style={'text-align': 'center'}),
        html.Div([
            html.Div([
                dcc.Graph(
                    id='map',
                    figure={
                        'data': [
                            go.Scattermapbox(
                                lat=[trajet.latitude for trajet in results],
                                lon=[trajet.longitude for trajet in results],
                                mode='markers',
                                marker=dict(
                                    size=9,
                                    color=colors
                                ),
                                text=[trajet.destination for trajet in results],
                                customdata=[trajet.id_trajet for trajet in results]
                            )
                        ],
                        'layout': go.Layout(
                            height=700,
                            autosize=True,
                            hovermode='closest',
                            mapbox=dict(
                                accesstoken=mapbox_access_token,
                                bearing=0,
                                center=dict(
                                    lat=np.mean([trajet.latitude for trajet in results]),
                                    lon=np.mean([trajet.longitude for trajet in results])
                                ),
                                pitch=0,
                                zoom=11
                            ),
                        )
                    }
                )
            ], style={'width': '70%', 'float': 'left'}),
            html.Div([
                dcc.Markdown(d("""
                    **Graphique à ajouter**

                    Description du graphique
                """))
            ], style={'margin-top': '83px', 'float': 'right', 'width': '30%'})
        ]),
        html.Div([
            dcc.Markdown(d("""
                **Données par point**

                Cliquez sur un point pour afficher les données relatives à celui-ci.
            """)),
            html.Table(id='click-data')
        ], style={'display': 'inline-block', 'width': '100%', 'margin-left': '78px'})
    ])

    @app.callback(
        dash.dependencies.Output('click-data', 'children'),
        [dash.dependencies.Input('map', 'clickData')])
    def display_click_data(clickData):
        # nom de ligne
        # numéro de ligne
        # prochain arrêt
        # retard
        
        # Ouverture d'une session vers la DB
        session = Session()
        print(clickData['points'])
        query = session.query(Ligne.nom_ligne, Ligne.num_ligne, Vehicule.type_vehicule, Vehicule.etat_vehicule) \
                       .select_from(Trajet).join(Ligne).join(Vehicule) \
                       .filter(Trajet.id_trajet == clickData['points'][0]['customdata'])
        session.close()

        df = pd.read_sql_query(query.statement, query.session.bind)
        return generate_table(df)

    return app

def run_dash(docker=False):
    app = get_dash()
    if docker:
        app.run_server(host='0.0.0.0', port=8383)
    else:
        app.run_server(debug=True)

# Démarrage de l'app
if __name__== '__main__':
    run_dash()
