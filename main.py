from Navigo_validations_cleaning import (
    charger_donnees_validations,
    top_stations_par_validation,
    tracer_top_stations,
    tracer_profil_station,
)
from Retard_Incidents_IDFM_cleaning import (
    charger_incidents,
    voyageurs_affectes_par_ligne,
    tracer_carte_incidents_animee,
    tracer_heatmap_incidents,
    tracer_voyageurs_affectes,
)
from Réseau_IDFM_cleaning import charger_stations

annee = 2025

noms, dates, stations_jour, stations_heure, zones = charger_donnees_validations()
top = top_stations_par_validation(stations_jour, dates)

df, incidents = charger_incidents(annee)
stations = charger_stations()

# Corrélation incidents / masse d'usagers, ligne par ligne
voyageurs = voyageurs_affectes_par_ligne(incidents, stations, top, zones)
print(voyageurs.head(10).round())

tracer_top_stations(top, 10)
tracer_profil_station(stations_heure.loc[top.index[0]], top.index[0])
tracer_carte_incidents_animee(incidents, annee)
tracer_heatmap_incidents(incidents, annee)
tracer_voyageurs_affectes(voyageurs, 15)
