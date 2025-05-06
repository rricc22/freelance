import streamlit as st
import pandas as pd
import os

# --- CONFIG ---
st.set_page_config(page_title="Étude dimensionnelle", layout="wide")
st.title("📏 Dashboard d'Étude Dimensionnelle")

# --- SIDEBAR ---
st.sidebar.header("📂 Import des données")
uploaded_file = st.sidebar.file_uploader("Choisissez un fichier CSV", type=["csv"])

image_folder = st.sidebar.text_input("Dossier des vues CAO (images)", "images/")

# --- MAIN LOGIC ---
if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Vérification des colonnes nécessaires
    expected_cols = ["item", "cote_nom", "cote_rdm"]
    if not all(col in df.columns for col in expected_cols):
        st.error("Le fichier doit contenir les colonnes : item, cote_nom, cote_rdm")
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

else:
    st.info("Veuillez importer un fichier CSV contenant les données dimensionnelles.")
