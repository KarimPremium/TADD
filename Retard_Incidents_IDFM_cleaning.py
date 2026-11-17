import re
import pandas as pd
import plotly.express as px

INCIDENTS = "https://ratpstatus.fr/{:%Y%m%d}/timeline.csv"


def charger_incidents(annee=2025):
    # 365 téléchargements : on garde une copie locale pour les lancements suivants.
    fichier = f"incidents_{annee}.csv"
    try:
        df = pd.read_csv(fichier, sep=";")
    except FileNotFoundError:
        frames = []
        for j in pd.date_range(f"{annee}-01-01", f"{annee}-12-31"):
            try:
                d = pd.read_csv(INCIDENTS.format(j), sep=";", engine="python", on_bad_lines=lambda r: r[:8])
                frames.append(d.iloc[:, :7])
            except (OSError, ValueError):
                pass  # jour manquant
        df = pd.concat(frames, ignore_index=True)
        df.columns = ["jour", "mode", "ligne", "debut", "fin", "statut", "id_incident"]
        df.to_csv(fichier, sep=";", index=False)

    df["jour"] = pd.to_datetime(df["jour"])
    df["debut"] = pd.to_datetime(df["debut"])
    df["fin"] = pd.to_datetime(df["fin"])
    df["ligne"] = df["ligne"].str.strip()

    # Un incident = au moins une période en perturbation (PB) ou blocage (BQ).
    # Un même incident peut passer de BQ à PB : il garde le même id_incident.
    incidents = df[df["statut"].isin(["PB", "BQ"])].copy()
    incidents["heures"] = (incidents["fin"] - incidents["debut"]).dt.total_seconds() / 3600
    return df, incidents


def voyageurs_affectes_par_ligne(incidents, stations, moyennes, zones):
    # Validations moyennes par jour de chaque zone (id_zdc)
    validations_zone = moyennes.groupby(zones).sum()

    stations = stations.copy()
    stations["validations"] = stations["id_ref_zdc"].map(validations_zone).fillna(0)
    # Une gare desservie par plusieurs lignes (Châtelet...) : ses validations sont réparties entre elles.
    stations["validations"] = stations["validations"] / stations.groupby("id_ref_zdc")["ligne"].transform("count")

    voyageurs = pd.DataFrame({
        "voyageurs_par_jour": stations.groupby("ligne")["validations"].sum(),
        "jours_incident": incidents.groupby("ligne")["jour"].nunique(),
        "nb_incidents": incidents.groupby("ligne")["id_incident"].nunique(),
        "heures_incident": incidents.groupby("ligne")["heures"].sum(),
    }).dropna()
    # Voyageurs présents pendant les incidents, en supposant le trafic réparti sur 20 h de service.
    voyageurs["voyageurs_affectes"] = voyageurs["voyageurs_par_jour"] * voyageurs["heures_incident"] / 20
    return voyageurs.sort_values("voyageurs_affectes", ascending=False)


def ordre_ligne(ligne):
    # "Métro 2" avant "Métro 10"
    nombre = re.search(r"\d+", ligne)
    return (re.sub(r"\d.*", "", ligne), int(nombre.group()) if nombre else 0, ligne)


def incidents_par_jour_et_ligne(incidents, annee):
    # Nombre d'incidents distincts par ligne (lignes) et par jour (colonnes), jours sans incident à 0
    tableau = incidents.pivot_table(index="ligne", columns="jour", values="id_incident", aggfunc="nunique", fill_value=0)
    jours = pd.date_range(f"{annee}-01-01", f"{annee}-12-31")
    return tableau.reindex(index=sorted(tableau.index, key=ordre_ligne), columns=jours, fill_value=0)


def tracer_carte_incidents_animee(incidents, annee):
    # Une image par jour (365 frames) : bouton "play" ou curseur pour avancer dans l'année
    tableau = incidents_par_jour_et_ligne(incidents, annee)
    par_jour = tableau.melt(ignore_index=False, var_name="jour", value_name="incidents").reset_index()
    par_jour["jour"] = par_jour["jour"].dt.strftime("%d/%m/%Y")

    fig = px.bar(
        par_jour,
        x="ligne",
        y="incidents",
        animation_frame="jour",
        range_y=[0, par_jour["incidents"].max()],
        color_discrete_sequence=["#d62728"],
        labels={"ligne": "Ligne", "incidents": "Nombre d'incidents", "jour": "Jour"},
        title="Incidents par ligne, jour par jour - " + str(annee),
    )
    fig.show()


def tracer_heatmap_incidents(incidents, annee):
    tableau = incidents_par_jour_et_ligne(incidents, annee)

    fig = px.imshow(
        tableau,
        aspect="auto",
        color_continuous_scale="YlOrRd",
        labels={"x": "Jour", "y": "Ligne", "color": "Incidents"},
        title="Incidents par ligne et par jour - " + str(annee),
        height=900,
    )
    fig.show()


def tracer_voyageurs_affectes(voyageurs, n):
    top = voyageurs.head(n).rename_axis("ligne").reset_index()
    fig = px.scatter(
        top,
        x="nb_incidents",
        y="voyageurs_affectes",
        size="voyageurs_par_jour",
        color="voyageurs_affectes",
        text="ligne",
        hover_data=["jours_incident", "heures_incident"],
        labels={
            "nb_incidents": "Nombre d'incidents dans l'année",
            "voyageurs_affectes": "Voyageurs affectés estimés",
            "voyageurs_par_jour": "Voyageurs par jour",
            "jours_incident": "Jours avec incident",
            "heures_incident": "Heures d'incident",
        },
        title="Lignes où les incidents touchent le plus de voyageurs (taille = voyageurs par jour)",
    )
    fig.update_traces(textposition="top center")
    fig.show()


if __name__ == "__main__":
    df, incidents = charger_incidents()
    par_ligne = incidents.groupby("ligne")["jour"].unique()
    jours_incident = {ligne: sorted(par_ligne.get(ligne, [])) for ligne in df["ligne"].unique()}
    print(incidents.groupby("ligne")["id_incident"].nunique().sort_values(ascending=False).head(10))
