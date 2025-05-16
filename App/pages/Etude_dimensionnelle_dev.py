import streamlit as st
import pandas as pd
from io import StringIO
import json

# --- Détection automatique du type de cote ---
def detect_type(nom):
    nom = nom.lower()
    if "rayon" in nom:
        return "Rayon"
    elif "diam" in nom or "ø" in nom:
        return "Diamètre extérieur"
    elif "épais" in nom or "patin" in nom:
        return "Épaisseur"
    elif "largeur" in nom or "hauteur" in nom or "gorge" in nom:
        return "Longueur"
    elif "perçage" in nom:
        return "Diamètre extérieur"
    elif "alésage" in nom:
        return "Alésage"
    elif "angle" in nom:
        return "Angle"
    else:
        return "Autre"

types_possibles = ["Diamètre extérieur", "Alésage", "Épaisseur", "Rayon", "Longueur", "Angle", "Autre"]

st.title("📏 Étude dimensionnelle - Développement")

# --- Import JSON des cotes ---
st.markdown("### 📥 Importer les caractéristiques des cotes")
fichier_json = st.file_uploader("Chargez un fichier JSON exporté précédemment", type="json")

if fichier_json is not None:
    try:
        donnees_importees = json.load(fichier_json)

        if "cotes_info" not in st.session_state:
            st.session_state.cotes_info = {}

        for nom_cote, infos in donnees_importees.items():
            if nom_cote not in st.session_state.cotes_info:
                st.session_state.cotes_info[nom_cote] = infos
            else:
                st.session_state.cotes_info[nom_cote].update(infos)

        st.success("✅ Caractéristiques des cotes importées avec succès !")
    except Exception as e:
        st.error(f"❌ Erreur lors de l'import : {e}")

# --- Données CSV collées ---
st.markdown("### 📋 Coller les données CSV (copiées depuis Excel)")
text_input = st.text_area("Zone de saisie CSV", height=200)

if text_input.strip():
    try:
        df = pd.read_csv(StringIO(text_input), sep="\t")

        expected_cols = ["Date", "Serial", "OF", "Nom_Cote", "Mesure", "Nominal", "Tolérance_Min", "Tolérance_Max"]
        if not all(col in df.columns for col in expected_cols):
            st.error(f"❌ Colonnes attendues : {expected_cols}")
            st.stop()

        st.success("✅ Données chargées avec succès")

        # --- Initialisation des cotes si absentes ---
        if "cotes_info" not in st.session_state or not st.session_state.cotes_info:
            unique_cotes = df["Nom_Cote"].dropna().unique().tolist()
            st.session_state.cotes_info = {
                cote: {
                    "Type_Cote": detect_type(cote),
                    "Tolérances_GPS": [],
                    "Groupe_Profil": None,
                    "Position_Angulaire": "Non spécifié",
                    "Angle_Degres": None
                }
                for cote in unique_cotes
            }

        # --- Affichage tableau + options ---
        col_gauche, col_droite = st.columns([1.5, 1])

        with col_gauche:
            st.subheader("📊 Tableau des cotes disponibles")

            selected_type = st.selectbox("Filtrer par type :", ["Tous"] + types_possibles, key="filtre_type_dev")

            df_visu = pd.DataFrame([
                {
                    "Nom_Cote": cote,
                    "Type_Cote": info.get("Type_Cote", ""),
                    "Tolérances_GPS": ", ".join(info.get("Tolérances_GPS", [])),
                    "Groupe_Profil": info.get("Groupe_Profil", ""),
                    "Position_Angulaire": info.get("Position_Angulaire", ""),
                    "Angle_Degres": info.get("Angle_Degres", "")
                }
                for cote, info in st.session_state.cotes_info.items()
            ])

            df_filtered = df_visu if selected_type == "Tous" else df_visu[df_visu["Type_Cote"] == selected_type]
            st.dataframe(df_filtered, use_container_width=True)

            st.download_button(
                label="📥 Exporter JSON des cotes",
                data=json.dumps(st.session_state.cotes_info, indent=2).encode(),
                file_name="caracterisation_cotes.json",
                mime="application/json"
            )

        with col_droite:
            st.subheader("🧩 Sélection des OF à analyser")
            of_dispo = df["OF"].dropna().unique().tolist()
            of_selectionnes = st.multiselect("Choisissez les OF :", options=of_dispo, key="of_selectionnes_dev")

            st.subheader("📌 Synthèse des cotes sélectionnées")
            if "groupes_cotes" in st.session_state and st.session_state.groupes_cotes:
                for idx, groupe in enumerate(st.session_state.groupes_cotes):
                    st.markdown(f"**Groupe {idx + 1}** : {', '.join(groupe)}")
                if st.button("♻️ Réinitialiser les groupes de cotes"):
                    st.session_state.groupes_cotes = []
                    st.success("Groupes de cotes réinitialisés.")
            else:
                st.info("Aucun groupe de cotes n'a encore été défini.")

        import plotly.graph_objects as go

        st.markdown("### 🌟 Visualisation en étoile interactive (Plotly)")

        # Exemple : extraire les mesures pour une seule cote et OF
        nom_cote_cible = "Rayon extérieur ANG1"  # ou autre
        of_cible = df["OF"].iloc[0]

        df_cible = df[(df["Nom_Cote"].str.contains("ANG")) & (df["Nom_Cote"].str.contains("Rayon")) & (df["OF"] == of_cible)]

        if df_cible.empty:
            st.info("Aucune donnée angulaire détectée.")
        else:
            # Extraire l'angle depuis le nom de la cote : ANG1 → 0°, ANG2 → 120°, etc.
            def extraire_angle(nom):
                if "ANG" in nom:
                    try:
                        n = int(nom.split("ANG")[-1])
                        return (n - 1) * 360 / 12
                    except:
                        return 0
                return 0

            df_cible["Angle"] = df_cible["Nom_Cote"].apply(extraire_angle)

            # Ordonner
            df_cible = df_cible.sort_values("Angle")

            angles_deg = df_cible["Angle"].tolist() + [df_cible["Angle"].iloc[0]]
            mesures = df_cible["Mesure"].tolist() + [df_cible["Mesure"].iloc[0]]
            tol_plus = df_cible["Tolérance_Max"].tolist() + [df_cible["Tolérance_Max"].iloc[0]]
            tol_moins = df_cible["Tolérance_Min"].tolist() + [df_cible["Tolérance_Min"].iloc[0]]

            fig = go.Figure()

            fig.add_trace(go.Scatterpolar(
                r=mesures,
                theta=angles_deg,
                mode='lines+markers',
                name='Mesure',
                line=dict(width=3)
            ))

            fig.add_trace(go.Scatterpolar(
                r=tol_plus,
                theta=angles_deg,
                mode='lines',
                name='Tolérance +',
                line=dict(dash='dot')
            ))

            fig.add_trace(go.Scatterpolar(
                r=tol_moins,
                theta=angles_deg,
                mode='lines',
                name='Tolérance -',
                line=dict(dash='dot')
            ))

            fig.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True),
                    angularaxis=dict(direction="clockwise")
                ),
                showlegend=True,
                title=f"Profil angulaire — {nom_cote_cible} — OF {of_cible}"
            )

            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Erreur : {e}")
else:
    st.info("🕐 En attente de données à coller…")
