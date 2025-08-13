import pandas as pd

# Lis le fichier CSV avec le bon séparateur
df = pd.read_csv("sites.csv", sep=';', encoding='utf-8-sig')
df.columns = df.columns.str.strip()

# Affiche les colonnes et les 3 premières lignes pour debug
print("Colonnes détectées :", df.columns.tolist())
print(df.head(3))

# Essaie de lire une seule ville
for i, row in df.iterrows():
    try:
        ville = str(row['Ville']).strip()
        lat = float(str(row['Latitude']).strip().replace(',', '.'))
        lon = float(str(row['Longitude']).strip().replace(',', '.'))
        print(f"✅ Coordonnées extraites : {ville} ({lat}, {lon})")
    except Exception as e:
        print(f"❌ Erreur à la ligne {i+2} : {e}")
    break  # juste un test avec la 1ère ligne
