#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Modèle de données propre pour les données Irigo, ainsi que les fonctions
    permettant d'importer depuis les données brutes dans le modèle de données
    propre.
"""
from sqlalchemy import create_engine, Column, Integer, BigInteger, Float, MetaData, Table, ForeignKey, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import pandas as pd
import datetime as dt

engine = create_engine('sqlite:///database.db')
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

class Etape(Base):
    __tablename__ = 'etape'
    id_etape = Column(BigInteger, primary_key=True, autoincrement=True)

    id_trajet = Column(BigInteger, ForeignKey('trajet.id_trajet'))
    id_arret = Column(BigInteger, ForeignKey('arret.id_arret'))
    heure_arret_theorique = Column(DateTime)
    heure_arret_reelle = Column(DateTime)
    record_timestamp = Column(DateTime)
    ecart = Column(Integer)

    
def create_database():
    Base.metaData.create_all(engine)