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
from db import Session, Trajet
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
    trajets = session.query(Trajet).all()

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
                    lat=[trajet.latitude for trajet in trajets],
                    lon=[trajet.longitude for trajet in trajets],
                    mode='markers',
                    marker=dict(
                        size=9
                    ),
                    text=[trajet.destination for trajet in trajets],
                )
                ],
                'layout': go.Layout(
                    autosize=True,
                    hovermode='closest',
                    mapbox=dict(
                        accesstoken=mapbox_access_token,
                        bearing=0,
                        center=dict(
                            lat=np.mean([trajet.latitude for trajet in trajets]),
                            lon=np.mean([trajet.longitude for trajet in trajets])
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
