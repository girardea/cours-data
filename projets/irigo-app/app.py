#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Lancement du serveur qui fait tourner l'app complète (le tableau de bord).
"""

import argparse

import glob

import json

import progressbar

# https://stackoverflow.com/questions/40845304/runtimewarning-numpy-dtype-size-changed-may-indicate-binary-incompatibility
import warnings
warnings.filterwarnings("ignore", message="numpy.dtype size changed")

# from db import create_database
from dataviz import run_dash

from db import create_database, drop_database, check_database

from etl import download, create_dataframes, test, fill_database


def fetch(verbose=False, directory="./data"):
    """Requête sur l'API data.angers.fr et stockage dans un fichier JSON"""
    # Pour manipuler les dates et temps
    import datetime as dt

    # Pour trouver des fichiers (ls-like)
    import glob

    # Pour manipuler des fichiers/dossiers sur le système
    import os

    # Pour faire des requêtes GET et POST
    import requests

    if verbose:
        print("--> Fetching data.angers.fr API at {}".format(dt.datetime.now()))

    r = requests.get(
        "https://data.angers.fr/api/records/1.0/search/",
        params={"dataset": "bus-tram-position-tr", "rows": -1},
    )

    # test
    r.raise_for_status()

    # On vérifie que le dossier de stockage des données existe
    if not os.path.exists(directory):
        os.makedirs(directory)

    if not os.path.isdir(directory):
        msg = "Path {} seems to be a file and not a directory".format(directory)
        raise Exception()

    # On trouve le dernier indice utilisé pour nommer les fichiers
    ll = []
    for file in glob.glob(os.path.join(directory, "*.json")):
        num = file.split("/data.")[-1].split(".json")[0]
        num = int(num)

        ll.append(num)

    if len(ll) == 0:
        idx = 1
    else:
        idx = max(ll) + 1

    filepath = os.path.join(directory, "data." + str(idx) + ".json")
    with open(filepath, "w") as file:
        file.write(r.text)

    if verbose:
        print("--> Wrote to {}".format(filepath))


def run_server():
    print("run server")
    run_dash()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--run-server",
        help="run web server to display graphs",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--create-db", help="create database", action="store_true", default=False
    )
    parser.add_argument(
        "--drop-db",
        help="drops all tables in database",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--check-db",
        help="gives info about tables in" " database",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--fetch",
        help="fetches API and dumps in json file",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--update",
        help="queries API and updates database",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--reset",
        help="updates database with JSON files in " "'data' subfolder",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--verbose", help="verbose mode", action="store_true", default=False
    )
    parser.add_argument(
        "--docker", help="docker deploy", action="store_true", default=False
    )

    args = parser.parse_args()

    if args.drop_db:
        if args.verbose:
            print("--> Dropping all tables in database")
        drop_database()

    if args.create_db:
        if args.verbose:
            print("--> Creating database")
        create_database()

    if args.check_db:
        check_database()

    if args.fetch:
        fetch(verbose=args.verbose)

    if args.update:
        # Requête l'API et renvoie un dictionnaire (traduction objet du JSON)
        d = download()

        # A partir du dictionnaire, on crée les tables
        # sous la forme de DataFrames
        d_df = create_dataframes(d)

        # On teste les colonnes (types, aberrations, etc.)
        # test(d_df)

        # On rentre ces informations dans la DB
        fill_database(d_df, verbose=args.verbose)

    if args.reset:
        filenames = glob.glob("data/*.json")
        bar = progressbar.ProgressBar(max_value=len(filenames))
        for i, filename in enumerate(filenames):
            if args.verbose:
                print(filename)

            with open(filename, "r") as file:
                d = json.load(file)

            # Si pas de données (la nuit), on passe.
            if len(d["records"]) == 0:
                continue

            # A partir du dictionnaire, on crée les tables
            # sous la forme de DataFrames
            d_df = create_dataframes(d["records"])

            # On teste les colonnes (types, aberrations, etc.)
            # test(d_df)

            # On rentre ces informations dans la DB
            fill_database(d_df, verbose=args.verbose)

            bar.update(i)

        bar.finish()

    if args.run_server:
        run_dash(args.docker)
