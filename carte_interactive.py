import pandas as pd
import folium
from folium.plugins import MarkerCluster
import webbrowser

# === 1. CHEMINS DES FICHIERS CSV ===
csv_sites_path = "C:/Analyse_surfacique/sites.csv"
csv_sites_ps_path = "C:/Analyse_surfacique/sites_ps.csv"
csv_ps_path = "C:/Analyse_surfacique/ps.csv"

# === 2. CHARGEMENT DES DONNÉES ===
df_sites = pd.read_csv(csv_sites_path, sep=";", encoding="latin1")
df_sites_ps = pd.read_csv(csv_sites_ps_path, sep=";", encoding="latin1")
df_ps = pd.read_csv(csv_ps_path, sep=";", encoding="latin1")

# === 3. NETTOYAGE DES DONNÉES ===
df_sites = df_sites.dropna(subset=["Latitude", "Longitude"])
df_ps = df_ps.dropna(subset=["Latitude", "Longitude"])
df_sites_ps = df_sites_ps.dropna(subset=["PS_plus_proche", "Distance_km"])

# === 4. JOINTURE coordonnées postes sources ===
df_sites_ps = pd.merge(
    df_sites_ps,
    df_ps[["Nom Commune", "Latitude", "Longitude"]],
    left_on="PS_plus_proche",
    right_on="Nom Commune",
    how="left"
).rename(columns={"Latitude": "Lat_PS", "Longitude": "Lon_PS"})

# === 5. JOINTURE coordonnées sites ===
df_sites_ps = pd.merge(
    df_sites_ps,
    df_sites[["Ville", "Latitude", "Longitude"]],
    left_on="Site",
    right_on="Ville",
    how="left"
).rename(columns={"Latitude": "Lat_Site", "Longitude": "Lon_Site"})

# === 6. Garder le poste source le plus proche par site
df_sites_ps = df_sites_ps.sort_values("Distance_km").drop_duplicates(subset=["Site"], keep="first")

# === 7. Identifier les postes sources en doublon de nom
duplicated_postes_villes = df_sites_ps["PS_plus_proche"][df_sites_ps["PS_plus_proche"].duplicated(keep=False)]

# === 8. CENTRE DE LA CARTE ===
mean_lat = df_sites["Latitude"].mean()
mean_lon = df_sites["Longitude"].mean()
m = folium.Map(location=[mean_lat, mean_lon], zoom_start=8)

# === 9. MARQUEURS DES SITES (bleu) ===
marker_cluster_sites = MarkerCluster(name="Sites").add_to(m)
for _, site_row in df_sites.iterrows():
    site_name = site_row["Ville"]
    lat = site_row["Latitude"]
    lon = site_row["Longitude"]

    match = df_sites_ps[df_sites_ps["Site"] == site_name]
    if not match.empty:
        match_row = match.iloc[0]
        popup_html = f"""
        <b>Nom du site :</b> {site_name}<br>
        <b>Poste source le plus proche :</b> {match_row['PS_plus_proche']}<br>
        <b>Distance :</b> {match_row['Distance_km']} km
        """
    else:
        popup_html = f"<b>Nom du site :</b> {site_name}"

    folium.Marker(
        location=[lat, lon],
        popup=folium.Popup(popup_html, max_width=300),
        tooltip=site_name,
        icon=folium.Icon(color="blue", icon="info-sign")
    ).add_to(marker_cluster_sites)

# === 10. MARQUEURS DES POSTES SOURCES (rouge ou orange) ===
marker_cluster_postes = MarkerCluster(name="Postes sources").add_to(m)
grouped_postes = df_sites_ps.groupby("PS_plus_proche")
df_unique_postes = df_sites_ps.drop_duplicates(subset=["PS_plus_proche"])

for _, row in df_unique_postes.iterrows():
    if pd.notna(row["Lat_PS"]) and pd.notna(row["Lon_PS"]):
        poste_nom = row["PS_plus_proche"]
        sites_lies = grouped_postes.get_group(poste_nom)["Site"].unique()
        sites_str = "<br>".join(sites_lies)
        color = "orange" if poste_nom in duplicated_postes_villes.values else "red"

        popup_html = f"""
        <b>Poste source :</b> {poste_nom}<br>
        <b>Sites liés :</b><br>{sites_str}
        """
        folium.Marker(
            location=[row["Lat_PS"], row["Lon_PS"]],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"{poste_nom} ({len(sites_lies)} site(s))",
            icon=folium.Icon(color=color, icon="star")
        ).add_to(marker_cluster_postes)

# === 11. CONTRÔLE DE COUCHES ===
folium.LayerControl().add_to(m)

# === 12. EXPORTATION ET CORRECTION DU FICHIER HTML ===
output_path = "C:/Analyse_surfacique/carte_terres_du_sud.html"
m.save(output_path)

# 🧽 Correction de l'encodage pour les accents
with open(output_path, "r", encoding="utf-8", errors="replace") as f:
    content = f.read()

if "<meta charset=" not in content:
    content = content.replace("<head>", "<head>\n<meta charset='UTF-8'>", 1)

with open(output_path, "w", encoding="utf-8") as f:
    f.write(content)

# OUVERTURE DE LA CARTE
print(f"✅ Carte sauvegardée : {output_path}")
webbrowser.open(output_path)
