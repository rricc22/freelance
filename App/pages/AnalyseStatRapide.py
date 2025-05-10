import streamlit as st
import pandas as pd
import numpy as np
import os
from io import StringIO


# Vérifie que le type d’analyse est bien “stat rapide”
if st.session_state.get("type_analyse") != "Étude statistique rapide (vie série)":
    st.error("❌ Cette page est réservée à l’analyse statistique rapide.")
    st.stop()


# --- CONFIG ---
st.set_page_config(page_title="Étude dimensionnelle", layout="wide")
st.title("📏 Dashboard d'Étude Dimensionnelle")

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

            # --- Sélection OF ---
            st.subheader("📊 Données Mesure")
            selected_of = st.selectbox("Sélectionnez un OF :", df["OF"].astype(str).unique())
            df_filtered = df[df["OF"].astype(str) == selected_of]

            st.dataframe(df_filtered, use_container_width=True)
            

            # --- STATISTIQUES PAR COTE ---
            # --- GRAPHIQUES PAR COTE (POPULATION COMPLÈTE) ---


            st.subheader("📉 Distribution des écarts par cote (toutes pièces)")

            selected_nom_cote = st.selectbox("Sélectionnez un nom de cote :", df["Nom_Cote"].unique())
            df_graph = df[df["Nom_Cote"] == selected_nom_cote]

            import altair as alt
            chart = alt.Chart(df_graph).mark_bar().encode(
                x=alt.X("Écart (mm):Q", bin=alt.Bin(maxbins=30), title="Écart (mm)"),
                y=alt.Y("count():Q", title="Nombre de pièces"),   
                tooltip=["count()"]
            ).properties(
                width=600,
                height=400,
                title=f"Distribution des écarts pour {selected_nom_cote} (toutes pièces)"
            )

            st.altair_chart(chart, use_container_width=True)
            

            def compute_stats(group):
                if len(group) < 2:
                    return pd.Series({
                        "N Mesures": len(group),
                        "Moyenne": group["Mesure_Theorique"].mean(),
                        "Écart-type": None,
                        "Écart moyen absolu": group["Écart (mm)"].abs().mean(),
                        "Cp": None,
                        "Cpk": None,
                        "% hors tolérance": 100 * group["Hors tolérance"].mean()
                    })
                else:
                    std = group["Mesure_Theorique"].std()
                    mean = group["Mesure_Theorique"].mean()
                    tol_min = group["Tolérance_Min"].iloc[0]
                    tol_max = group["Tolérance_Max"].iloc[0]
                    cp = (tol_max - tol_min) / (6 * std) if std > 0 else None
                    cpk = min(tol_max - mean, mean - tol_min) / (3 * std) if std > 0 else None

                    return pd.Series({
                        "N Mesures": int(len(group)),
                        "Moyenne": mean,
                        "Écart-type": std,
                        "Écart moyen absolu": group["Écart (mm)"].abs().mean(),
                        "Cp": cp,
                        "Cpk": cpk,
                        "% hors tolérance": 100 * group["Hors tolérance"].mean()
                    })

                
            stats_df = df.groupby("Nom_Cote").apply(compute_stats).reset_index()

            st.dataframe(
                stats_df.style.format({
                    "N Mesures": "{:.0f}",
                    "Moyenne": "{:.3f}",
                    "Écart-type": "{:.3f}",
                    "Écart moyen absolu": "{:.3f}",
                    "Cp": "{:.2f}",
                    "Cpk": "{:.2f}",
                    "% hors tolérance": "{:.1f} %"
                }),
                use_container_width=True
            )

    except Exception as e:
        st.error(f"Erreur de lecture des données : {e}")
else:
    st.info("Veuillez copier-coller les données depuis Excel avec les colonnes correctes.")
