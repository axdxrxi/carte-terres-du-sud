from scipy.spatial import cKDTree
import pandas as pd
import numpy as np
from geopy.distance import geodesic

# Chargement des fichiers avec gestion du BOM et détection du séparateur
ps_df = pd.read_csv("ps.csv", sep=None, engine="python", encoding='utf-8-sig')
sites_df = pd.read_csv("sites.csv", sep=None, engine="python", encoding='utf-8-sig')

# Nettoyage des noms de colonnes
ps_df.columns = ps_df.columns.str.strip()
sites_df.columns = sites_df.columns.str.strip()

# Conversion coordonnées en numérique et suppression lignes invalides
for df in [ps_df, sites_df]:
    df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
    df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
    df.dropna(subset=['Latitude', 'Longitude'], inplace=True)

# Vérification
print(f"\n{len(ps_df)} points de service valides")
print(f"{len(sites_df)} sites valides")
print("Colonnes PS :", ps_df.columns.tolist())
print("Colonnes Sites :", sites_df.columns.tolist())

# Coordonnées
ps_coords = ps_df[["Latitude", "Longitude"]].to_numpy()
sites_coords = sites_df[["Latitude", "Longitude"]].to_numpy()

# Recherche du PS le plus proche
ps_tree = cKDTree(ps_coords)
distances, indices = ps_tree.query(sites_coords, k=1)

# Résultats
sites_df["PS_plus_proche"] = ps_df.iloc[indices]["Nom Commune"].values
sites_df["Distance_km"] = [
    geodesic(site, ps).km
    for site, ps in zip(sites_coords, ps_coords[indices])
]

# Affichage final
print(sites_df[["Ville", "PS_plus_proche", "Distance_km"]].to_string(index=False))
