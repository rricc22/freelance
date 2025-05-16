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

    except Exception as e:
        st.error(f"❌ Erreur : {e}")
else:
    st.info("🕐 En attente de données à coller…")
