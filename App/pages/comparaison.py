import streamlit as st
import pandas as pd
from io import StringIO

# --- CONFIG ---
st.set_page_config(page_title="Comparaison", layout="wide")
st.title("📊 Comparaison des Données")

# --- LAYOUT ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("📋 Données pour Métal")
    metal_text_input = st.text_area("Collez ici les données pour Métal copiées depuis Excel", height=300, key="metal")

with col2:
    st.subheader("📋 Données pour Cote Cire")
    cire_text_input = st.text_area("Collez ici les données pour Cote Cire copiées depuis Excel", height=300, key="cire")

# --- FONCTION D'IMPORT ---
def traiter_csv_brut(texte_csv, nom_type):
    try:
        df = pd.read_csv(StringIO(texte_csv), sep="\t")
        expected_cols = ["Date", "Serial", "OF", "Nom_Cote", "Mesure","Nominal", "Tolérance_Min", "Tolérance_Max"]
        if not all(col in df.columns for col in expected_cols):
            st.error(f"🛑 Colonnes attendues pour {nom_type} : {expected_cols}. Colonnes détectées : {df.columns.tolist()}")
            return None
        df["Mesure"] = df["Mesure"].astype(str).str.replace(",", ".").astype(float)
        df["Écart (mm)"] = df["Nominal"] - df["Mesure"]
        df["Écart (%)"] = 100 * df["Écart (mm)"] / df["Mesure"]
        df["Hors tolérance"] = ~df["Nominal"].between(df["Tolérance_Min"], df["Tolérance_Max"])
        return df
    except Exception as e:
        st.error(f"❌ Erreur de lecture des données pour {nom_type} : {e}")
        return None

# --- TRAITEMENT DES DEUX BLOCS ---
if metal_text_input:
    df_metal = traiter_csv_brut(metal_text_input, "Métal")
    if df_metal is not None:
        st.subheader("✅ Données analysées pour Métal")
        st.dataframe(df_metal, use_container_width=True)

if cire_text_input:
    df_cire = traiter_csv_brut(cire_text_input, "Cire")
    if df_cire is not None:
        st.subheader("✅ Données analysées pour Cire")
        st.dataframe(df_cire, use_container_width=True)
