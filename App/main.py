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
text_input = st.text_area("Collez ici les données copiées depuis Excel", height=300)

if text_input:
    try:
        df = pd.read_csv(StringIO(text_input), sep="\t")

        expected_cols = ["Datetime", "Serial", "OF", "Cote", "Mesure_Theorique", "Tolérance_Min", "Tolérance_Max"]
        if not all(col in df.columns for col in expected_cols):
            st.error(f"Les colonnes attendues sont : {expected_cols}. Colonnes détectées : {df.columns.tolist()}")
        else:
            # Nettoyage éventuel des virgules en float
            df["Cote"] = df["Cote"].astype(str).str.replace(",", ".").astype(float)

            # Calculs
            df["Écart (mm)"] = df["Mesure_Theorique"] - df["Cote"]
            df["Écart (%)"] = 100 * df["Écart (mm)"] / df["Cote"]
            df["Out of Tolérance"] = ~df["Mesure_Theorique"].between(df["Tolérance_Min"], df["Tolérance_Max"])

            # --- DISPLAY ---
            st.subheader("📊 Résultats des mesures")
            selected_of = st.selectbox("Sélectionnez un OF :", df["OF"].astype(str).unique())

            filtered_df = df[df["OF"].astype(str) == selected_of]
            st.dataframe(filtered_df, use_container_width=True)

            # --- IMAGE ---
            st.subheader("🖼️ Vue CAO associée")
            image_path = os.path.join(image_folder, f"{selected_of}.png")
            if os.path.exists(image_path):
                st.image(image_path, caption=f"Vue CAO de l'OF {selected_of}", use_column_width=True)
            else:
                st.warning(f"Image non trouvée pour l'OF {selected_of} dans {image_folder}")
    except Exception as e:
        st.error(f"Erreur de lecture des données : {e}")
else:
    st.info("Veuillez copier-coller les données depuis Excel avec les colonnes correctes.")
