# import streamlit as st
# import plotly.graph_objects as go

# import pandas as pd
# import numpy as np

# # Simuler des positions le long d'une pièce (en mm)
# positions = np.linspace(0, 120, 13)  # tous les 10 mm

# # Simuler des cotes d'épaisseur (paroi, patin) mesurées à chaque position
# types_epaisseurs = {
#     "Épaisseur patin A": dict(nominal=5.0, tol_min=4.8, tol_max=5.2),
#     "Épaisseur patin B": dict(nominal=4.0, tol_min=3.7, tol_max=4.3),
#     "Épaisseur paroi latérale": dict(nominal=3.0, tol_min=2.8, tol_max=3.2)
# }

# # Génération des données
# data = []
# for cote, tol in types_epaisseurs.items():
#     for pos in positions:
#         mesure = np.round(np.random.normal(tol["nominal"], 0.07), 3)
#         data.append({
#             "Nom_Cote": cote,
#             "Position": pos,
#             "Mesure": mesure,
#             "Nominal": tol["nominal"],
#             "Tolérance_Min": tol["tol_min"],
#             "Tolérance_Max": tol["tol_max"]
#         })

# df_epaisseurs = pd.DataFrame(data)

# # Préparer les données simulées
# positions = df_epaisseurs["Position"].unique()
# cotes_dispo = df_epaisseurs["Nom_Cote"].unique()
# import streamlit as st
# import plotly.graph_objects as go
# import pandas as pd

# # Données chargées depuis df_epaisseurs
# df = df_epaisseurs.copy()
# df["Écart"] = df["Mesure"] - df["Nominal"]
# df["Hors_Tol"] = (df["Mesure"] < df["Tolérance_Min"]) | (df["Mesure"] > df["Tolérance_Max"])

# st.set_page_config(page_title="Épaisseurs - Avancé", layout="wide")
# st.title("🧱 Analyse avancée des épaisseurs")

# # Sélection d’une seule cote
# selected_cote = st.selectbox("Sélectionnez une cote :", df["Nom_Cote"].unique())
# df_cote = df[df["Nom_Cote"] == selected_cote]

# # === Layout principal ===
# col1, col2 = st.columns([2, 1])

# # --- GRAPHIQUE PROFIL AVEC ZONE OMBRÉE ---
# with col1:
#     fig = go.Figure()

#     fig.add_trace(go.Scatter(
#         x=df_cote["Position"],
#         y=df_cote["Tolérance_Max"],
#         mode='lines',
#         line=dict(width=0),
#         name="Tolérance max",
#         showlegend=False
#     ))

#     fig.add_trace(go.Scatter(
#         x=df_cote["Position"],
#         y=df_cote["Tolérance_Min"],
#         fill='tonexty',
#         fillcolor='rgba(0,200,0,0.1)',
#         line=dict(width=0),
#         mode='lines',
#         name="Zone tolérée",
#         showlegend=True
#     ))

#     fig.add_trace(go.Scatter(
#         x=df_cote["Position"],
#         y=df_cote["Mesure"],
#         mode='lines+markers',
#         name="Mesure",
#         line=dict(color='blue')
#     ))

#     fig.update_layout(
#         title=f"📈 Profil d'épaisseur : {selected_cote}",
#         xaxis_title="Position (mm)",
#         yaxis_title="Mesure (mm)",
#         height=500
#     )

#     st.plotly_chart(fig, use_container_width=True)

# # --- GRAPHIQUE CIRCLES & TABLEAU ---
# with col2:
#     tab1, tab2 = st.tabs(["🟢 Carte conformité", "📋 Détails mesures"])

#     with tab1:
#         fig_check = go.Figure()
#         fig_check.add_trace(go.Scatter(
#             x=df_cote["Position"],
#             y=[1] * len(df_cote),
#             mode='markers+text',
#             marker=dict(
#                 size=18,
#                 color=df_cote["Hors_Tol"].map({False: "green", True: "red"}),
#             ),
#             text=[f'{v:.2f}' for v in df_cote["Mesure"]],
#             textposition="top center",
#             showlegend=False
#         ))

#         fig_check.update_layout(
#             title="✅ Conformité par position",
#             xaxis_title="Position (mm)",
#             yaxis=dict(showticklabels=False),
#             height=350
#         )

#         st.plotly_chart(fig_check, use_container_width=True)

#     with tab2:
#         st.dataframe(
#             df_cote[["Position", "Mesure", "Nominal", "Écart", "Tolérance_Min", "Tolérance_Max", "Hors_Tol"]],
#             use_container_width=True
#         )

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

def analyser_epaisseurs(df):
    # Validation des colonnes nécessaires
    required_cols = ["Nom_Cote", "Mesure", "Nominal", "Tolérance_Min", "Tolérance_Max"]
    if not all(col in df.columns for col in required_cols):
        st.warning("❗ Les colonnes nécessaires pour l'analyse d'épaisseur sont manquantes.")
        return

    # Vérifie s'il y a une colonne Position, sinon générer une par défaut
    if "Position" not in df.columns:
        unique_cotes = df["Nom_Cote"].unique()
        position_mapping = {
            cote: list(np.linspace(0, 100, len(df[df["Nom_Cote"] == cote])))
            for cote in unique_cotes
        }
        df["Position"] = df.apply(lambda row: position_mapping[row["Nom_Cote"]].pop(0), axis=1)

    df["Écart"] = df["Mesure"] - df["Nominal"]
    df["Hors_Tol"] = (df["Mesure"] < df["Tolérance_Min"]) | (df["Mesure"] > df["Tolérance_Max"])

    st.subheader("🧱 Analyse avancée des épaisseurs")

    selected_cote = st.selectbox("Sélectionnez une cote :", df["Nom_Cote"].unique())
    df_cote = df[df["Nom_Cote"] == selected_cote]

    col1, col2 = st.columns([2, 1])

    with col1:
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df_cote["Position"],
            y=df_cote["Tolérance_Max"],
            mode='lines',
            line=dict(width=0),
            name="Tolérance max",
            showlegend=False
        ))

        fig.add_trace(go.Scatter(
            x=df_cote["Position"],
            y=df_cote["Tolérance_Min"],
            fill='tonexty',
            fillcolor='rgba(0,200,0,0.1)',
            line=dict(width=0),
            mode='lines',
            name="Zone tolérée",
            showlegend=True
        ))

        fig.add_trace(go.Scatter(
            x=df_cote["Position"],
            y=df_cote["Mesure"],
            mode='lines+markers',
            name="Mesure",
            line=dict(color='blue')
        ))

        fig.update_layout(
            title=f"📈 Profil d'épaisseur : {selected_cote}",
            xaxis_title="Position (mm)",
            yaxis_title="Mesure (mm)",
            height=500
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        tab1, tab2 = st.tabs(["🟢 Carte conformité", "📋 Détails mesures"])

        with tab1:
            fig_check = go.Figure()
            fig_check.add_trace(go.Scatter(
                x=df_cote["Position"],
                y=[1] * len(df_cote),
                mode='markers+text',
                marker=dict(
                    size=18,
                    color=df_cote["Hors_Tol"].map({False: "green", True: "red"}),
                ),
                text=[f'{v:.2f}' for v in df_cote["Mesure"]],
                textposition="top center",
                showlegend=False
            ))

            fig_check.update_layout(
                title="✅ Conformité par position",
                xaxis_title="Position (mm)",
                yaxis=dict(showticklabels=False),
                height=350
            )

            st.plotly_chart(fig_check, use_container_width=True)

        with tab2:
            st.dataframe(
                df_cote[["Position", "Mesure", "Nominal", "Écart", "Tolérance_Min", "Tolérance_Max", "Hors_Tol"]],
                use_container_width=True
            )
