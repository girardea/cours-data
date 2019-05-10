# -*- coding: utf-8 -*-
import base64

import csv

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

import dash_bootstrap_components as dbc

import io

import numpy as np

import pandas as pd

import plotly.graph_objs as go

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css", dbc.themes.FLATLY]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

navbar = dbc.NavbarSimple(
    brand="Analyse de tables de données", brand_href="#", sticky="top"
)

body = dbc.Container(
    [
        dcc.Upload(
            id="upload-data",
            children=html.Div(["Drag and Drop or ", html.A("Select Files")]),
            style={
                "width": "100%",
                "height": "60px",
                "lineHeight": "60px",
                "borderWidth": "1px",
                "borderStyle": "dashed",
                "borderRadius": "5px",
                "textAlign": "center",
                "margin": "10px",
            },
            # Don't allow multiple files to be uploaded
            multiple=False,
        ),
        html.Div(id="div-alerts"),
        dbc.Row(
            [
                dbc.Col(
                    id="row-remplissage", children=dcc.Graph(id="graph-filled"), width=6
                ),
                dbc.Col(
                    dbc.Card(
                        id="card-info",
                        children=[
                            dbc.CardHeader(id="card-header"),
                            dbc.CardBody(id="card-body"),
                        ],
                    ),
                    width=6,
                ),
            ]
        ),
    ]
)

app.layout = html.Div([navbar, body])


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(",")

    decoded = base64.b64decode(content_string)
    try:
        if filename.endswith(".csv"):
            # Assume that the user uploaded a CSV file

            # Guess delimiter
            with io.StringIO(decoded.decode("utf-8")) as file:
                dialect = csv.Sniffer().sniff(file.read())

            # Read file into pandas
            df = pd.read_csv(
                io.StringIO(decoded.decode("utf-8")), delimiter=dialect.delimiter
            )
        elif filename.endswith(".xlsx") or filename.endswith(".xls"):
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
        else:
            ext = filename.split(".")[-1]
            return dbc.Alert(f"Le format {ext} n'est pas supporté", color="danger")

    except Exception as e:
        print(e)
        return dbc.Alert("Je n'ai pas réussi à ouvrir ce fichier.", color="danger")

    return df


@app.callback(
    Output("div-alerts", "children"),
    [Input("upload-data", "contents")],
    [State("upload-data", "filename"), State("upload-data", "last_modified")],
)
def display_alerts(contents, filename, date):
    if contents is None:
        return

    df = parse_contents(contents, filename, date)

    if type(df) != pd.DataFrame:
        return df

    return


@app.callback(
    Output("graph-filled", "figure"),
    [Input("upload-data", "contents")],
    [State("upload-data", "filename"), State("upload-data", "last_modified")],
)
def display_graph(contents, filename, date):
    if contents is None:
        return {}

    df = parse_contents(contents, filename, date)

    if type(df) != pd.DataFrame:
        raise PreventUpdate

    st = df.notnull().mean()

    return {
        "data": [{"x": st, "y": st.index, "type": "bar", "orientation": "h"}],
        "layout": {
            "title": f"Colonnes du fichier {filename}",
            "xaxis": {
                "range": [0, 1],
                "title": "taux de remplissage",
                "automargin": True,
                "tickformat": ".0%",
            },
            "yaxis": {"automargin": True, "dtick": 1},
            "margin": {"l": 20, "r": 20, "b": 20, "t": 40},
        },
    }


@app.callback(
    [Output("card-header", "children"), Output("card-body", "children")],
    [Input("graph-filled", "clickData")],
    [
        State("upload-data", "contents"),
        State("upload-data", "filename"),
        State("upload-data", "last_modified"),
    ],
)
def display_float_info(click, contents, filename, date):
    if click is None:
        return "Informations détaillées", html.P("En attente de données")

    column = click["points"][0]["y"]

    df = parse_contents(contents, filename, date)

    if type(df) != pd.DataFrame:
        raise PreventUpdate

    title = f"Colonne {column}"

    ctype = df[column].dtype

    if ctype in ["float64", "int64"]:
        content = dcc.Graph(
            figure={
                "data": [go.Histogram(x=df[column])],
                "layout": {
                    "margin": {"l": 20, "r": 20, "b": 20, "t": 20},
                    "xaxis": {"title": "valeurs", "automargin": True},
                    "yaxis": {"title": "nombre d'occurences", "automargin": True},
                },
            }
        )
    else:
        content = f"Type : {ctype}"

    return title, content


if __name__ == "__main__":
    app.run_server(debug=True)
