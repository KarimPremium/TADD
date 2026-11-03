import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt


URL = "https://data.iledefrance-mobilites.fr/api/explore/v2.1/catalog/datasets/"
VALIDATIONS_JOUR = "https://data.iledefrance-mobilites.fr/api/explore/v2.1/catalog/datasets/validations-reseau-ferre-nombre-validations-par-jour-2eme-trimestre/exports/csv?delimiter=;"
VALIDATIONS_HEURE = "https://data.iledefrance-mobilites.fr/api/explore/v2.1/catalog/datasets/validations-reseau-ferre-profils-horaires-par-jour-type-3eme-trimestre/exports/csv?delimiter=;"
def charger(validations):
    df = pd.read_csv(URL + validations + "/exports/csv?delimiter=;", sep=";")
    return df


def convertir(valeur):
    try:
        x = float(str(valeur).replace(",", "."))
    except ValueError:
        return None
    if math.isnan(x):
        return None
    return x


def numeroter(liste):
    numero = {}
    for i in range(len(liste)):
        numero[liste[i]] = i
    return numero


def stations_par_jour(df):
    noms = list(set(df["libelle_arret"]))
    dates = list(set(df["jour"]))
    dates.sort()
    numero_nom = numeroter(noms)
    numero_date = numeroter(dates)

    stations = []
    for i in range(len(noms)):
        station = []
        for j in range(len(dates)):
            station.append([])
        stations.append(station)

    col_noms = list(df["libelle_arret"])
    col_dates = list(df["jour"])
    col_validations = list(df["nb_vald"])
    for i in range(len(col_noms)):
        v = convertir(col_validations[i])
        if v is not None:
            stations[numero_nom[col_noms[i]]][numero_date[col_dates[i]]].append(v)
    return noms, dates, stations


def stations_par_heure(df, noms, moyennes, type_jour):
    numero_nom = numeroter(noms)

    stations = []
    for i in range(len(noms)):
        station = []
        for h in range(24):
            station.append([])
        stations.append(station)

    col_cat = list(df["cat_jour"])
    col_noms = list(df["libelle_arret"])
    col_heures = list(df["trnc_horr_60"])
    col_pourcentages = list(df["pourc_validations"])
    for i in range(len(col_cat)):
        p = convertir(col_pourcentages[i])
        tranche = str(col_heures[i])
        if col_cat[i] == type_jour and p is not None and tranche[0].isdigit() and col_noms[i] in numero_nom:
            h = int(tranche.split("H")[0])
            k = numero_nom[col_noms[i]]
            if h < 24:
                stations[k][h].append(moyennes[k] * p / 100)
    return stations


def validation_navigo_moyen_par_station(station, dates):
    c = 0
    for i in range(len(dates)):
        c = c + sum(station[i])
    moyenne = c / len(dates)
    return moyenne


def validation_navigo_moyen_par_station_par_heure(station, heure):  # V2
    validation = station[heure]
    if len(validation) == 0:
        return 0
    moyenne_horaire = sum(validation) / len(validation)
    return moyenne_horaire


def top_stations_par_validation_par_heure(stations, heure):
    D = []
    for i in range(len(stations)):
        D.append([validation_navigo_moyen_par_station_par_heure(stations[i], heure), i])
    D.sort(reverse=True)
    return D


def top_stations_par_validation(stations, dates):
    D = []
    for i in range(len(stations)):
        D.append([validation_navigo_moyen_par_station(stations[i], dates), i])
    D.sort(reverse=True)
    return D


def concentration_des_validation_par_heure(stations, heure):
    tuple_top_stations = []
    for h in range(heure):
        tuple_top_stations.append(top_stations_par_validation_par_heure(stations, h))
    return tuple_top_stations


def tracer_top_stations(top, noms, n):
    x = []
    y = []
    for i in range(min(n, len(top)) - 1, -1, -1):
        x.append(noms[top[i][1]])
        y.append(top[i][0])
    plt.figure(figsize=(10, 6))
    plt.barh(x, y)
    plt.xlabel("Validations moyennes par jour")
    plt.title("Stations les plus fréquentées")
    plt.tight_layout()
    plt.show()


def tracer_profil_station(station, nom):
    heures = []
    valeurs = []
    for h in range(24):
        heures.append(str(h) + "H")
        valeurs.append(validation_navigo_moyen_par_station_par_heure(station, h))
    plt.figure(figsize=(12, 5))
    plt.bar(heures, valeurs)
    plt.xlabel("Heure")
    plt.ylabel("Validations estimées")
    plt.title("Profil horaire : " + nom)
    plt.tight_layout()
    plt.show()



df_jour = charger(VALIDATIONS_JOUR)
df_heure = charger(VALIDATIONS_HEURE)

noms, dates, stations_jour = stations_par_jour(df_jour)

moyennes = []
for i in range(len(stations_jour)):
    moyennes.append(validation_navigo_moyen_par_station(stations_jour[i], dates))

stations_heure = stations_par_heure(df_heure, noms, moyennes, "JOHV")

top = top_stations_par_validation(stations_jour, dates)
for i in range(min(10, len(top))):
    print(noms[top[i][1]], round(top[i][0]))

concentration = concentration_des_validation_par_heure(stations_heure, 24)
for h in range(24):
    print(str(h) + "H", noms[concentration[h][0][1]])

tracer_top_stations(top, noms, 10)
tracer_profil_station(stations_heure[top[0][1]], noms[top[0][1]])