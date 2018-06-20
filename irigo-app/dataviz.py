#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Eléments de visualisation (graphiques) appelés par app-irigo.py
"""
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
import math

from plotly.offline import init_notebook_mode, iplot
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# from db import Arret, Vehicule, Ligne, Trajet, Etape

def get_mapbox_access_token(folderpath='.', filename="mapbox.txt"):
    import os
    
    with open(os.path.join(folderpath, filename), 'r') as file:
        s = file.read()
    
    return s


def midpoint(lat1, lon1, lat2, lon2):
#Input values as degrees

#Convert to radians
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)


    bx = math.cos(lat2) * math.cos(lon2 - lon1)
    by = math.cos(lat2) * math.sin(lon2 - lon1)
    lat3 = math.atan2(math.sin(lat1) + math.sin(lat2), \
            math.sqrt((math.cos(lat1) + bx) * (math.cos(lat1) \
            + bx) + by**2))
    lon3 = lon1 + math.atan2(by, math.cos(lat1) + bx)

    return[round(math.degrees(lat3), 2), round(math.degrees(lon3), 2)]

def get_dash():
    # Instanciation du Dash
    app = dash.Dash()

    # Récupération de la db
    engine = create_engine('sqlite:///database.db')

    # Stockage de la db dans la RAM
    Session = sessionmaker(bind=engine)
    session = Session()

    # Récupération des trajets
    # session.query(Trajet).all()

    # Récupération du token mapbox
    mapbox_access_token = get_mapbox_access_token()

    # Contenu de l'app
    app.layout = html.Div([
        html.H1('Irigo app'),
        dcc.Graph(
            id='life-exp-vs-gdp',
            figure={
                'data': [
                    go.Scattermapbox(
                    lat=['47.51151'],
                    lon=['-0.59615'],
                    mode='markers',
                    marker=dict(
                        size=9
                    ),
                    text=["test"],
                )
                ],
                'layout': go.Layout(
                    autosize=True,
                    hovermode='closest',
                    mapbox=dict(
                        accesstoken=mapbox_access_token,
                        bearing=0,
                        center=dict(
                            lat=47.51151,
                            lon=-0.59615
                        ),
                        pitch=0,
                        zoom=10
                    ),
                )
            }
        )
    ], style={'text-align': 'center'})

    return app

def run_dash():
    app = get_dash()
    #app.run_server(debug=True) on localhost
    app.run_server(host='0.0.0.0', port=8383)
    fig = dict(data=data, layout=layout)
    iplot(fig, filename='Multiple Mapbox')

# Démarrage de l'app
if __name__== '__main__':
    app = get_dash()
    #app.run_server(debug=True) on localhost
    app.run_server(host='0.0.0.0', port=8383)
    fig = dict(data=data, layout=layout)
    iplot(fig, filename='Multiple Mapbox')
