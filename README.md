# TADD
## Analyse de données

### Projet d'Analyse de données

* Corrélation du tourisme et du scan des pass Navigo, tickets et titres de transport.
* Corrélation de l'impact des pannes sur la masse d'usagers.
* Corrélation de la répartition des ménages les plus pauvres et la masse dans les trains.

### Structure du projet

```text
README.md
├── requirements.txt
├── main.py
├── Navigo_validations_cleaning.py
├── Retard_Incidents_IDFM_cleaning.py
├── Réseau_IDFM_cleaning.py
├── Tourisme_Insee_cleaning.py
├── Revenus_pauvreté_Insee_cleaning.py
└── Localisaiton_communes.py
```

### Descriptions et sources des scripts

* **`README.md`** : Fichier de la structure du projet et de ses sources API.
* **`requirements.txt`** : Prérequis Python pour exécuter les scripts (`pandas` et `plotly`).
* **`Navigo_validations_cleaning.py`** : Historique des validations des Navigo dans les stations ($A_i$).
  * [API Validation journalière par arrêt par titre](https://data.iledefrance-mobilites.fr/api/explore/v2.1/catalog/datasets/validations-reseau-ferre-nombre-validations-par-jour-2eme-trimestre/records?limit=100)
  * [API Validation horaire](https://data.iledefrance-mobilites.fr/api/explore/v2.1/catalog/datasets/validations-sur-le-reseau-ferre-profils-horaires-par-jour-type-2eme-trimestre/records?limit=100)
  * [API Archive](https://data.iledefrance-mobilites.fr/api/explore/v2.1/catalog/datasets/histo-validations-reseau-ferre/records?limit=100)

* **`Retard_Incidents_IDFM_cleaning.py`** : Historique des incidents par ligne ($B_i$) et voyageurs affectés.
  * [Incidents RATP par jour (ratpstatus.fr)](https://ratpstatus.fr/20250115/timeline.csv) : une copie locale `incidents_2025.csv` est créée au premier lancement.
  * [Retard API CSV](https://ressources.data.sncf.com/api/explore/v2.1/catalog/datasets/ponctualite-mensuelle-transilien/exports/csv)
  * [API](https://prim.iledefrance-mobilites.fr/marketplace/v2/navitia/line_reports/line_reports?count=100&start_page=0)

* **`Réseau_IDFM_cleaning.py`** : Données des stations ($A_i$) et lignes de transports ($B_i$).
  * [Arrêt API](https://data.iledefrance-mobilites.fr/api/explore/v2.1/catalog/datasets/arrets/records?limit=100)
  * [Lignes API](https://data.iledefrance-mobilites.fr/api/explore/v2.1/catalog/datasets/referentiel-des-lignes/records?limit=100)
  * [Gares par ligne API](https://data.iledefrance-mobilites.fr/api/explore/v2.1/catalog/datasets/emplacement-des-gares-idf/records?limit=100) : `id_ref_zdc` = `id_zdc` des validations.

* **`Tourisme_Insee_cleaning.py`** : Données du tourisme par nuitée d'hôtel à Paris.
  * [API](https://bdm.insee.fr/series/sdmx/data/SERIES_BDM/010598705?startPeriod=2022-01)
  * *À lier avec la localisation des stations pour évaluer les stations empruntées par les touristes.*

* **`Revenus_pauvreté_Insee_cleaning.py`** : Données des foyers à bas revenus localisés.
  * [API](https://api.insee.fr/melodi)

* **`Localisaiton_communes.py`** : Données de la géographie des communes (utiles pour savoir si les habitants de la ville $X$ ne sont pas plus proches d'une station de la ville $Y$).
  * [Liste commune IDF API](https://geo.api.gouv.fr/communes?codeRegion=11&fields=nom,code,codeDepartement,population,centre&format=json)
  * [Communes contours géo API](https://geo.api.gouv.fr/communes?codeRegion=11&fields=nom,code,population&format=geojson&geometry=contour)
  * [Coordonnées GPS communes API](https://geo.api.gouv.fr/communes?lat=48.85&lon=2.35&fields=nom,code,population)

### Installation et utilisation

```bash
python -m pip install -r requirements.txt
```
### Graphiques Utiles

Les graphiques sont générés avec Plotly par `main.py` :

```bash
python main.py
```

* barres des stations les plus fréquentées ;
* profil horaire de la station la plus fréquentée (jour ouvré) ;
* animation de 365 frames, une par jour, des incidents par ligne ;
* heatmap des incidents par ligne et par jour ;
* nuage de bulles des voyageurs affectés selon le nombre d'incidents.

Nuages de point pour les pics de validation/station dans les les zones de pauvereté
Un graphique de distribution pour la présence de touriste dans les stations de métro/train
Un partitionage des lignes fréquenté par la masse pauvre
Un sous partitionage de la ligne et de ses stations les plus fréquenté par la masse pauvre