#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Modèle de données propre pour les données Irigo, ainsi que les fonctions
    permettant d'importer depuis les données brutes dans le modèle de données
    propre.
"""
from sqlalchemy import (Column, Integer, BigInteger, Float, MetaData, Table,
                        ForeignKey, select, String, DateTime, func)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import pandas as pd
import datetime as dt
import json

# Local imports
import utils

engine = utils.create_engine(flavor='sqlite')

Session = sessionmaker(bind=engine)

Base = declarative_base()

class Arret(Base):
    __tablename__ = 'arret'
    id_arret = Column(BigInteger, primary_key=True, autoincrement=True)

    nom_arret = Column(String(32))
    mne_arret = Column(String(32))

    def __repr__(self):
        return "nom_arret='{}'".format(self.nom_arret)

class Vehicule(Base):
    __tablename__ = 'vehicule'
    id_vehicule = Column(BigInteger, primary_key=True, autoincrement=True)

    type_vehicule = Column(String(32))
    etat_vehicule = Column(String(32))

class Ligne(Base):
    __tablename__ = 'ligne'
    id_ligne = Column(BigInteger, primary_key=True, autoincrement=True)

    nom_ligne = Column(String(32))
    num_ligne = Column(String(32))

class Trajet(Base):
    __tablename__ = 'trajet'
    id_trajet = Column(BigInteger, primary_key=True, autoincrement=True)

    id_vehicule = Column(BigInteger, ForeignKey('vehicule.id_vehicule'))
    id_ligne = Column(BigInteger, ForeignKey('ligne.id_ligne'))
    latitude = Column(Float)
    longitude = Column(Float)
    destination = Column(String(32))

    etapes = relationship("Etape")

    def __str__( self ):
        return 'id:'+str(self.id_trajet)+', id_vehicule:'+str(self.id_vehicule)+', id_ligne:'+str(self.id_ligne)

class Etape(Base):
    __tablename__ = 'etape'
    id_etape = Column(BigInteger, primary_key=True, autoincrement=True)

    id_trajet = Column(BigInteger, ForeignKey('trajet.id_trajet'))
    id_arret = Column(BigInteger, ForeignKey('arret.id_arret'))
    heure_arret_theorique = Column(DateTime)
    heure_arret_estimee = Column(DateTime)
    record_timestamp = Column(DateTime)
    ecart = Column(Integer)

    def __str__( self ):
        return 'id:'+str(self.id_etape)+', id_trajet:'+str(self.id_trajet)+', id_arret:'+str(self.id_arret)+', ecart:'+str(self.ecart)

    
def create_database():
    Base.metadata.create_all(bind=engine)

def drop_database():
    Base.metadata.drop_all(bind=engine)

def check_database():
    """Affcihe quelques infos sur les tables en base"""
    connection = engine.connect()

    for tablename in engine.table_names():

        # création de l'objet Table
        table = Table(tablename, MetaData(), autoload=True,
                      autoload_with=engine)
        # nom de la table
        print("\n*** {} ***\n".format(tablename))

        # nombre de lignes dans la table
        stmt = select([func.count(table)])
        nrows = connection.execute(stmt).scalar()
        print("{} lignes en base.".format(nrows))

        # les premières lignes
        print("Premières lignes :")
        stmt = select([table]).limit(5)
        print(pd.read_sql_query(stmt, connection))

    connection.close()
