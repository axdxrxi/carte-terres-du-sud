import pandas as pd
from math import radians, sin, cos, sqrt, atan2

# --- Fonction pour calculer la distance (Haversine) ---
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # rayon Terre en km
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

# --- Fonction pour lire un CSV en détectant le séparateur ---
def read_csv_auto(path):
    with open(path, 'r', encoding='utf-8') as f:
        first_line = f.readline()
        if '\t' in first_line:
            sep = '\t'
        elif ';' in first_line:
            sep = ';'
        else:
            sep = ','
    df = pd.read_csv(path, encoding='utf-8', sep=sep)
    df.columns = df.columns.str.strip()  # enlever espaces début/fin
    return df

# --- Lecture des CSV ---
sites_df = read_csv_auto("sites_ps.csv")
ps_df = read_csv_auto("ps.csv")

print("Colonnes sites_ps.csv :", list(sites_df.columns))
print("Colonnes ps.csv :", list(ps_df.columns))

# --- Colonnes de sortie ---
sites_df["PS_latitude"] = None
sites_df["PS_longitude"] = None
sites_df["Distance_calculee_km"] = None

# --- Boucle sur chaque site ---
for idx, site in sites_df.iterrows():
    ps_nom = str(site["PS_plus_proche"]).strip()
    site_lat = float(site["Latitude"])
    site_lon = float(site["Longitude"])
    dist_attendue = float(site["Distance_km"])
    
    # Filtrer les postes sources du même nom
    candidats = ps_df[ps_df["Nom Commune"].astype(str).str.strip() == ps_nom]
    
    meilleur_candidat = None
    diff_min = float("inf")
    
    for _, ps in candidats.iterrows():
        dist_calc = haversine(site_lat, site_lon, float(ps["Latitude"]), float(ps["Longitude"]))
        diff = abs(dist_calc - dist_attendue)
        
        if diff < diff_min:
            diff_min = diff
            meilleur_candidat = ps
            meilleure_distance = dist_calc
    
    # Remplissage
    if meilleur_candidat is not None:
        sites_df.at[idx, "PS_latitude"] = meilleur_candidat["Latitude"]
        sites_df.at[idx, "PS_longitude"] = meilleur_candidat["Longitude"]
        sites_df.at[idx, "Distance_calculee_km"] = round(meilleure_distance, 3)

# --- Sauvegarde ---
sites_df.to_csv("sites_ps_avec_coordonnees.csv", index=False, encoding="utf-8")
print("✅ Fichier 'sites_ps_avec_coordonnees.csv' créé avec succès.")
