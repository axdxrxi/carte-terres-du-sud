from scipy.spatial import cKDTree
import pandas as pd
import numpy as np
from geopy.distance import geodesic

# Chargement des fichiers
ps_df = pd.read_csv("ps.csv", sep=';', encoding='latin1')
sites_df = pd.read_csv("sites.csv", sep=';', encoding='latin1')

# Nettoyage des données
ps_df = ps_df.dropna(subset=['Latitude', 'Longitude'])
sites_df = sites_df.dropna(subset=['Latitude', 'Longitude'])

ps_df['Latitude'] = pd.to_numeric(ps_df['Latitude'], errors='coerce')
ps_df['Longitude'] = pd.to_numeric(ps_df['Longitude'], errors='coerce')
sites_df['Latitude'] = pd.to_numeric(sites_df['Latitude'], errors='coerce')
sites_df['Longitude'] = pd.to_numeric(sites_df['Longitude'], errors='coerce')

ps_df = ps_df[np.isfinite(ps_df['Latitude']) & np.isfinite(ps_df['Longitude'])]
sites_df = sites_df[np.isfinite(sites_df['Latitude']) & np.isfinite(sites_df['Longitude'])]

# Vérification
print(f"\n{len(ps_df)} points de service valides")
print(f"{len(sites_df)} sites valides")

# Conversion en coordonnées
ps_coords = ps_df[["Latitude", "Longitude"]].to_numpy()
sites_coords = sites_df[["Latitude", "Longitude"]].to_numpy()

# Calcul des distances
ps_tree = cKDTree(ps_coords)
distances, indices = ps_tree.query(sites_coords, k=1)

# Résultats
sites_df["PS_plus_proche"] = ps_df.iloc[indices]["Nom Commune"].values
sites_df["Distance_km"] = [geodesic(site, ps).km for site, ps in zip(sites_coords, ps_coords[indices])]

print(sites_df[["Ville", "PS_plus_proche", "Distance_km"]].to_string(index=False))
