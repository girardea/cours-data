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

from plotly.offline import init_notebook_mode, iplot
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Modules internes
from db import Session, Trajet, Etape
# from db import Arret, Vehicule, Ligne, Trajet, Etape

def get_mapbox_access_token(folderpath='.', filename="mapbox.txt"):
    import os
    
    with open(os.path.join(folderpath, filename), 'r') as file:
        s = file.read()
    
    return s

def get_dash():
    # Instanciation du Dash
    app = dash.Dash()

    # Ouverture d'une session vers la DB
    session = Session()

    # Récupération des trajets
    results = session.query(Etape.ecart, Trajet.latitude, Trajet.longitude, Trajet.destination).select_from(Etape).join(Trajet)
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
        html.H1('Irigo app'),
        dcc.Graph(
            id='map',
            figure={
                'data': [
                    go.Scattermapbox(
                    lat=[result.latitude for result in results],
                    lon=[result.longitude for result in results],
                    mode='markers',
                    marker=dict(
                        size=9,
                        color=colors
                    ),
                    text=[result.ecart for result in results],
                )
                ],
                'layout': go.Layout(
                    autosize=True,
                    hovermode='closest',
                    mapbox=dict(
                        accesstoken=mapbox_access_token,
                        bearing=0,
                        center=dict(
                            lat=np.mean([result.latitude for result in results]),
                            lon=np.mean([result.longitude for result in results])
                        ),
                        pitch=0,
                        zoom=10
                    ),
                )
            }
        )
    ], style={'text-align': 'center'})

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
