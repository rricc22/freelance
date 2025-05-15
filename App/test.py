import streamlit as st
import trimesh
import plotly.graph_objects as go
import os
import math

st.set_page_config(layout="wide")
st.header("🧩 Caractérisation de la pièce")

col1, col2 = st.columns([1, 2])

# Dictionnaire de correspondance type -> nom fichier STL
mapping_stl = {
    "Support palier": "Support_palier_compresseur.stl",
    "Nozzle": "Jet_Engine-Compressor_Housing.stl",
    "Distributeur": "Rotor_compresseur_distributeur.stl",
    "Roues": "Roue.stl",
    "Barettes": "Jet_Engine_Fan-Stator.stl",
    "Pales": "Jet_Engine_Fan-Stator.stl",  # Idem si pas de fichier distinct
    "Autre (forme libre)": None
}

with col1:
    type_piece = st.selectbox(
        "Quel type de pièce analysez-vous ?",
        list(mapping_stl.keys())
    )
    st.session_state["type_piece"] = type_piece

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


# --- LAYOUT ---

            # nom_zone = st.text_input("Nom de la zone")
            # type_gps = st.selectbox("Type de tolérance GPS", ["Planéité", "Rectitude", "Parallélisme", "Profil de surface"])
            # tol_gps = st.text_input("Tolérance associée (mm)")
            # referentiel = st.text_input("Référentiel (optionnel)")
            # commentaire = st.text_area("Commentaire")

            # type_mesure = st.selectbox("Type de mesure contrôlée :", ["Rayon", "Diamètre", "Épaisseur", "Distance", "Autre"])
            # type_rep = st.selectbox("Type de répartition :", ["Libre", "Par axe (Z)", "Par axe + angulaire", "Grille XY"])


            # cotes_associees = st.multiselect("Sélectionner les cotes associées à cette zone", st.session_state.df_cotes["Nom_Cote"].tolist())

            # points = []
            # for cote in cotes_associees:
            #     with st.expander(f"Cote : {cote}"):
            #         coord = {}
            #         if "axe" in type_rep.lower() or "z" in type_rep.lower():
            #             coord["Hauteur"] = st.number_input(f"Hauteur (mm) pour {cote}", key=f"h_{cote}")
            #         if "angulaire" in type_rep.lower():
            #             coord["Angle"] = st.number_input(f"Angle (°) pour {cote}", key=f"a_{cote}")
            #         if "grille" in type_rep.lower():
            #             coord["X"] = st.number_input(f"X pour {cote}", key=f"x_{cote}")
            #             coord["Y"] = st.number_input(f"Y pour {cote}", key=f"y_{cote}")
            #         valeur = st.number_input(f"Valeur mesurée pour {cote} ({type_mesure})", key=f"val_{cote}")
            #         points.append({"Nom_Cote": cote, "Coordonnées": coord, "Valeur_Mesurée": valeur})
