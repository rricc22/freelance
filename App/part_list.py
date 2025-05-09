import streamlit as st
import os
from PIL import Image

# --- Titre ---
st.title("🧩 Analyse dimensionnelle - Rapport avec Schéma Type")

# --- Sélection du type de pièce ---
st.sidebar.header("📂 Paramètres")
piece_type = st.sidebar.selectbox("Type de pièce :", ["Support de palier", "Roue", "Distributeur", "Nozzle", "Corps"])

# --- Mapping nom -> fichier image ---
schema_map = {
    "Support de palier": "support_palier.png",
    "Roue": "roue.png",
    "Distributeur": "distributeur.png",
    "Nozzle": "nozzle.png",
    "Corps": "corps.png"
}

# --- Chargement de l'image ---
image_folder = "images/schemas_types"
schema_filename = schema_map[piece_type]
schema_path = os.path.join(image_folder, schema_filename)

# --- Affichage ---
st.subheader(f"🖼️ Schéma type pour : {piece_type}")
if os.path.exists(schema_path):
    image = Image.open(schema_path)
    st.image(image, caption=f"Schéma type - {piece_type}", use_column_width=True)
else:
    st.error(f"❌ Le fichier {schema_path} est introuvable.")

# --- Optionnel : données fictives associées ---
st.markdown("---")
st.subheader("📏 Exemple de tableau dimensionnel")
st.write("Voici un exemple simplifié lié à ce type de pièce :")

import pandas as pd

df_ex = pd.DataFrame({
    "Nom_Cote": ["A", "B", "C"],
    "Valeur mesurée (mm)": [24.95, 10.02, 45.10],
    "Tolérance -": [0.1, 0.05, 0.2],
    "Tolérance +": [0.1, 0.05, 0.2]
})

st.dataframe(df_ex, use_container_width=True)
