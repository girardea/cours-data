
# coding: utf-8

# # Import des modules nécessaires

# In[22]:

# Pour manipuler efficacement des tables de données dans Python
import pandas as pd

# Pour faire des requêtes GET et POST
import requests

# Pour gérer les date
import datetime as dt

# sql
from sqlalchemy import create_engine


# In[23]:

print(pd.__version__)


# In[24]:

print(requests.__version__)


# # Requêtage d'une API REST

# Pour lancer une requête GET, c'est ultra-simple : on utilise `requests.get(url)`.
# 
# Si vous voulez glisser des paramètres avec la requête, utilisez l'argument optionnel `params`, qui accepte un simple dictionnaire.

# In[25]:

r = requests.get("https://data.angers.fr/api/records/1.0/search/",
                 params={
                     'dataset': 'horaires-theoriques-et-arrets-du-reseau-irigo-gtfs',
                     'rows': 10
                 })


# In[26]:

g = requests.get("https://data.angers.fr/api/records/1.0/search/",
                 params={
                     'dataset': 'bus-tram-position-tr',
                     'rows': 200
                 })


# Regardons la nature de ce qui nous est renvoyé.

# In[27]:

type(g)


# C'est un objet de la classe `Response`. Si vous voulez connaitre toutes les méthodes attachées, faites `help(r)`

# In[28]:

help(g)


# Pour tester que tout a bien fonctionnné, on va vérifié le statut.

# In[29]:

g.raise_for_status()


# Si ça dit rien c'est que c'est bon :) Dans le doute, regardons le statut...

# In[30]:

g.status_code


# Statut 200 = succès !!

# In[31]:

g.json()


# # Remplissage de DataFrame

# On peut construire une `DataFrame` directement à partir d'un "dictionnaires de colonnes".

# In[32]:

dd = g.json()['records']


# In[38]:

dd[0]


# In[39]:

#Arret
id_arret = [elem['fields']['idarret'] for elem in dd]
nom_arret = [elem['fields']['nomarret'] for elem in dd]
mne_arret = [elem['fields']['mnemoarret'] for elem in dd]

arret = pd.DataFrame({
    'id_arret': id_arret,
    'nom_arret': nom_arret,
    'mne_arret': mne_arret
})

#arret.info()

arret


# In[40]:

#Bus
id_vh = [elem['fields']['idvh'] for elem in dd]
type_vh = [elem['fields']['type'] for elem in dd]
etat_vh = [elem['fields']['etat'] for elem in dd]

bus = pd.DataFrame({
    'id_vh': id_vh,
    'type_vh': type_vh,
    'etat_vh': etat_vh
})

#bus.info()

bus


# In[41]:

#Ligne
id_ligne = [elem['fields']['idligne'] for elem in dd]
nom_ligne = [elem['fields']['nomligne'] for elem in dd]
mne_ligne = [elem['fields']['mnemoligne'] for elem in dd]

ligne = pd.DataFrame({
    'id_ligne': id_arret,
    'nom_ligne': nom_ligne,
    'mne_ligne': mne_ligne
})

#ligne.info()

ligne


# In[42]:

#Trajet
id_bus = [elem['fields']['idvh'] for elem in dd]
id_ligne = [elem['fields']['idligne'] for elem in dd]
latitude = [elem['fields']['coordonnees'][0] for elem in dd]
longitude = [elem['fields']['coordonnees'][1] for elem in dd]

trajet = pd.DataFrame({
    'id_bus': id_bus,
    'id_ligne': id_ligne,
    'latitude': latitude,
    'longitude': longitude
})

#trajet.info()

trajet


# In[43]:

#Etape
id_arret = [elem['fields']['idarret'] for elem in dd]
harret = [elem['fields']['harret'] for elem in dd]
record_timestamp = [elem['record_timestamp'] for elem in dd]
ecart = [elem['fields']['ecart'] for elem in dd]

etape = pd.DataFrame({
    'id_arret': id_arret,
    'heure_theorique': harret,
    'ecart': ecart,
    'record_timestamp': record_timestamp
})

etape['record_timestamp'] = pd.to_datetime(etape['record_timestamp'])

def transfo(row):
    return row['record_timestamp'] + dt.timedelta(seconds=row['ecart'])
etape['heure_estime'] = etape.apply(transfo, axis='columns')

#etape.info()

etape


# In[44]:

#Ouverture de la connection vers la bdd
engine = create_engine("sqlite:///data.sqlite")
connection = engine.connect()


# In[45]:

#Table arret
arret.to_sql('arret', connection, if_exists='replace', index=False)


# In[46]:

#Table bus
bus.to_sql('bus', connection, if_exists='replace', index=False)


# In[47]:

#Table ligne
ligne.to_sql('ligne', connection, if_exists='replace', index=False)


# In[48]:

#Table trajet
trajet.to_sql('trajet', connection, if_exists='replace', index=False)


# In[49]:

#Table etape
etape.to_sql('etape', connection, if_exists='replace', index=False)


# In[50]:

#Fermeture connection
connection.close()


# In[ ]:



