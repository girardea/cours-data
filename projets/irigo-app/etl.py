
# coding: utf-8

# # Import des modules nécessaires

# Pour gérer les date
import datetime as dt

# Pour manipuler efficacement des tables de données dans Python
import pandas as pd

# Pour faire des requêtes GET et POST
import requests

import json

# Local imports
import utils

from db import Arret, Ligne, Session, Vehicule


def download():
    # Pour lancer une requête GET, c'est ultra-simple : on utilise `requests.get(url)`.
    #
    # Si vous voulez glisser des paramètres avec la requête, utilisez l'argument optionnel `params`, qui accepte un simple dictionnaire.

    g = requests.get(
        "https://data.angers.fr/api/records/1.0/search/",
        params={"dataset": "bus-tram-position-tr", "rows": -1},
    )

    # Pour tester que tout a bien fonctionnné, on va vérifié le statut.
    g.raise_for_status()
    # On peut construire une `DataFrame` directement à partir d'un "dictionnaires de colonnes".
    dd = g.json()["records"]
    return dd


def create_dataframes(d):
    """Crée les tables (en mode DataFrame) à parti du résultat de la requête"""
    """
    Arret
    """
    id_arret = [elem["fields"]["idarret"] for elem in d]
    nom_arret = [elem["fields"]["nomarret"] for elem in d]
    mne_arret = [elem["fields"]["mnemoarret"] for elem in d]

    arret = pd.DataFrame(
        {"id_arret": id_arret, "nom_arret": nom_arret, "mne_arret": mne_arret}
    )

    # Virer les doublons
    arret = arret.drop_duplicates(subset=["id_arret"])

    """
    Vehicule
    """
    id_vehicule = [elem["fields"]["idvh"] for elem in d]
    type_vehicule = [elem["fields"]["type"] for elem in d]
    etat_vehicule = [elem["fields"]["etat"] for elem in d]

    vehicule = pd.DataFrame(
        {
            "id_vehicule": id_vehicule,
            "type_vehicule": type_vehicule,
            "etat_vehicule": etat_vehicule,
        }
    )

    # Note que les véihicules ne peuvent pas être sortis en double
    assert vehicule["id_vehicule"].nunique() == len(vehicule)

    """
    Ligne
    """
    id_ligne = [elem["fields"]["idligne"] for elem in d]
    nom_ligne = [
        elem["fields"]["nomligne"] if "nomligne" in elem["fields"] else "" for elem in d
    ]
    num_ligne = [
        elem["fields"]["mnemoligne"] if "mnemoligne" in elem["fields"] else ""
        for elem in d
    ]

    # RQ : il y avait une ENORME erreur ici (au sens où j'ai mis 30 minutes
    # à la trouver...)
    ligne = pd.DataFrame(
        {"id_ligne": id_ligne, "nom_ligne": nom_ligne, "num_ligne": num_ligne}
    )

    # Virer les doublons
    ligne = ligne.drop_duplicates(subset=["id_ligne"])

    # Trajet
    # id_trajet = [elem['fields']['iddesserte'] for elem in d]

    id_vehicule = [elem["fields"]["idvh"] for elem in d]
    id_ligne = [elem["fields"]["idligne"] for elem in d]
    latitude = [elem["fields"]["coordonnees"][0] for elem in d]
    longitude = [elem["fields"]["coordonnees"][1] for elem in d]
    destination = [
        elem["fields"]["dest"] if "dest" in elem["fields"] else "" for elem in d
    ]

    trajet = pd.DataFrame(
        {
            "id_vehicule": id_vehicule,
            "id_ligne": id_ligne,
            "latitude": latitude,
            "longitude": longitude,
            "destination": destination,
        }
    )

    # Note que les trajets ne peuvent pas être sortis en double
    # assert trajet['id_trajet'].nunique() == len(trajet)

    # Etape
    id_arret = [elem["fields"]["idarret"] for elem in d]
    harret = [elem["fields"]["harret"] for elem in d]
    record_timestamp = [elem["record_timestamp"] for elem in d]
    ecart = [elem["fields"]["ecart"] for elem in d]

    etape = pd.DataFrame(
        {
            "id_arret": id_arret,
            "heure_arret_estimee": harret,
            "ecart": ecart,
            "record_timestamp": record_timestamp,
        }
    )

    etape["record_timestamp"] = pd.to_datetime(etape["record_timestamp"])
    etape["heure_arret_estimee"] = pd.to_datetime(etape["heure_arret_estimee"])

    # TODO: remove and adapt
    etape["record_timestamp"] = etape["record_timestamp"].max()

    def transfo(row):
        return row["heure_arret_estimee"] - dt.timedelta(seconds=row["ecart"])

    etape["heure_arret_theorique"] = etape.apply(transfo, axis="columns")

    d_df = {
        "arret": arret,
        "vehicule": vehicule,
        "ligne": ligne,
        "trajet": trajet,
        "etape": etape,
    }

    return d_df


def test(d_df):
    """Test d'intégrité et d'abberation sur les données d'entrée"""
    # boucle sur les DataFrame
    for key, df in d_df.items():
        # boucle sur les colonnes des DataFrame
        for c in df.columns:
            # ID non vides
            if c in ["id_ligne", "id_arret", "id_vehicule"]:
                if df[c].isnull().any():
                    print(df.loc[df[c].isnull()])
                    msg = "{} should always be non-empty.".format(c)
                    raise ValueError(msg)
            # latitude dans les bornes angevines
            # TODO : ajouter borne max
            if c == "latitude":
                if not (df[c] > 45).all():
                    print(df.loc[df[c] <= 45])
                    msg = "Latitudes seem to be off-grid."
                    raise ValueError(msg)
            # longitude dans les bornes angevines
            # TODO : ajouter borne min
            if c == "longitude":
                if not (df[c] < 1).all():
                    msg = "Longitudes seem to be off-grid."
                    raise ValueError(msg)

    return


def add_index(df, tablename, indexname, engine):
    """Ajoute une nouvelle colonne avec l'auto-incrément"""
    from sqlalchemy import func, MetaData, select, Table

    connection = engine.connect()

    # On va chercher dans la table le dernier incrément
    table = Table(tablename, MetaData(), autoload=True, autoload_with=engine)
    stmt = select([func.max(getattr(table.c, indexname))])
    idxmax = connection.execute(stmt).scalar()

    connection.close()

    if idxmax is None:
        idxmax = -1

    # On rajoute la colonne d'index
    df[indexname] = range(idxmax + 1, idxmax + 1 + len(df))

    return df


def fill_database(d_df, verbose=False):
    if verbose:
        print("--> Filling in database")

    engine = utils.create_engine(flavor="sqlite")

    # Ajout des IDs dans les dataframes
    d_df["trajet"] = add_index(d_df["trajet"], "trajet", "id_trajet", engine)
    d_df["etape"] = add_index(d_df["etape"], "etape", "id_etape", engine)

    d_df["etape"]["id_trajet"] = d_df["trajet"]["id_trajet"]

    def filter_id(df, col, dcol):
        """Elimine de la DataFrame les éléments de col déjà présents en base"""
        session = Session()

        ids = session.query(dcol).filter(dcol.in_(df[col])).all()

        session.close()

        ids = [idx[0] for idx in ids]
        c = ~df[col].isin(ids)

        return df.loc[c]

    """
    Suppression des arrêts déjà présents en base
    """
    d_df["arret"] = filter_id(d_df["arret"], "id_arret", Arret.id_arret)

    """
    Suppression des véhicules déjà présents en base
    """
    d_df["vehicule"] = filter_id(d_df["vehicule"], "id_vehicule", Vehicule.id_vehicule)

    """
    Suppression des lignes déjà présentes en base
    """
    d_df["ligne"] = filter_id(d_df["ligne"], "id_ligne", Ligne.id_ligne)

    connection = engine.connect()

    # Export des dataframes
    for tablename, df in d_df.items():
        if verbose:
            print(tablename)

        df.to_sql(tablename, connection, if_exists="append", index=False)

    # Fermeture connection
    connection.close()
