
import dash_core_components as dcc

import numpy as np

import plotly.graph_objs as go

def get_mapbox_access_token(folderpath='.', filename="mapbox.txt"):
    import os
    
    with open(os.path.join(folderpath, filename), 'r') as file:
        s = file.read()
    
    return s

def get_map(results, colors):

    # Récupération du token mapbox
    mapbox_access_token = get_mapbox_access_token()

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

    g = dcc.Graph(
        id='map',
        figure={
            'data': [data],
            'layout': layout
        }
    )

    return [g]
