from PIL import Image

# Ouvrir l'image
logo = Image.open("logo_tds.jpg")

# Redimensionner : largeur = 100 px, hauteur ajustée automatiquement pour garder les proportions
largeur = 100
hauteur = int((largeur / logo.width) * logo.height)
logo_redim = logo.resize((largeur, hauteur), Image.Resampling.LANCZOS)

# Sauvegarder le logo redimensionné
logo_redim.save("logo_tds_small.jpg")
print("✅ Logo redimensionné et sauvegardé sous 'logo_tds_small.jpg'")
