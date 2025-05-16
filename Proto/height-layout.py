import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

st.set_page_config(page_title="Dashboard Hauteurs", layout="wide")
st.title("📊 Analyse dimensionnelle par hauteur")

# --- Données simulées ---
hauteurs = [0, 20, 40, 60, 80, 100]
types_cotes = {
    "Épaisseur patin": dict(nominal=5.0, tol_min=4.8, tol_max=5.2),
    "Largeur gorge": dict(nominal=10.0, tol_min=9.7, tol_max=10.3),
    "Épaisseur paroi": dict(nominal=3.0, tol_min=2.8, tol_max=3.2)
}

data = []
for cote, tol in types_cotes.items():
    for h in hauteurs:
        mesure = np.round(np.random.normal(tol["nominal"], 0.05), 3)
        data.append({
            "Nom_Cote": cote,
            "Hauteur": h,
            "Mesure": mesure,
            "Nominal": tol["nominal"],
            "Tolérance_Min": tol["tol_min"],
            "Tolérance_Max": tol["tol_max"]
        })

df = pd.DataFrame(data)

# --- Mode d'affichage : Global vs Détail ---
mode = st.radio(
    "Mode d'affichage :",
    ["Vue globale", "Vue détaillée (une seule cote)"],
    horizontal=True
)

if mode == "Vue détaillée (une seule cote)":
    cote_unique = st.selectbox("🔎 Choisissez une seule cote :", df["Nom_Cote"].unique())
    df_filtered = df[df["Nom_Cote"] == cote_unique]
    selected_cotes = [cote_unique]
else:
    selected_cotes = st.multiselect(
        "Sélectionnez les cotes à afficher :",
        df["Nom_Cote"].unique(),
        default=df["Nom_Cote"].unique()
    )
    df_filtered = df[df["Nom_Cote"].isin(selected_cotes)]

# --- GRAPHIQUE MULTI-CURVE ---
fig = go.Figure()

for cote in selected_cotes:
    df_cote = df_filtered[df_filtered["Nom_Cote"] == cote]

    fig.add_trace(go.Scatter(
        x=df_cote["Hauteur"],
        y=df_cote["Mesure"],
        mode='lines+markers',
        name=cote
    ))

    fig.add_trace(go.Scatter(
        x=df_cote["Hauteur"],
        y=df_cote["Tolérance_Min"],
        mode='lines',
        name=f"{cote} - Tolérance min",
        line=dict(dash='dot'),
        showlegend=False
    ))

    fig.add_trace(go.Scatter(
        x=df_cote["Hauteur"],
        y=df_cote["Tolérance_Max"],
        mode='lines',
        name=f"{cote} - Tolérance max",
        line=dict(dash='dot'),
        showlegend=False
    ))

fig.update_layout(
    title="📈 Mesures en fonction de la hauteur",
    xaxis_title="Hauteur (mm)",
    yaxis_title="Mesure (mm)",
    height=500
)

# --- BAR CHART : ÉCARTS ---
df_filtered["Écart"] = df_filtered["Mesure"] - df_filtered["Nominal"]
fig_bar = go.Figure()

for cote in selected_cotes:
    df_cote = df_filtered[df_filtered["Nom_Cote"] == cote]
    fig_bar.add_trace(go.Bar(
        x=df_cote["Hauteur"],
        y=df_cote["Écart"],
        name=cote
    ))

fig_bar.update_layout(
    title="📊 Écarts par rapport au nominal",
    xaxis_title="Hauteur (mm)",
    yaxis_title="Écart (mm)",
    barmode="group",
    height=400
)

# --- Affichage en colonnes
col1, col2 = st.columns([1.5, 1])
with col1:
    st.plotly_chart(fig, use_container_width=True)
with col2:
    st.plotly_chart(fig_bar, use_container_width=True)
