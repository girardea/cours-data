import dash_core_components as dcc

import datetime as dt

import numpy as np

import pandas as pd

import plotly.graph_objs as go

from sqlalchemy import desc, func

# import internes
from db import Etape, Ligne, Trajet, Vehicule, Session


def closest_time(lastUts):
    """ Returns time that exists in DB and that is closest to lastUts
    """
    session = Session()

    lowUts = (
        session.query(Etape.record_timestamp)
        .filter(Etape.record_timestamp <= lastUts)
        .order_by(desc(Etape.record_timestamp))
        .first()[0]
    )

    highUts = (
        session.query(Etape.record_timestamp)
        .filter(Etape.record_timestamp >= lastUts)
        .order_by(Etape.record_timestamp)
        .first()[0]
    )
    session.close()

    if highUts - lastUts > lastUts - lowUts:
        closeUts = lowUts
    else:
        closeUts = highUts

    return closeUts


def get_mapbox_access_token(folderpath=".", filename="mapbox.txt"):
    import os

    with open(os.path.join(folderpath, filename), "r") as file:
        s = file.read()

    return s


def get_map_figure(lastUts, line=None):
    """
    Get closest time
    """
    closeUts = closest_time(lastUts)

    print(lastUts, closeUts)

    """
    Get data
    """
    session = Session()

    results = (
        session.query(
            Etape.ecart,
            Trajet.latitude,
            Trajet.longitude,
            Trajet.destination,
            Trajet.id_trajet,
            Trajet.id_ligne,
            Ligne.nom_ligne,
            Vehicule.type_vehicule
        )
        .select_from(Etape)
        .join(Trajet)
        .join(Ligne)
        .join(Vehicule)
        .filter(Etape.record_timestamp == closeUts)
    )

    if line:
        results = results.filter(Trajet.id_ligne == line)

    session.close()

    # Récupération du token mapbox
    mapbox_access_token = get_mapbox_access_token()

    lats = [trajet.latitude for trajet in results]

    data = go.Scattermapbox(
        lat=[trajet.latitude for trajet in results],
        lon=[trajet.longitude for trajet in results],
        mode="markers",
        marker=dict(size=9, color=get_colors(results)),
        text=[trajet.destination for trajet in results],
        customdata=[trajet.id_trajet for trajet in results],
    )

    vehicules = [vehicule.type_vehicule for vehicule in results]

    total_bus = 0
    total_tram = 0

    for vehicule in vehicules:
        if vehicule=='CITADIS':
            total_tram += 1
        elif vehicule!='CITADIS':
            total_bus += 1

    layout = go.Layout(
        title=f"Il y a <b>{total_bus}</b> bus et <b>{total_tram}</b> tram en circulation",
        height=600,
        autosize=True,
        hovermode="closest",
        mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=dict(
                lat=np.mean([trajet.latitude for trajet in results]),
                lon=np.mean([trajet.longitude for trajet in results]),
            ),
            pitch=0,
            zoom=11,
        ),
    )

    return {"data": [data], "layout": layout}


def get_barh(lastUts):
    """
    Get closest date
    """
    closeUts = closest_time(lastUts)

    """
    Get data
    """
    session = Session()

    query = (
        session.query(Etape.ecart, Ligne.nom_ligne)
        .select_from(Etape)
        .join(Trajet)
        .join(Ligne)
        .filter(Etape.record_timestamp == closeUts)
    )

    df = pd.read_sql_query(query.statement, query.session.bind)

    session.close()

    dft = df.pivot_table(
        index="nom_ligne", values="ecart", aggfunc=lambda x: np.mean(np.abs(x))
    ).sort_values(by="ecart")

    xmax = (dft["ecart"] / 60).max()

    data = go.Bar(
        y=dft.index,
        x=dft["ecart"] / 60,
        orientation="h",
        marker={"color":dft["ecart"] / 60,
                'colorscale':'RdBu'},
    )

    layout = go.Layout(
        title="<b>Qualité du service ligne par ligne</b> <i>{}</i>".format(
            (closeUts + dt.timedelta(hours=2)).strftime("%A %d/%m/%Y à %H:%M")
        ),
        xaxis=dict(title="écart absolu moyen (minutes)", range=[0, max(10, xmax)]),
        yaxis=dict(title="ligne"),
        margin={"l": 300},
        showlegend=True,
    )

    figure = {"data": [data], "layout": layout}

    return figure


def get_tsplot():
    session = Session()

    query = (
        session.query(
            func.avg(func.abs(Etape.ecart)).label("ecart"), Etape.record_timestamp
        )
        .group_by(Etape.record_timestamp)
        .order_by(desc(Etape.record_timestamp))
    )

    df = pd.read_sql_query(query.statement, query.session.bind)

    session.close()

    df.set_index("record_timestamp", inplace=True)
    df.index = df.index.shift(2, freq="H")

    df = df.resample("15T").mean() / 60

    data = go.Scatter(
        x=df.index,
        y=df["ecart"],
        mode='lines+markers',
        opacity=0.7,
        marker={
            'size': 15,
            'line': {'width': 0.5, 'color': '#0a3859'},
            'color': df["ecart"],
            'colorscale': 'RdBu'
        },
    )

    layout = go.Layout(
        title="<b>Qualité du service ces dernières heures sur l'ensemble du réseau</b>",
        xaxis={"title": "heure de la journée"},
        yaxis={"title": "écart absolu moyen (minutes)"},
        hovermode="closest",
        plot_bgcolor="#fff",
        paper_bgcolor="#fff",
        autosize=True,
        height=300,
        showlegend=True,
    )

    g = dcc.Graph(id="tsplot", figure={"data": [data], "layout": layout})

    return [g]


def get_colors(results):
    colors = []

    for result in results:
        if result.ecart > 3 * 60:
            color = "red"
        elif result.ecart < -3 * 60:
            color = "purple"
        else:
            color = "green"

        colors.append(color)

    return colors
