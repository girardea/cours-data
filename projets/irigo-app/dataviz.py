#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Eléments de visualisation (graphiques) appelés par app-irigo.py
"""
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

import datetime as dt

import json

import math

import numpy as np

import os

from flask import send_from_directory

import pandas as pd

import plotly.graph_objs as go

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from textwrap import dedent as d

# Modules internes
from db import Session, Trajet, Etape, Ligne, Vehicule

from datavizelements import get_map_figure, get_barh, get_tsplot


def generate_table(dataframe, max_rows=10):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])]
        +
        # Body
        [
            html.Tr([html.Td(dataframe.iloc[i][col]) for col in dataframe.columns])
            for i in range(min(len(dataframe), max_rows))
        ]
    )


def get_dash():
    # Instanciation du Dash
    external_stylesheets = ['/static/stylesheet.css']
    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
    app.config['suppress_callback_exceptions'] = True

    # Ouverture d'une session vers la DB
    session = Session()

    # Récupération des trajets
    lastUts = (
        session.query(Etape.record_timestamp)
        .order_by(Etape.record_timestamp.desc())
        .first()[0]
    )
    results = (
        session.query(
            Etape.ecart,
            Trajet.latitude,
            Trajet.longitude,
            Trajet.destination,
            Trajet.id_trajet,
            Trajet.id_ligne,
            Ligne.nom_ligne,
        )
        .select_from(Etape)
        .join(Trajet)
        .join(Ligne)
        .filter(Etape.record_timestamp == lastUts)
    )

    session.close()

    # Contenu de l'app
    app.layout = html.Div(
        className="container-fluid bg-white",
        children=[
            html.Div(
                className="row",
                children=[
                    html.Div(
                        className="col-sm-4",
                        children=[
                            html.H1(className="text-center text-black py-4", children="Irigo app"),
                            html.P(className="text-center text-black py-4", children="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."),
                        ],
                    ),
                    html.Div(className="col-sm-8", children=get_tsplot()),
                ],
            ),
            html.Div(
                className="row",
                children=[
                    html.Div(className="col-sm-4", children=[dcc.Graph(id="barh")]),
                    html.Div(className="col-sm-8", children=[dcc.Graph(id="map")]),
                ],
            ),
            # html.Div(
            #     className="row",
            #     children=[
            #         html.Div(
            #             className="col-sm-4",
            #             children=[
            #                 dcc.Dropdown(
            #                     id="select-ligne",
            #                     options=[
            #                         {
            #                             "label": trajet.nom_ligne,
            #                             "value": trajet.id_ligne,
            #                         }
            #                         for trajet in results
            #                     ],
            #                 ),
            #                 dcc.Markdown(
            #                     d(
            #                         """
            #     **Données par point**
            #
            #     Cliquez sur un point pour afficher les données relatives à celui-ci.
            # """
            #                     )
            #                 ),
            #                 html.Table(id="click-data"),
            #             ],
            #         ),
            #     ],
            # ),
            html.Footer(
                className="page-footer font-small fixed-bottom bg-grey-clear border-top-black py-3",
                children=html.Div(
                    className="text-center color-black",
                        children=[
                            "Outil développé par ",
                            html.A(
                                className="color-black",
                                href="http://www.crossdata.tech/",
                                children="Crossdata",
                            ),

                        ],
                ),
            ),
        ],
    )

    @app.callback(Output("barh", "figure"), [Input("tsplot", "clickData")])
    def plot_barh(hoverData):
        if not hoverData:
            return get_barh(lastUts)

        nb = len(hoverData["points"])
        if nb > 1:
            logging.warning("{} points hovered (should be 0 or 1).".format(nb))

        tt = dt.datetime.strptime(hoverData["points"][0]["x"], "%Y-%m-%d %H:%M")

        # bug des deux heures (lié à la timezone)
        tt -= dt.timedelta(hours=2)

        return get_barh(tt)

    # @app.callback(
    #     dash.dependencies.Output("click-data", "children"),
    #     [dash.dependencies.Input("map", "clickData")],
    # )
    # def display_click_data(clickData):
    #     # nom de ligne
    #     # numéro de ligne
    #     # prochain arrêt
    #     # retard
    #     # Ouverture d'une session vers la DB
    #     session = Session()
    #
    #     if clickData:
    #         query = (
    #             session.query(
    #                 Ligne.nom_ligne,
    #                 Ligne.num_ligne,
    #                 Vehicule.type_vehicule,
    #                 Vehicule.etat_vehicule,
    #             )
    #             .select_from(Trajet)
    #             .join(Ligne)
    #             .join(Vehicule)
    #             .filter(Trajet.id_trajet == clickData["points"][0]["customdata"])
    #         )
    #     else:
    #         query = (
    #             session.query(
    #                 Ligne.nom_ligne,
    #                 Ligne.num_ligne,
    #                 Vehicule.type_vehicule,
    #                 Vehicule.etat_vehicule,
    #             )
    #             .select_from(Trajet)
    #             .join(Ligne)
    #             .join(Vehicule)
    #         )
    #
    #     df = pd.read_sql_query(query.statement, query.session.bind)
    #
    #     session.close()
    #
    #     return generate_table(df)

    @app.callback(
        Output("map", "figure"),
        [Input("tsplot", "hoverData")],
    )
    def update_graph(hoverData):
        if not hoverData:
            return get_map_figure(lastUts)

        tt = dt.datetime.strptime(hoverData["points"][0]["x"], "%Y-%m-%d %H:%M")

        # bug des deux heures (lié à la timezone)
        tt -= dt.timedelta(hours=2)

        return get_map_figure(tt)

    # Bootstrap
    app.css.append_css(
        {
            "external_url": "https://maxcdn.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css"
        }
    )
    app.scripts.append_script(
        {
            "external_url": "https://maxcdn.bootstrapcdn.com/bootstrap/4.1.3/js/bootstrap.min.js"
        }
    )

    # Dash CSS
    app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})

    # Loading screen CSS
    app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/brPBPO.css"})

    return app


def run_dash(docker=False):
    app = get_dash()
    if docker:
        app.run_server(host="0.0.0.0", port=8383)
    else:
        app.run_server(debug=True)


# Démarrage de l'app
if __name__ == "__main__":
    run_dash()
