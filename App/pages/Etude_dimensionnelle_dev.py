import streamlit as st
import pandas as pd
from io import StringIO
import json
import plotly.graph_objects as go

# --- Modules d'analyse spécifiques ---
from modules.analyse_hauteurs import analyser_hauteurs
from modules.analyse_rayons import analyser_rayons
from modules.analyse_epaisseurs import analyser_epaisseurs
from modules.data_cleaning import nettoyer_donnees_brutes

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
st.markdown("### 📅 Importer les caractéristiques des cotes")
fichier_json = st.file_uploader("Chargez un fichier JSON exporté précédemment", type="json")

if fichier_json is not None:
    try:
        donnees_importees = json.load(fichier_json)
        if "cotes_info" not in st.session_state:
            st.session_state.cotes_info = {}
        for nom_cote, infos in donnees_importees.items():
            st.session_state.cotes_info[nom_cote] = infos
        st.success("✅ Caractéristiques des cotes importées avec succès !")
    except Exception as e:
        st.error(f"❌ Erreur lors de l'import : {e}")

# --- Données CSV collées ---
st.markdown("### 📋 Coller les données CSV (copiées depuis Excel)")
text_input = st.text_area("Zone de saisie CSV", height=200)

df = None
if text_input.strip():
    try:
        df = nettoyer_donnees_brutes(text_input)
        st.success("✅ Données chargées avec succès")

        # Initialisation des cotes si absentes
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

        df["Type_Cote"] = df["Nom_Cote"].apply(detect_type)

        # Injecter Angle_Degres à partir de cotes_info
        if "cotes_info" in st.session_state:
            df["Angle_Degres"] = df["Nom_Cote"].map(
                lambda x: st.session_state.cotes_info.get(x, {}).get("Angle_Degres", None)
            )

        # Sélection des OF
        st.subheader("🧾 Sélection des OF à analyser")
        of_disponibles = df["OF"].dropna().unique().tolist()
        of_selectionnes = st.multiselect("Choisissez un ou plusieurs OF :", options=of_disponibles, default=of_disponibles)
        df = df[df["OF"].isin(of_selectionnes)]

        # Affichage tableau
        st.subheader("📊 Tableau des cotes disponibles")
        selected_type = st.selectbox("Filtrer par type :", ["Tous"] + types_possibles)
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

        # Analyse
        st.markdown("---")
        st.header("🔍 Analyse selon le type de cote")
        type_selectionne = st.selectbox("Quel type de cote souhaitez-vous analyser ?", df["Type_Cote"].unique())
        df_filtré = df[df["Type_Cote"] == type_selectionne]

        if type_selectionne == "Longueur":
            analyser_hauteurs(df_filtré)
        elif type_selectionne == "Rayon":
            df_rayon = df_filtré.copy()
            if "Angle_Degres" in df_rayon.columns and df_rayon["Angle_Degres"].notna().any():
                analyser_rayons(df_rayon)
            else:
                st.warning("⚠️ Colonne 'Angle_Degres' manquante ou vide.")


        elif type_selectionne == "Épaisseur":
            analyser_epaisseurs(df_filtré)
        else:
            st.info("Aucune analyse spécifique pour ce type de cote.")

    except Exception as e:
        st.error(f"❌ Erreur : {e}")
else:
    st.info("🕐 En attente de données à coller…")