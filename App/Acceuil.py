import streamlit as st
import pandas as pd
from io import StringIO
import json
import trimesh # type: ignore
import plotly.graph_objects as go
import os
import math
from dictionaries import mapping_stl, cotes_critiques_par_type
from modules.structured_data import nettoyer_donnees_brutes_excel

st.set_page_config(page_title="Accueil - Étude dimensionnelle", layout="wide")
st.title("🏭 Outil d'Étude Dimensionnelle")


type_analyse = st.radio(
    "Quel est le type d’analyse souhaité ?",
    [
        "Étude statistique rapide (vie série)",
        "Comparaison (cire / métal, ScanBox / CMM, etc.)",
        "Étude des dérives (vie série)",
        "Étude dimensionnelle (développement pièce)"
    ]
)

# Sauvegarde dans session_state pour les autres pages
st.session_state["type_analyse"] = type_analyse

if type_analyse == "Étude statistique rapide (vie série)":
    st.success("✅ Vous avez sélectionné : **Étude statistique rapide**.")
    st.markdown("👉 Cliquez sur l’onglet **AnalyseStatRapide** dans la **barre latérale** pour lancer l’analyse.")

elif type_analyse == "Comparaison (cire / métal, ScanBox / CMM, etc.)":
    st.success("✅ Vous avez sélectionné : **Comparaison** dimensionnelle.")
    st.markdown("👉 Cliquez sur l’onglet **Comparaison** dans la **barre latérale** pour lancer l’analyse.")
else:
    st.warning("⚠️ Le type d’analyse sélectionné n’est pas encore pris en charge dans cette version.")

# Fonctions 
# Heuristique de type par défaut selon le nom
def detect_type(nom):
    nom_lower = nom.lower()
    if "ø" in nom_lower or "diam" in nom_lower:
        return "Diamètre extérieur"
    elif "rayon" in nom_lower or "r" in nom_lower:
        return "Rayon"
    elif "épais" in nom_lower or "epaiss" in nom_lower:
        return "Épaisseur"
    elif "long" in nom_lower:
        return "Longueur"
    elif "angle" in nom_lower:
        return "Angle"
    elif "ales" in nom_lower:
        return "Alésage"
    else:
        return "Autre"

# --- LAYOUT ---

st.subheader("📋 Coller les données CSV depuis Excel")
text_input = st.text_area("Collez ici les données copiées depuis Excel", height=300)

st.subheader("📐 Visualisation 3D des pièces")

col1, col2 = st.columns([1, 2])

# mapping_stl et cotes_critiques_par_type sont maintenant importés
with col1:
    type_piece = st.selectbox(
        "Quel type de pièce analysez-vous ?",
        list(cotes_critiques_par_type.keys())
    )

    # Affichage des cotes critiques à cocher
    cotes_possibles = cotes_critiques_par_type.get(type_piece, [])
    cotes_critiques_selectionnees = st.multiselect(
        "📌 Sélectionnez les cotes critiques à suivre :", cotes_possibles,
        default=cotes_possibles  # toutes sélectionnées par défaut si tu veux
    )

    # (Optionnel) Stocker dans session_state si besoin ailleurs
    st.session_state["cotes_critiques_selectionnees"] = cotes_critiques_selectionnees
with col2:
    st.subheader("🔎 Visualisation 3D tournante")

    fichier_stl = mapping_stl.get(type_piece)
    chemin_fichier = os.path.join("static", fichier_stl) if fichier_stl else None

    if chemin_fichier and os.path.exists(chemin_fichier):
        with st.spinner("🔄 Chargement du modèle 3D..."):
            st.session_state.angle = st.session_state.get("angle", 0) + 5  # fait tourner
            mesh = trimesh.load_mesh(chemin_fichier)

            # Caméra
            r = 2.5
            theta = math.radians(st.session_state.angle)
            camera_eye = dict(x=r * math.cos(theta), y=0.8, z=r * math.sin(theta))

            fig = go.Figure(data=[
                go.Mesh3d(
                    x=mesh.vertices[:, 0],
                    y=mesh.vertices[:, 1],
                    z=mesh.vertices[:, 2],
                    i=mesh.faces[:, 0],
                    j=mesh.faces[:, 1],
                    k=mesh.faces[:, 2],
                    color='lightblue',
                    opacity=1.0
                )
            ])

            fig.update_layout(
                scene=dict(
                    xaxis=dict(visible=False),
                    yaxis=dict(visible=False),
                    zaxis=dict(visible=False),
                    camera=dict(eye=camera_eye),
                    aspectmode='data'
                ),
                margin=dict(l=0, r=0, t=0, b=0)
            )

            st.plotly_chart(fig, use_container_width=True)

    elif fichier_stl:
        st.warning("❌ Fichier STL introuvable.")
    else:
        st.info("ℹ️ Aucun modèle STL associé à ce type de pièce.")

if text_input:
    try:
        # Utilisation de la fonction de nettoyage pour transformer les données collées
        df_raw = pd.read_csv(StringIO(text_input), sep="\t", header=None)
        df = nettoyer_donnees_brutes_excel(df_raw)

        # Vérification des colonnes attendues
        expected_cols = ["Date", "Serial", "OF", "Nom_Cote", "Mesure", "Nominal", "Tolérance_Min", "Tolérance_Max"]
        if not all(col in df.columns for col in expected_cols):
            st.error(f"❌ Colonnes attendues : {expected_cols}. Colonnes détectées : {df.columns.tolist()}")
        else:
            st.success("✅ Données chargées avec succès !")

            # Supprimer les doublons de Nom_Cote
            unique_cotes = df["Nom_Cote"].dropna().unique()

        # --- Initialisation ---
        unique_cotes = df["Nom_Cote"].dropna().unique().tolist()

        if "cotes_info" not in st.session_state:
            st.session_state.cotes_info = {}

        # Ajouter les nouvelles cotes manquantes
        for cote in unique_cotes:
            if cote not in st.session_state.cotes_info:
                st.session_state.cotes_info[cote] = {
                    "Type_Cote": detect_type(cote),
                    "Tolérances_GPS": [],
                    "Groupe_Profil": None
                }

        if "groupes_cotes" not in st.session_state:
            st.session_state.groupes_cotes = []

        types_possibles = ["Diamètre extérieur", "Alésage", "Épaisseur", "Rayon", "Longueur", "Angle", "Autre"]
        gps_flat_list = [
            "Planéité", "Rectitude", "Circularité", "Cylindricité",
            "Parallélisme", "Perpendicularité", "Inclinaison",
            "Position vraie", "Battement", "Symétrie",
            "Rugosité", "Référentiel A", "Référentiel B"
        ]

        # --- Disposition 2 colonnes : caractérisation / visualisation ---
        col_left, col_right = st.columns([1.5, 2])

        with col_left:
            st.subheader("🛠️ Caractérisation des cotes principales")

            with st.expander("🔽 Modifier types et tolérances", expanded=True):
                for i in range(0, len(unique_cotes), 2):
                    cols = st.columns(2)
                    for j in range(2):
                        if i + j < len(unique_cotes):
                            cote = unique_cotes[i + j]
                            with cols[j]:
                                st.markdown(f"**🔹 {cote}**")
                                st.session_state.cotes_info[cote]["Type_Cote"] = st.selectbox(
                                    "Type", types_possibles,
                                    index=types_possibles.index(st.session_state.cotes_info[cote]["Type_Cote"])
                                    if st.session_state.cotes_info[cote]["Type_Cote"] in types_possibles else 0,
                                    key=f"type_{cote}"
                                )
                                # Initialisation des champs manquants dans la session state
                                if "Position_Angulaire" not in st.session_state.cotes_info[cote]:
                                    st.session_state.cotes_info[cote]["Position_Angulaire"] = "Non spécifié"
                                if "Angle_Degres" not in st.session_state.cotes_info[cote]:
                                    st.session_state.cotes_info[cote]["Angle_Degres"] = None
                                # Si c’est un rayon angulaire, proposer le choix de position angulaire
                                if st.session_state.cotes_info[cote]["Type_Cote"] == "Rayon":

                                    # Détection auto des ANGx présents dans le jeu de données
                                    all_cotes = df["Nom_Cote"].dropna().unique().tolist()
                                    ang_candidats = sorted({c.split()[-1] for c in all_cotes if "ANG" in c and cote.replace(" ANG", "") in c})
                                    ang_options = [f"ANG{i}" for i in range(1, len(ang_candidats)+1)] if ang_candidats else []
                                    position_choices = ["Non spécifié"] + ang_options + ["Autre (angle personnalisé)"]

                                    choix_angulaire = st.selectbox("Position angulaire", position_choices, key=f"angulaire_{cote}")
                                    st.session_state.cotes_info[cote]["Position_Angulaire"] = choix_angulaire

                                    if choix_angulaire == "Autre (angle personnalisé)":
                                        angle_libre = st.number_input("Angle (en degrés)", min_value=0.0, max_value=360.0, step=1.0, key=f"angle_libre_{cote}")
                                        st.session_state.cotes_info[cote]["Angle_Degres"] = angle_libre
                                    else:
                                        st.session_state.cotes_info[cote]["Angle_Degres"] = None

                                st.session_state.cotes_info[cote]["Tolérances_GPS"] = st.multiselect(
                                    "Tolérances GPS", gps_flat_list,
                                    default=st.session_state.cotes_info[cote]["Tolérances_GPS"],
                                    key=f"gps_{cote}"
                                )


        with col_right:
            st.subheader("📊 Tableau des données")

            selected_type = st.selectbox("Filtrer par type :", ["Tous"] + types_possibles)
            df_visu = pd.DataFrame([
                {
                    "Nom_Cote": cote,
                    "Type_Cote": info["Type_Cote"],
                    "Tolérances_GPS": ", ".join(info["Tolérances_GPS"]),
                    "Groupe_Profil": info["Groupe_Profil"]
                }
                for cote, info in st.session_state.cotes_info.items()
            ])
            df_filtered = df_visu if selected_type == "Tous" else df_visu[df_visu["Type_Cote"] == selected_type]
            st.dataframe(df_filtered, use_container_width=True)
            st.session_state.df_cotes = df_filtered

            # --- Groupe et export SOUS le tableau ---

              # --- Partie sélection des cotes à lier (placée après le layout principal) ---
            st.markdown("---")
            st.subheader("🔗 Lier des cotes dans une tolérance de profil")
            cotes_a_lier = st.multiselect("Sélectionnez les cotes à lier :", unique_cotes, key="cotes_a_lier")

            if st.button("➕ Lier les cotes sélectionnées"):
                if len(cotes_a_lier) >= 2:
                    st.session_state.groupes_cotes.append(cotes_a_lier)
                    group_id = len(st.session_state.groupes_cotes)
                    for cote in cotes_a_lier:
                        st.session_state.cotes_info[cote]["Groupe_Profil"] = group_id
                    st.success(f"Groupe {group_id} créé : {', '.join(cotes_a_lier)}")
                else:
                    st.warning("Sélectionnez au moins deux cotes.")

            st.markdown("### 🧷 Groupes de tolérances de profil")
            if st.session_state.groupes_cotes:
                for idx, groupe in enumerate(st.session_state.groupes_cotes):
                    st.markdown(f"**Groupe {idx + 1}** : {', '.join(groupe)}")
            else:
                st.info("Aucun groupe de cotes n'a encore été défini.")

            st.subheader("📤 Exporter les données")
            col1, col2 = st.columns(2)
            with col1:
                st.download_button("📥 Export CSV", df_visu.to_csv(index=False).encode(), file_name="cotes_info.csv")
            with col2:
                st.download_button("📥 Export JSON", json.dumps(st.session_state.cotes_info, indent=2).encode(), file_name="cotes_info.json")

    except Exception as e:
        st.error(f"Erreur lors du chargement des données : {e}")
