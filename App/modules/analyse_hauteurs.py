import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

def analyser_hauteurs(df):
    st.subheader("📊 Analyse dimensionnelle par hauteur")

    # Détection automatique des colonnes candidates pour axe X
    colonnes_x = [col for col in df.columns if col.lower() in ["hauteur", "z", "position", "angle"]]
    default_x = "Hauteur" if "Hauteur" in df.columns else df.columns[0]
    colonne_x = st.selectbox("🧭 Choix de l'axe des abscisses :", colonnes_x or [default_x])

    # Mode d'affichage
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

    # Calcul des écarts
    df_filtered["Écart"] = df_filtered["Mesure"] - df_filtered["Nominal"]

    # GRAPHIQUE MULTI-CURVE
    fig = go.Figure()

    for cote in selected_cotes:
        df_cote = df_filtered[df_filtered["Nom_Cote"] == cote]

        fig.add_trace(go.Scatter(
            x=df_cote[colonne_x],
            y=df_cote["Mesure"],
            mode='lines+markers',
            name=cote
        ))

        fig.add_trace(go.Scatter(
            x=df_cote[colonne_x],
            y=df_cote["Tolérance_Min"],
            mode='lines',
            name=f"{cote} - Tolérance min",
            line=dict(dash='dot'),
            showlegend=False
        ))

        fig.add_trace(go.Scatter(
            x=df_cote[colonne_x],
            y=df_cote["Tolérance_Max"],
            mode='lines',
            name=f"{cote} - Tolérance max",
            line=dict(dash='dot'),
            showlegend=False
        ))

    fig.update_layout(
        title="📈 Mesures en fonction de la hauteur",
        xaxis_title=colonne_x,
        yaxis_title="Mesure (mm)",
        height=500
    )

    # BAR CHART : ÉCARTS
    fig_bar = go.Figure()

    for cote in selected_cotes:
        df_cote = df_filtered[df_filtered["Nom_Cote"] == cote]
        fig_bar.add_trace(go.Bar(
            x=df_cote[colonne_x],
            y=df_cote["Écart"],
            name=cote
        ))

    fig_bar.update_layout(
        title="📊 Écarts par rapport au nominal",
        xaxis_title=colonne_x,
        yaxis_title="Écart (mm)",
        barmode="group",
        height=400
    )

    # Affichage
    col1, col2 = st.columns([1.5, 1])
    with col1:
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.plotly_chart(fig_bar, use_container_width=True)
