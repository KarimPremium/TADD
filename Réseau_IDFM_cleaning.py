import json
import math
import pandas as pd
import Réseau_IDFM_cleaning as idfm

Resau_IDFM = (https://data.iledefrance-mobilites.fr/api/explore/v2.1/catalog/datasets/referentiel-des-lignes/records?limit=100)

def lignes_bus_metadonnes(liste):
    return [
            {k: v for k, v in ligne.items() if k != "type"}
            for ligne in liste
            if ligne.get("type") == "bus"
        ]

def lignes_tram_metadonnes(liste):
    return [
            {k: v for k, v in ligne.items() if k != "type"}
            for ligne in liste
            if ligne.get("type") == "tram"
        ]

def lignes_metro_metadonnes(liste):
    return [
            {k: v for k, v in ligne.items() if k != "type"}
            for ligne in liste
            if ligne.get("type") == "metro"
        ]

def lignes_rer_metadonnes(liste):
    return [
            {k: v for k, v in ligne.items() if k != "type"}
            for ligne in liste
            if ligne.get("type") == "rer"
        ]

def lignes_transilien_metadonnes(liste):
    return [
        {k: v for k, v in ligne.items() if k != "type"}
        for ligne in liste
        if ligne.get("type") == "transilien"
    ]


bus, tram, metro, rer, transilien = lignes_bus_metadonnes(idfm.charger(Resau_IDFM)), lignes_tram_metadonnes(idfm.charger(Resau_IDFM)), lignes_metro_metadonnes(idfm.charger(Resau_IDFM)), lignes_rer_metadonnes(idfm.charger(Resau_IDFM)), lignes_transilien_metadonnes(idfm.charger(Resau_IDFM))

""" faire la meme chose avec les stations, puis dans retard incidents idfm : corrélation entre les deux """