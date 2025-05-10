import streamlit as st
import pandas as pd
from io import StringIO

# --- CONFIG ---
st.set_page_config(page_title="Comparaison", layout="wide")
st.title("📊 Comparaison des Données")

# --- MAIN ---
st.subheader("📋 Coller les données CSV depuis Excel")
text_input = st.text_area("Collez ici les données copiées depuis Excel", height=300)

if text_input:
    try:
        df = pd.read_csv(StringIO(text_input), sep="\t")

        # Vérification des colonnes attendues
        expected_cols = ["Date", "Serial", "OF", "Cote", "Nom_Cote", "Mesure_Theorique", "Tolérance_Min", "Tolérance_Max"]
        if not all(col in df.columns for col in expected_cols):
            st.error(f"Colonnes attendues : {expected_cols}. Colonnes détectées : {df.columns.tolist()}")
        else:
            # Nettoyage des valeurs de cote (virgule à point si besoin)
            df["Cote"] = df["Cote"].astype(str).str.replace(",", ".").astype(float)

            # Calculs élémentaires
            df["Écart (mm)"] = df["Mesure_Theorique"] - df["Cote"]
            df["Écart (%)"] = 100 * df["Écart (mm)"] / df["Cote"]
            df["Hors tolérance"] = ~df["Mesure_Theorique"].between(df["Tolérance_Min"], df["Tolérance_Max"])

            st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.error(f"Erreur de lecture des données : {e}")
else:
    st.info("Veuillez copier-coller les données depuis Excel avec les colonnes correctes.")