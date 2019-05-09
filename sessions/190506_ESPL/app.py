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
        html.Div(
            id="row-remplissage",
            children=[
                html.H2(children="Taux de remplissage des colonnes"),
                dcc.Graph(id="graph-filled"),
            ],
            style={"display": "none"},
        ),
        html.Div(
            id="row-analyse",
            children=[
                html.H2(children="Analyse visuelle des colonnes"),
                dbc.CardDeck(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader("Colonnes de float"),
                                dbc.CardBody(
                                    [
                                        dcc.Dropdown(id="dropdown-float"),
                                        html.Div(id="div-float-info"),
                                    ]
                                ),
                            ]
                        ),
                        dbc.Card(
                            [
                                dbc.CardHeader("Colonnes de int"),
                                dbc.CardBody(
                                    [
                                        dcc.Dropdown(id="dropdown-int"),
                                        html.Div(id="div-int-info"),
                                    ]
                                ),
                            ]
                        ),
                        dbc.Card(
                            [
                                dbc.CardHeader("Colonnes de string"),
                                dbc.CardBody(
                                    [
                                        dcc.Dropdown(id="dropdown-str"),
                                        html.Div(id="div-str-info"),
                                    ]
                                ),
                            ]
                        ),
                    ]
                ),
            ],
            style={"display": "none"},
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

            print(dialect.delimiter)

            # Read file into pandas
            df = pd.read_csv(io.StringIO(decoded.decode("utf-8")),
                             delimiter=dialect.delimiter)
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

    st = df.isnull().mean()

    return {
        "data": [{"x": st.index, "y": st, "type": "bar"}],
        "layout": {
            "title": "Pourcentage de cellules vides par colonne",
            "yaxis": {"range": [0, 1]},
        },
    }


@app.callback(
    [Output("row-analyse", "style"), Output("row-remplissage", "style")],
    [Input("upload-data", "contents")],
    [State("upload-data", "filename"), State("upload-data", "last_modified")],
)
def display_rows(contents, filename, date):
    if contents is None:
        return {"display": "none"}, {"display": "none"}

    df = parse_contents(contents, filename, date)

    if type(df) != pd.DataFrame:
        raise PreventUpdate

    return {"display": "block"}, {"display": "block"}


# Float


@app.callback(
    Output("dropdown-float", "options"),
    [Input("upload-data", "contents")],
    [State("upload-data", "filename"), State("upload-data", "last_modified")],
)
def display_dropdown_float(contents, filename, date):
    if contents is None:
        return []

    df = parse_contents(contents, filename, date)

    if type(df) != pd.DataFrame:
        raise PreventUpdate

    df = df.select_dtypes(include=["float64"])

    return [{"label": col, "value": col} for col in df.columns]


@app.callback(
    Output("div-float-info", "children"),
    [Input("dropdown-float", "value")],
    [
        State("upload-data", "contents"),
        State("upload-data", "filename"),
        State("upload-data", "last_modified"),
    ],
)
def display_float_info(value, contents, filename, date):
    if value is None:
        return html.P("En attente de données")

    df = parse_contents(contents, filename, date)

    if type(df) != pd.DataFrame:
        raise PreventUpdate

    # return [
    #     html.P(f"Valeur min : {df[value].min()}"),
    #     html.P(f"Valeur max : {df[value].max()}"),
    # ]

    return dcc.Graph(
        figure={
            "data": [go.Histogram(x=df[value])],
            "layout": {
                "margin": {"l": 20, "r": 20, "b": 20, "t": 20},
                "xaxis": {"title": "valeurs", "automargin": True},
                "yaxis": {"title": "nombre d'occurences", "automargin": True},
            },
        }
    )


# Int


@app.callback(
    Output("dropdown-int", "options"),
    [Input("upload-data", "contents")],
    [State("upload-data", "filename"), State("upload-data", "last_modified")],
)
def display_dropdown_int(contents, filename, date):
    if contents is None:
        return []

    df = parse_contents(contents, filename, date)

    if type(df) != pd.DataFrame:
        raise PreventUpdate

    df = df.select_dtypes(include=["int64"])

    return [{"label": col, "value": col} for col in df.columns]


@app.callback(
    Output("div-int-info", "children"),
    [Input("dropdown-int", "value")],
    [
        State("upload-data", "contents"),
        State("upload-data", "filename"),
        State("upload-data", "last_modified"),
    ],
)
def display_int_info(value, contents, filename, date):
    if value is None:
        return html.P("En attente de données")

    df = parse_contents(contents, filename, date)

    if type(df) != pd.DataFrame:
        raise PreventUpdate

    return [
        html.P(f"Valeur min : {df[value].min()}"),
        html.P(f"Valeur max : {df[value].max()}"),
    ]


# String


@app.callback(
    Output("dropdown-str", "options"),
    [Input("upload-data", "contents")],
    [State("upload-data", "filename"), State("upload-data", "last_modified")],
)
def display_dropdown_str(contents, filename, date):
    if contents is None:
        return []

    df = parse_contents(contents, filename, date)

    if type(df) != pd.DataFrame:
        raise PreventUpdate

    df = df.select_dtypes(include=["object"])

    return [{"label": col, "value": col} for col in df.columns]


@app.callback(
    Output("div-str-info", "children"),
    [Input("dropdown-str", "value")],
    [
        State("upload-data", "contents"),
        State("upload-data", "filename"),
        State("upload-data", "last_modified"),
    ],
)
def display_str_info(value, contents, filename, date):
    if value is None:
        return html.P("En attente de données")

    df = parse_contents(contents, filename, date)

    if type(df) != pd.DataFrame:
        raise PreventUpdate

    st = df[value].value_counts().head(5)

    return [html.P(f"{idx} ({value} occurences)") for idx, value in st.iteritems()]


if __name__ == "__main__":
    app.run_server(debug=True)
