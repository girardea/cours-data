#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Test Insert de données dans la BDD.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pandas as pd
import datetime as dt

from db import Arret, Bus, Ligne, Trajet, Etape

engine = create_engine('sqlite:///database.db')
Session = sessionmaker(bind=engine)

arret1 = Arret(id_arret=1, nom_arret='Arret 1')
arret2 = Arret(id_arret=2, nom_arret='Arret 2')
arret3 = Arret(id_arret=3, nom_arret='Arret 3')

bus1 = Bus(id_bus=1, type='Type Bus 1', etat='Etat 1')
bus2 = Bus(id_bus=2, type='Type Bus 2', etat='Etat 1')
bus3 = Bus(id_bus=3, type='Type Bus 1', etat='Etat 2')

ligne1 = Ligne(id_ligne=1, nom_ligne='MURS ERIGNE <> ADEZIERE SALETTE', num_ligne='3')

trajet1 = Trajet(id_trajet=1, id_bus=1, id_ligne=1, latitude=-0.59608549, longitude=47.511559, destination="AVRILLE ADEZIERE")

etape1 = Etape(id_etape=1, id_trajet=1, id_arret=1, heure_arret_theorique=dt.datetime(2018, 6, 18, 16, 32, 00), heure_arret_estime=dt.datetime(2018, 6, 18, 16, 33, 00), ecart=60)
etape2 = Etape(id_etape=2, id_trajet=1, id_arret=2, heure_arret_theorique=dt.datetime(2018, 6, 18, 16, 40, 00), heure_arret_estime=dt.datetime(2018, 6, 18, 16, 42, 00), ecart=120)
etape3 = Etape(id_etape=3, id_trajet=1, id_arret=3, heure_arret_theorique=dt.datetime(2018, 6, 18, 16, 55, 00), heure_arret_estime=dt.datetime(2018, 6, 18, 16, 58, 00), ecart=180)

session = Session()

session.add(arret1)
session.add(arret2)
session.add(arret3)

session.add(bus1)
session.add(bus2)
session.add(bus3)

session.add(ligne1)

session.add(trajet1)

session.add(etape1)
session.add(etape2)
session.add(etape3)

session.commit()

session.close()

connection = engine.connect()

print (pd.read_sql_table("arret", connection))
print (pd.read_sql_table("bus", connection))
print (pd.read_sql_table("ligne", connection))
print (pd.read_sql_table("trajet", connection))
print (pd.read_sql_table("etape", connection))

connection.close()