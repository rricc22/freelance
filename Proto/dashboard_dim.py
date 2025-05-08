import streamlit as st
import pandas as pd
import os
from io import StringIO

# --- CONFIG ---
st.set_page_config(page_title="Étude dimensionnelle", layout="wide")
st.title("📏 Dashboard d'Étude Dimensionnelle")

# --- SIDEBAR ---
st.sidebar.header("📂 Options")
image_folder = st.sidebar.text_input("Dossier des vues CAO (images)", "images/")

# --- MAIN ---
st.subheader("📋 Coller les données CSV depuis Excel")
text_input = st.text_area("Collez ici les données copiées depuis Excel (colonnes: item, cote_nom, cote_rdm)", height=300)

if text_input:
    try:
        # Lecture via StringIO
        df = pd.read_csv(StringIO(text_input), sep="[\t,;]", engine="python")

        expected_cols = ["item", "cote_nom", "cote_rdm"]
        if not all(col in df.columns for col in expected_cols):
            st.error("Les colonnes attendues sont : item, cote_nom, cote_rdm")
        else:
            df["écart (%)"] = 100 * (df["cote_rdm"] - df["cote_nom"]) / df["cote_nom"]

            # --- DISPLAY TABLE ---
            st.subheader("📊 Tableau des écarts dimensionnels")
            selected_item = st.selectbox("Sélectionnez un item :", df["item"].astype(str).unique())

            filtered_df = df[df["item"].astype(str) == selected_item]
            st.dataframe(filtered_df, use_container_width=True)

            # --- DISPLAY IMAGE ---
            st.subheader("🖼️ Vue CAO associée")
            image_path = os.path.join(image_folder, f"{selected_item}.png")

            if os.path.exists(image_path):
                st.image(image_path, caption=f"Vue CAO de l'item {selected_item}", use_column_width=True)
            else:
                st.warning(f"Image non trouvée pour l'item {selected_item} dans {image_folder}")
    except Exception as e:
        st.error(f"Erreur de lecture des données : {e}")
else:
    st.info("Veuillez copier-coller les données depuis Excel.")
