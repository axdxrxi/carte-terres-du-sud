import pandas as pd
import os
import matplotlib.pyplot as plt
from pvlib.iotools import get_pvgis_tmy

# --- Chargement CSV avec séparateur ; ---
csv_path = 'sites.csv'
df = pd.read_csv(csv_path, sep=';', encoding='utf-8-sig')
df.columns = df.columns.str.strip()  # retire espaces autour des noms colonnes

# Vérification colonnes obligatoires
for col in ['Ville', 'Latitude', 'Longitude']:
    if col not in df.columns:
        raise KeyError(f"La colonne obligatoire '{col}' est absente du fichier CSV.")

os.makedirs("graph_ghi", exist_ok=True)

resultats = []
moyennes = []

for idx, row in df.iterrows():
    site_nom = str(row['Ville']).strip()
    try:
        lat = float(str(row['Latitude']).strip().replace(',', '.'))
        lon = float(str(row['Longitude']).strip().replace(',', '.'))
    except Exception as e:
        print(f"⚠️ Coordonnées invalides pour '{site_nom}': {e}")
        continue

    # Skip si lat ou lon manquantes
    if pd.isna(lat) or pd.isna(lon):
        print(f"⚠️ Coordonnées manquantes pour '{site_nom}', passage à la suivante.")
        continue

    print(f"🔍 Récupération PVGIS pour : {site_nom} (lat={lat}, lon={lon})")

    try:
        tmy, meta = get_pvgis_tmy(latitude=lat, longitude=lon, outputformat='json')
    except Exception as e:
        print(f"⚠️ Erreur PVGIS pour '{site_nom}' : {e}")
        continue

    if 'G(h)' not in tmy.columns:
        print(f"⚠️ Données 'G(h)' absentes pour '{site_nom}'")
        continue

    ghi = tmy['G(h)']

    df_result = pd.DataFrame({
        'Date': ghi.index,
        'GHI (kWh/m²/jour)': ghi.values,
        'Site': site_nom
    })
    moyenne = ghi.mean()
    df_result['Moyenne Annuelle'] = moyenne

    moyennes.append({'Site': site_nom, 'Moyenne GHI': round(moyenne, 2)})
    resultats.append(df_result)

    # Graphique
    plt.figure(figsize=(10, 4))
    plt.plot(df_result['Date'], df_result['GHI (kWh/m²/jour)'], color='orange')
    plt.title(f'Irradiation journalière – {site_nom}')
    plt.xlabel('Date')
    plt.ylabel('GHI (kWh/m²/jour)')
    plt.grid(True)
    plt.tight_layout()

    safe_name = site_nom.replace(' ', '_').replace('(', '').replace(')', '').replace("'", "")
    plt.savefig(f"graph_ghi/{safe_name}_ghi.png")
    plt.close()

if resultats:
    final_df = pd.concat(resultats, ignore_index=True)
    final_df.to_csv('resultats_ensoleillement.csv', index=False)
    pd.DataFrame(moyennes).to_csv('moyennes_annuelles_ghi.csv', index=False)
    print("✅ Traitement terminé, fichiers générés.")
else:
    print("❌ Aucun résultat obtenu, vérifie les données et les erreurs.")
