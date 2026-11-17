import pandas as pd
import plotly.express as px


VALIDATIONS_JOUR = "https://data.iledefrance-mobilites.fr/api/explore/v2.1/catalog/datasets/validations-reseau-ferre-nombre-validations-par-jour-2eme-trimestre/exports/csv?delimiter=;"
VALIDATIONS_HEURE = "https://data.iledefrance-mobilites.fr/api/explore/v2.1/catalog/datasets/validations-reseau-ferre-profils-horaires-par-jour-type-2eme-trimestre/exports/csv?delimiter=;"


def charger(validations):
    df = pd.read_csv(validations, sep=";", low_memory=False)
    return df


def convertir(valeur):
    # "12,5" -> 12.5 ; tout ce qui n'est pas un nombre devient NaN
    return pd.to_numeric(valeur.astype(str).str.replace(",", "."), errors="coerce")


def stations_par_jour(df):
    # Une ligne de l'API = une station, un jour, une catégorie de titre :
    # on additionne toutes les catégories pour avoir le total du jour.
    df = df[df["libelle_arret"] != "Inconnu"].copy()
    df["nb_vald"] = convertir(df["nb_vald"])
    stations = df.pivot_table(index="libelle_arret", columns="jour", values="nb_vald", aggfunc="sum", fill_value=0)
    noms = list(stations.index)
    dates = list(stations.columns)
    return noms, dates, stations


def trouver_colonne(df, debut):
    for nom in df.columns:
        if nom.startswith(debut):
            return nom
    return None


def stations_par_heure(df, noms, moyennes, type_jour):
    colonne = trouver_colonne(df, "pourc")
    df = df[(df["cat_jour"] == type_jour) & df["libelle_arret"].isin(noms)].copy()
    df["heure"] = pd.to_numeric(df["trnc_horr_60"].str.extract(r"^(\d+)H", expand=False))  # "ND" -> NaN
    df["pourcentage"] = convertir(df[colonne])
    df = df.dropna(subset=["heure", "pourcentage"])

    # Une station peut avoir plusieurs codes (RATP / SNCF) : on moyenne leurs profils.
    pourcentages = df.pivot_table(index="libelle_arret", columns="heure", values="pourcentage", aggfunc="mean")
    pourcentages = pourcentages.reindex(index=noms, columns=range(24)).fillna(0)
    stations = pourcentages.mul(moyennes, axis=0) / 100
    return stations


def validation_navigo_moyen_par_station(station, dates):
    moyenne = station[dates].sum() / len(dates)
    return moyenne


def top_stations_par_validation_par_heure(stations, heure):
    return stations[heure].sort_values(ascending=False)


def top_stations_par_validation(stations, dates):
    moyennes = stations.apply(validation_navigo_moyen_par_station, axis=1, args=(dates,))
    return moyennes.sort_values(ascending=False)


def concentration_des_validation_par_heure(stations, heure):
    tuple_top_stations = []
    for h in range(heure):
        tuple_top_stations.append(top_stations_par_validation_par_heure(stations, h))
    return tuple_top_stations


def charger_donnees_validations():
    df_jour = charger(VALIDATIONS_JOUR)
    df_heure = charger(VALIDATIONS_HEURE)
    noms, dates, stations_jour = stations_par_jour(df_jour)

    # Le profil horaire "JOHV" (jour ouvré hors vacances) s'applique à la moyenne
    # des jours ouvrés, pas à celle de tous les jours (week-ends compris).
    jours_ouvres = [d for d in dates if pd.Timestamp(d).dayofweek < 5]
    moyennes = stations_jour.apply(validation_navigo_moyen_par_station, axis=1, args=(jours_ouvres,))
    stations_heure = stations_par_heure(df_heure, noms, moyennes, "JOHV")

    # Identifiant de zone (id_zdc) de chaque station, pour la relier aux lignes du réseau.
    zones = df_jour.dropna(subset=["id_zdc"]).groupby("libelle_arret")["id_zdc"].first().astype(int)
    return noms, dates, stations_jour, stations_heure, zones


def tracer_top_stations(top, n):
    top = top.head(n)[::-1]
    fig = px.bar(
        x=top.values,
        y=top.index,
        orientation="h",
        labels={"x": "Validations moyennes par jour", "y": "Station"},
        title="Stations les plus fréquentées",
    )
    fig.show()


def tracer_profil_station(station, nom):
    heures = [str(h) + "H" for h in range(24)]
    fig = px.bar(
        x=heures,
        y=station.values,
        labels={"x": "Heure", "y": "Validations estimées (jour ouvré)"},
        title="Profil horaire : " + nom,
    )
    fig.show()


if __name__ == "__main__":
    noms, dates, stations_jour, stations_heure, zones = charger_donnees_validations()

    top = top_stations_par_validation(stations_jour, dates)
    for nom, valeur in top.head(10).items():
        print(nom, round(valeur))

    concentration = concentration_des_validation_par_heure(stations_heure, 24)
    for h in range(24):
        print(str(h) + "H", concentration[h].index[0])

    tracer_top_stations(top, 10)
    tracer_profil_station(stations_heure.loc[top.index[0]], top.index[0])
