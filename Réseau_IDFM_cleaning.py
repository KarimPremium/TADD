import re
import pandas as pd
from Navigo_validations_cleaning import charger

Resau_IDFM = "https://data.iledefrance-mobilites.fr/api/explore/v2.1/catalog/datasets/referentiel-des-lignes/exports/csv?delimiter=;"
Gares_IDFM = "https://data.iledefrance-mobilites.fr/api/explore/v2.1/catalog/datasets/emplacement-des-gares-idf/exports/csv?delimiter=;"

# Dans le référentiel, le mode est dans "transportmode" (bus, tram, metro, rail) ;
# RER et Transilien sont tous les deux "rail", on les sépare par "networkname".
# La colonne "type" ne donne pas le mode (lignes de remplacement, saisonnières).


def lignes_bus_metadonnes(liste):
    return liste[liste["transportmode"] == "bus"]


def lignes_tram_metadonnes(liste):
    return liste[liste["transportmode"] == "tram"]


def lignes_metro_metadonnes(liste):
    return liste[liste["transportmode"] == "metro"]


def lignes_rer_metadonnes(liste):
    return liste[(liste["transportmode"] == "rail") & (liste["networkname"] == "RER")]


def lignes_transilien_metadonnes(liste):
    return liste[(liste["transportmode"] == "rail") & (liste["networkname"] == "Transilien")]


def charger_lignes(url=Resau_IDFM):
    lignes = charger(url)
    return (
        lignes_bus_metadonnes(lignes),
        lignes_tram_metadonnes(lignes),
        lignes_metro_metadonnes(lignes),
        lignes_rer_metadonnes(lignes),
        lignes_transilien_metadonnes(lignes),
    )


def nom_ligne(mode, indice):
    # Écrit la ligne comme dans les incidents (ratpstatus.fr) : "Métro 3B", "Ligne A", "T3A", "C1"
    indice = re.sub(r"bis$", "B", str(indice)).upper()
    if mode == "METRO":
        return "Métro " + indice
    if mode in ("RER", "TRAIN"):
        return "Ligne " + indice
    if mode == "TRAMWAY":
        return "T" + indice
    if mode == "CABLE":
        return "C" + indice
    return indice


def charger_stations(url=Gares_IDFM):
    # Une ligne de l'API = une gare sur une ligne, avec son identifiant de zone (id_ref_zdc),
    # le même que "id_zdc" dans les validations : c'est la clé pour relier les deux.
    gares = charger(url)
    gares["ligne"] = [nom_ligne(mode, indice) for mode, indice in zip(gares["mode"], gares["indice_lig"])]
    return gares[["ligne", "id_ref_zdc", "nom_zdc"]].drop_duplicates()


if __name__ == "__main__":
    bus, tram, metro, rer, transilien = charger_lignes()
    print(len(bus), "bus,", len(tram), "tram,", len(metro), "métro,", len(rer), "RER,", len(transilien), "Transilien")

    stations = charger_stations()
    print(stations.groupby("ligne")["nom_zdc"].count())
