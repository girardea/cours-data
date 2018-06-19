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

class Bus(Base):
    __tablename__ = 'bus'
    id_bus = Column(BigInteger, primary_key=True, autoincrement=True)
    type = Column(String(32))
    etat = Column(String(32))

class Ligne(Base):
    __tablename__ = 'ligne'
    id_ligne = Column(BigInteger, primary_key=True, autoincrement=True)
    nom_ligne = Column(String(32))
    num_ligne = Column(String(32))

class Trajet(Base):
    __tablename__ = 'trajet'
    id_trajet = Column(BigInteger, primary_key=True, autoincrement=True)
    id_bus = Column(BigInteger, ForeignKey('bus.id_bus'))
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
    ecart = Column(Integer)

class Arret(Base):
    __tablename__ = 'arret'
    id_arret = Column(Integer, primary_key=True, autoincrement=True)
    nom_arret = Column(String(32))

Base.metadata.create_all(engine)