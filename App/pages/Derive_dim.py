import streamlit as st
import pandas as pd
import plotly.express as px
from io import StringIO

# --- CONFIG ---
st.set_page_config(page_title="Étude des dérives dimensionnelles", layout="wide")
st.title("📉 Étude des dérives dimensionnelles (vie série)")

# --- IMPORT DES DONNÉES ---
st.subheader("📋 Import des données depuis Excel")
text_input = st.text_area("Collez ici les données copiées depuis Excel (avec tabulations)", height=300)

expected_cols = ["Date", "Serial", "OF", "Nom_Cote", "Mesure", "Nominal", "Tolérance_Min", "Tolérance_Max"]
df = None

if text_input:
    try:
        df = pd.read_csv(StringIO(text_input), sep="\t")

        if not all(col in df.columns for col in expected_cols):
            st.error(f"❌ Colonnes manquantes. Colonnes attendues : {expected_cols}")
            st.stop()

        df["Date"] = pd.to_datetime(df["Date"])
        df["Hors_Tolérance"] = (df["Mesure"] < df["Tolérance_Min"]) | (df["Mesure"] > df["Tolérance_Max"])
        st.success("✅ Données importées avec succès")

    except Exception as e:
        st.error(f"❌ Erreur lors de l'import : {e}")
        st.stop()

# --- ANALYSE PAR COTE ---
if df is not None:
    st.subheader("🔍 Analyse par cote")

    nom_cote = st.selectbox("Sélectionnez une cote :", sorted(df["Nom_Cote"].unique()))
    df_cote = df[df["Nom_Cote"] == nom_cote]

    # --- FILTRE PAR PÉRIODE ---
    st.markdown("### ⏱️ Filtrer par période")
    min_date, max_date = df_cote["Date"].min(), df_cote["Date"].max()
    date_range = st.date_input("Choisissez une plage de dates :", (min_date, max_date))

    if isinstance(date_range, tuple) and len(date_range) == 2:
        df_cote = df_cote[(df_cote["Date"] >= pd.to_datetime(date_range[0])) & 
                          (df_cote["Date"] <= pd.to_datetime(date_range[1]))]

    st.markdown("### 📈 Évolution dans le temps")
    fig = px.line(df_cote.sort_values("Date"), x="Date", y="Mesure", markers=True,
                  title=f"Évolution de la cote '{nom_cote}' dans le temps")
    fig.add_hline(y=df_cote["Nominal"].iloc[0], line_color="green", line_dash="dash", annotation_text="Nominal")
    fig.add_hline(y=df_cote["Tolérance_Min"].iloc[0], line_color="red", line_dash="dot", annotation_text="Tol. Min")
    fig.add_hline(y=df_cote["Tolérance_Max"].iloc[0], line_color="red", line_dash="dot", annotation_text="Tol. Max")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 📦 Distribution par OF")
    fig_box = px.box(df_cote, x="OF", y="Mesure", points="all", color="Hors_Tolérance",
                     color_discrete_map={False: "blue", True: "red"},
                     title=f"Distribution par OF pour '{nom_cote}'")
    st.plotly_chart(fig_box, use_container_width=True)
