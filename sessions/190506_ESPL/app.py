# -*- coding: utf-8 -*-
import base64
import io

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import numpy as np

import pandas as pd

import plotly.graph_objs as go

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(
    children=[
        html.H1(children="Analyse de fichiers CSV"),
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
        html.H2(children="Taux de remplissage des colonnes"),
        dcc.Graph(id="graph-filled"),
        html.H2(children="Analyse visuelle des colonnes"),
        html.H3(children="Colonnes de float"),
        dcc.Dropdown(id="dropdown-float"),
        html.Div(id="div-float-info"),
    ]
)


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(",")

    decoded = base64.b64decode(content_string)
    try:
        if "csv" in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
        elif "xls" in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div(["There was an error processing this file."])

    return df


@app.callback(
    Output("graph-filled", "figure"),
    [Input("upload-data", "contents")],
    [State("upload-data", "filename"), State("upload-data", "last_modified")],
)
def display_graph(contents, filename, date):
    if contents is None:
        return {}

    df = parse_contents(contents, filename, date)
    st = df.isnull().mean()

    return {
        "data": [{"x": st.index, "y": st, "type": "bar"}],
        "layout": {
            "title": "Pourcentage de cellules vides par colonne",
            "yaxis": {"range": [0, 1]},
        },
    }


@app.callback(
    Output("dropdown-float", "options"),
    [Input("upload-data", "contents")],
    [State("upload-data", "filename"), State("upload-data", "last_modified")],
)
def display_dropdown_float(contents, filename, date):
    if contents is None:
        return []

    df = parse_contents(contents, filename, date)

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

    return [
    	html.P(f"Valeur min : {df[value].min()}"),
    	html.P(f"Valeur max : {df[value].max()}")
    ]

#    return dcc.Graph(figure={"data": [go.Histogram(x=df[value])]})


if __name__ == "__main__":
    app.run_server(debug=True)
