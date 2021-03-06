
import dash_core_components as dcc

import numpy as np

import pandas as pd

import plotly.graph_objs as go

# import internes
from db import Etape, Ligne, Trajet, Session

def get_mapbox_access_token(folderpath='.', filename="mapbox.txt"):
    import os
    
    with open(os.path.join(folderpath, filename), 'r') as file:
        s = file.read()
    
    return s

def get_map_figure(results, colors):

    # Récupération du token mapbox
    mapbox_access_token = get_mapbox_access_token()

    lats = [trajet.latitude for trajet in results]
    print(len(lats))
    print(lats[:5])
    data = go.Scattermapbox(
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

    layout = go.Layout(
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

    return {'data': [data], 'layout': layout}

def get_barh(lastUts):

    session = Session()
    
    query = session.query(Etape.ecart, Ligne.nom_ligne) \
                   .select_from(Etape).join(Trajet).join(Ligne) \
                   .filter(Etape.record_timestamp == lastUts)

    df = pd.read_sql_query(query.statement, query.session.bind)

    session.close()

    dft = df.pivot_table(index="nom_ligne", values="ecart",
                         aggfunc=lambda x: np.mean(np.abs(x))) \
            .sort_values(by="ecart")

    data = go.Bar(
        y=dft.index,
        x=dft['ecart'],
        orientation='h',
        marker={
            'color': 'rgba(210, 105, 30, 0.5)'
        }
    )

    layout = go.Layout(
        title="Ecarts absolus moyens sur les lignes du réseau Irigo",
        xaxis={
            'title': "écart moyen absolu (secondes)",
        },
        yaxis={
            'title': "ligne"
        },
        margin={
            'l': 300
        }
    )

    g = dcc.Graph(
        id='barh',
        figure={
            'data': [data],
            'layout': layout
        }
    )

    return [g]

def get_colors(results):
    colors = []

    for result in results:
        if result.ecart > 60:
            color = 'red'

        if result.ecart < -60:
            color = 'purple'

        if abs(result.ecart) <= 60:
            color = 'green'

        colors.append(color)

    return colors
