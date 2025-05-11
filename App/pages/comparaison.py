import streamlit as st
import pandas as pd
from io import StringIO
import altair as alt

# Vérifie que le type d’analyse est bien “stat rapide”
if st.session_state.get("type_analyse") != "Comparaison (cire / métal, ScanBox / CMM, etc.)":
    st.error("❌ Cette page est réservée à la comparaison dimensionnelle.")
    st.stop()


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
        df["Hors tolérance"] = ~df["Mesure"].between(df["Tolérance_Min"], df["Tolérance_Max"])
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

# --- FONCTION DE PRÉPARATION ---
def preparer_donnees_comparaison(df_metal, df_cire):
    # Préparation des données pour la comparaison
    df_metal['Nom_Cote_Normalisé'] = df_metal['Nom_Cote']
    df_cire['Nom_Cote_Normalisé'] = df_cire['Nom_Cote'].str.replace("Cire_", "", regex=False)

    df_metal['Type'] = 'Métal'
    df_cire['Type'] = 'Cire'

    return pd.concat([df_metal, df_cire], ignore_index=True)

# --- FONCTION GRAPHIQUE ---
def afficher_graphique_comparaison(df_metal, df_cire):
    # Préparation
    df_comparaison = preparer_donnees_comparaison(df_metal, df_cire)

    st.subheader("📉 Distribution des mesures par cote (toutes pièces)")

    # Sélection du nom de cote
    selected_nom_cote = st.selectbox(
        "Sélectionnez un nom de cote :", 
        df_comparaison["Nom_Cote_Normalisé"].unique()
    )

    # Filtrage
    df_graph = df_comparaison[df_comparaison["Nom_Cote_Normalisé"] == selected_nom_cote]

    # Ajout bande de tolérance (une seule paire pour le graphe)
    tol_min = df_graph["Tolérance_Min"].iloc[0]
    tol_max = df_graph["Tolérance_Max"].iloc[0]
    band = alt.Chart(pd.DataFrame({'y': [tol_min], 'y2': [tol_max]})).mark_rect(opacity=0.1, color='green').encode(
        y='y:Q',
        y2='y2:Q'
    )

    # Chart avec points
    chart = alt.Chart(df_graph).mark_circle(size=60).encode(
        x=alt.X('OF:N', title='Ordre de Fabrication (OF)', sort=alt.EncodingSortField(field="OF", order="ascending")),
        y=alt.Y('Mesure:Q', title='Mesure (mm)', scale=alt.Scale(zero=False)),
        color=alt.Color('Type:N', title='Type'),
        shape=alt.Shape('Type:N'),
        tooltip=['Serial', 'OF', 'Type', 'Mesure', 'Nominal', 'Tolérance_Min', 'Tolérance_Max']
    ).properties(
        title=f"Comparaison des Mesures pour {selected_nom_cote}",
        width=800,
        height=400
    ).interactive()

    # Fusion bande de tolérance + données
    final_chart = band + chart
    st.altair_chart(final_chart, use_container_width=True)

    # Alerte auto si écart moyen > seuil
    df_metal_sel = df_graph[df_graph["Type"] == "Métal"]
    df_cire_sel = df_graph[df_graph["Type"] == "Cire"]

    if not df_metal_sel.empty and not df_cire_sel.empty:
        moyenne_metal = df_metal_sel["Mesure"].mean()
        moyenne_cire = df_cire_sel["Mesure"].mean()
        ecart_moyen = abs(moyenne_metal - moyenne_cire)

        if ecart_moyen > 0.05:
            st.warning(f"⚠️ L'écart moyen entre métal et cire pour la cote '{selected_nom_cote}' est de {ecart_moyen:.3f} mm.")

# --- APPEL DE LA FONCTION GRAPHIQUE ---
# Call the function if both datasets are available
if metal_text_input and cire_text_input:
    if df_metal is not None and df_cire is not None:
        afficher_graphique_comparaison(df_metal, df_cire)

def afficher_boxplot_comparaison(df_metal, df_cire):
    st.subheader("📦 Boxplot des mesures par cote")

    # Préparer les données
    df_comparaison = preparer_donnees_comparaison(df_metal, df_cire)

    selected_nom_cote = st.selectbox(
        "Sélectionnez une cote pour afficher le boxplot :",
        df_comparaison["Nom_Cote_Normalisé"].unique(),
        key="boxplot_select"
    )

    df_graph = df_comparaison[df_comparaison["Nom_Cote_Normalisé"] == selected_nom_cote]

    box = alt.Chart(df_graph).mark_boxplot(extent='min-max').encode(
        x=alt.X('Type:N', title='Type (Cire ou Métal)'),
        y=alt.Y('Mesure:Q', title='Mesure (mm)', scale=alt.Scale(zero=False)),
        color=alt.Color('Type:N', title='Type')
    )

    points = alt.Chart(df_graph).mark_circle(size=60, opacity=0.4).encode(
        x='Type:N',
        y='Mesure:Q',
        color='Type:N',
        tooltip=['Serial', 'OF', 'Mesure', 'Nominal']
    )

    st.altair_chart((box + points).properties(
        width=600,
        height=400,
        title=f"📦 Boxplot des mesures pour la cote : {selected_nom_cote}"
    ), use_container_width=True)

if metal_text_input and cire_text_input:
    if df_metal is not None and df_cire is not None:
        afficher_boxplot_comparaison(df_metal, df_cire)

        