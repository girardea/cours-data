
# coding: utf-8

# # Import des modules nécessaires

# Pour manipuler efficacement des tables de données dans Python
import pandas as pd

# Pour faire des requêtes GET et POST
import requests

# Pour gérer les date
import datetime as dt

# sql
from sqlalchemy import create_engine

# # Requêtage d'une API REST

# Pour lancer une requête GET, c'est ultra-simple : on utilise `requests.get(url)`.
# 
# Si vous voulez glisser des paramètres avec la requête, utilisez l'argument optionnel `params`, qui accepte un simple dictionnaire.

g = requests.get("https://data.angers.fr/api/records/1.0/search/",
                 params={
                     'dataset': 'bus-tram-position-tr',
                     'rows': -1
                 })

# Regardons la nature de ce qui nous est renvoyé.

# Pour tester que tout a bien fonctionnné, on va vérifié le statut.

g.raise_for_status()


# Si ça dit rien c'est que c'est bon :) Dans le doute, regardons le statut...

# # Remplissage de DataFrame

# On peut construire une `DataFrame` directement à partir d'un "dictionnaires de colonnes".

dd = g.json()['records']

# Arret
id_arret = [elem['fields']['idarret'] for elem in dd]
nom_arret = [elem['fields']['nomarret'] for elem in dd]
mne_arret = [elem['fields']['mnemoarret'] for elem in dd]

arret = pd.DataFrame({
    'id_arret': id_arret,
    'nom_arret': nom_arret,
    'mne_arret': mne_arret
})

#Vehicule
id_vehicule = [elem['fields']['idvh'] for elem in dd]
type_vehicule = [elem['fields']['type'] for elem in dd]
etat_vehicule = [elem['fields']['etat'] for elem in dd]

bus = pd.DataFrame({
    'id_vehicule': id_vehicule,
    'type_vehicule': type_vehicule,
    'etat_vehicule': etat_vehicule
})

#Ligne
id_ligne = [elem['fields']['idligne'] for elem in dd]
nom_ligne = [elem['fields']['nomligne'] for elem in dd]
num_ligne = [elem['fields']['mnemoligne'] for elem in dd]

ligne = pd.DataFrame({
    'id_ligne': id_arret,
    'nom_ligne': nom_ligne,
    'num_ligne': num_ligne
})

#Trajet
id_vehicule = [elem['fields']['idvh'] for elem in dd]
id_ligne = [elem['fields']['idligne'] for elem in dd]
latitude = [elem['fields']['coordonnees'][0] for elem in dd]
longitude = [elem['fields']['coordonnees'][1] for elem in dd]
destination = [elem['fields']['dest'] for elem in dd]

trajet = pd.DataFrame({
    'id_vehicule': id_vehicule,
    'id_ligne': id_ligne,
    'latitude': latitude,
    'longitude': longitude,
    'destination': destination
})

#Etape
id_arret = [elem['fields']['idarret'] for elem in dd]
harret = [elem['fields']['harret'] for elem in dd]
record_timestamp = [elem['record_timestamp'] for elem in dd]
ecart = [elem['fields']['ecart'] for elem in dd]

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


# Ouverture de la connection vers la bdd
engine = create_engine("sqlite:///database.db")
connection = engine.connect()

#Table arret
arret.to_sql('arret', connection, if_exists='replace', index=False)

#Table bus
bus.to_sql('bus', connection, if_exists='replace', index=False)

#Table ligne
ligne.to_sql('ligne', connection, if_exists='replace', index=False)

#Table trajet
trajet.to_sql('trajet', connection, if_exists='replace', index=False)

#Table etape
etape.to_sql('etape', connection, if_exists='replace', index=False)

#Fermeture connection
connection.close()
