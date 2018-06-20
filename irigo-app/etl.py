
# coding: utf-8

# # Import des modules nécessaires

# Pour gérer les date
import datetime as dt

# Pour manipuler efficacement des tables de données dans Python
import pandas as pd
# Pour faire des requêtes GET et POST
import requests

# sql
from sqlalchemy import create_engine


def download():
    # Pour lancer une requête GET, c'est ultra-simple : on utilise `requests.get(url)`.
    #
    # Si vous voulez glisser des paramètres avec la requête, utilisez l'argument optionnel `params`, qui accepte un simple dictionnaire.

    g = requests.get("https://data.angers.fr/api/records/1.0/search/",
                     params={
                         'dataset': 'bus-tram-position-tr',
                         'rows': -1
                     })

    # Pour tester que tout a bien fonctionnné, on va vérifié le statut.
    g.raise_for_status()
    # On peut construire une `DataFrame` directement à partir d'un "dictionnaires de colonnes".
    dd = g.json()['records']
    return dd

def create_dataframes(d):
    # Arret
    id_arret = [elem['fields']['idarret'] for elem in d]
    nom_arret = [elem['fields']['nomarret'] for elem in d]
    mne_arret = [elem['fields']['mnemoarret'] for elem in d]

    arret = pd.DataFrame({
        'id_arret': id_arret,
        'nom_arret': nom_arret,
        'mne_arret': mne_arret
    })

    # Vehicule
    id_vehicule = [elem['fields']['idvh'] for elem in d]
    type_vehicule = [elem['fields']['type'] for elem in d]
    etat_vehicule = [elem['fields']['etat'] for elem in d]

    bus = pd.DataFrame({
        'id_vehicule': id_vehicule,
        'type_vehicule': type_vehicule,
        'etat_vehicule': etat_vehicule
    })

    # Ligne
    id_ligne = [elem['fields']['idligne'] for elem in d]
    nom_ligne = [elem['fields']['nomligne'] for elem in d]
    num_ligne = [elem['fields']['mnemoligne'] for elem in d]

    ligne = pd.DataFrame({
        'id_ligne': id_arret,
        'nom_ligne': nom_ligne,
        'num_ligne': num_ligne
    })

    # Trajet
    id_vehicule = [elem['fields']['idvh'] for elem in d]
    id_ligne = [elem['fields']['idligne'] for elem in d]
    latitude = [elem['fields']['coordonnees'][0] for elem in d]
    longitude = [elem['fields']['coordonnees'][1] for elem in d]
    destination = [elem['fields']['dest'] for elem in d]

    trajet = pd.DataFrame({
        'id_vehicule': id_vehicule,
        'id_ligne': id_ligne,
        'latitude': latitude,
        'longitude': longitude,
        'destination': destination
    })

    # Etape
    id_arret = [elem['fields']['idarret'] for elem in d]
    harret = [elem['fields']['harret'] for elem in d]
    record_timestamp = [elem['record_timestamp'] for elem in d]
    ecart = [elem['fields']['ecart'] for elem in d]

    etape = pd.DataFrame({
        'id_arret': id_arret,
        'heure_arret_theorique': harret,
        'ecart': ecart,
        'record_timestamp': record_timestamp
    })

    etape['record_timestamp'] = pd.to_datetime(etape['record_timestamp'])

    def transfo(row):
        return row['record_timestamp'] + dt.timedelta(seconds=row['ecart'])

    etape['heure_arret_theorique'] = etape.apply(transfo, axis='columns')

    d_df =  {
        'arret': arret,
        'bus': bus,
        'ligne': ligne,
        'trajet': trajet,
        'etape': etape
    }

    return d_df


def add_index(df, tablename, indexname, engine):
    """Ajoute une nouvelle colonne avec l'auto-incrément"""
    from sqlalchemy import func, MetaData, select, Table

    connection = engine.connect()

    # On va chercher dans la table le dernier incrément
    table = Table(tablename, MetaData(), autoload=True,
                  autoload_with=engine)
    stmt = select([func.max(getattr(table.c, indexname))])
    idxmax = connection.execute(stmt).scalar()

    connection.close()

    if idxmax is None:
        idxmax = -1

    # On rajoute la colonne d'index
    df[indexname] = range(idxmax + 1, idxmax + 1 + len(df))

    return df

def fill_database(d_df):
    # Ouverture de la connection vers la bdd
    engine = create_engine("sqlite:///database.db")
    connection = engine.connect()

    # Table arret
    arret.to_sql('arret', connection, if_exists='replace', index=False)

    # Table vehicule
    vehicule.to_sql('vehicule', connection, if_exists='replace', index=False)

    # Table ligne
    ligne.to_sql('ligne', connection, if_exists='replace', index=False)

    # Table trajet
    trajet = add_index(trajet, 'trajet', 'id_trajet', engine)
    trajet.to_sql('trajet', connection, if_exists='append', index=False)

    # Table etape
    etape = add_index(etape, 'etape', 'id_etape', engine)
    etape.to_sql('etape', connection, if_exists='append', index=False)

    # Fermeture connection
    connection.close()

