import pandas as pd
import folium
import sys
from folium.plugins import FloatImage

# Nom du fichier CSV
fichier_csv = "sites_ps.csv"

# Charger le CSV avec séparateur ;
try:
    df = pd.read_csv(fichier_csv, sep=";")
except FileNotFoundError:
    print(f"❌ Fichier '{fichier_csv}' introuvable dans ce dossier.")
    sys.exit(1)

# Nettoyage des noms de colonnes : suppression espaces, mise en minuscules
df.columns = df.columns.str.strip().str.replace(" ", "_").str.lower()

# Vérification des colonnes nécessaires
colonnes_attendues = [
    "site", "latitude", "longitude",
    "ps_plus_proche", "ps_latitude", "ps_longitude", "distance_km"
]
for col in colonnes_attendues:
    if col not in df.columns:
        print(f"❌ Colonne manquante dans le CSV : '{col}'")
        print("Colonnes disponibles :", df.columns.tolist())
        sys.exit(1)

# Supprimer les lignes avec coordonnées manquantes
df = df.dropna(subset=["latitude", "longitude", "ps_latitude", "ps_longitude"])

# --- Création de la carte sans centrer pour l'instant ---
carte = folium.Map(zoom_start=8)

# Ajouter le logo en haut à droite
FloatImage("logo_tds_small.jpg", bottom=80, left=92).add_to(carte)

# --- FeatureGroups pour pouvoir les activer/désactiver ---
fg_postes = folium.FeatureGroup(name="Postes Sources", show=True)
fg_sites = folium.FeatureGroup(name="Sites", show=True)

# Liste unique des postes sources
postes_sources = df[["ps_plus_proche", "ps_latitude", "ps_longitude"]].drop_duplicates()

# --- Ajouter les postes sources en bleu ---
for _, row in postes_sources.iterrows():
    ps_nom = row["ps_plus_proche"]
    ps_lat = row["ps_latitude"]
    ps_lon = row["ps_longitude"]

    sites_reliés = df[df["ps_plus_proche"] == ps_nom]
    noms_sites = ", ".join(sites_reliés["site"].tolist())
    nb_sites = len(sites_reliés)

    popup_ps = folium.Popup(
        f"<b>Poste source :</b> {ps_nom}<br>"
        f"<b>Sites reliés :</b> {noms_sites}<br>"
        f"<b>Nombre de sites :</b> {nb_sites}",
        max_width=300
    )

    folium.Marker(
        location=[ps_lat, ps_lon],
        popup=popup_ps,
        icon=folium.Icon(color="blue", icon="bolt", prefix="fa")
    ).add_to(fg_postes)

# --- Ajouter les sites en vert + lignes ---
for _, row in df.iterrows():
    site_nom = row["site"]
    site_lat = row["latitude"]
    site_lon = row["longitude"]
    ps_nom = row["ps_plus_proche"]
    ps_lat = row["ps_latitude"]
    ps_lon = row["ps_longitude"]
    distance_km = row["distance_km"]

    popup_site = folium.Popup(
        f"<b>Site :</b> {site_nom}<br>"
        f"<b>Poste source relié :</b> {ps_nom}<br>"
        f"<b>Distance :</b> {distance_km} km",
        max_width=300
    )

    folium.Marker(
        location=[site_lat, site_lon],
        popup=popup_site,
        icon=folium.Icon(color="green", icon="map-marker", prefix="fa")
    ).add_to(fg_sites)

    # Ligne entre site et poste source
    folium.PolyLine(
        locations=[(site_lat, site_lon), (ps_lat, ps_lon)],
        color="gray",
        weight=2,
        opacity=0.7
    ).add_to(fg_sites)

# Ajouter les FeatureGroups à la carte
fg_postes.add_to(carte)
fg_sites.add_to(carte)

# --- Contrôle des calques avec titre personnalisé en bas à gauche ---
folium.LayerControl(
    position="bottomleft",
    collapsed=False,
    autoZIndex=True
).add_to(carte)

# --- Zoom automatique pour inclure tous les points (sites + postes sources) ---
all_coords = pd.concat([
    df[["latitude", "longitude"]],
    df[["ps_latitude", "ps_longitude"]].rename(columns={"ps_latitude":"latitude","ps_longitude":"longitude"})
])
carte.fit_bounds(all_coords[["latitude", "longitude"]].values.tolist())

# Sauvegarde de la carte
carte.save("index.html")
print("✅ Carte générée : 'index.html' avec zoom automatique et LayerControl")
