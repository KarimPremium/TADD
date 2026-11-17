import pandas as pd

jours = pd.date_range("2025-01-01", "2025-12-31")
frames = []
for j in jours:
    url = f"https://ratpstatus.fr/{j:%Y%m%d}/timeline.csv"
    try:
        d = pd.read_csv(url, sep=";", skiprows=1, header=None,
                        engine="python", on_bad_lines=lambda r: r[:8])
        frames.append(d.iloc[:, :6])
    except Exception:
        pass  # jour manquant

df = pd.concat(frames)
df.columns = ["jour", "mode", "ligne", "debut", "fin", "statut"]

# Un incident = au moins une période en perturbation (PB) ou blocage (BQ)
incidents = df[df["statut"].isin(["PB", "BQ"])]
par_ligne = incidents.groupby("ligne")["jour"].unique()

jours_incident = {ligne: sorted(par_ligne.get(ligne, []))
                  for ligne in df["ligne"].unique()}

print(par_ligne.head(10))