import streamlit as st
import trimesh
import plotly.graph_objects as go
import os
import math
import time

st.set_page_config(layout="wide")

st.header("🧩 Caractérisation de la pièce")

col1, col2 = st.columns([1, 2])

with col1:
    type_piece = st.selectbox(
        "Quel type de pièce analysez-vous ?",
        ["Support palier", "Nozzle", "Distributeur", "Roues", "Barettes", "Pales", "Autre (forme libre)"]
    )
    st.session_state["type_piece"] = type_piece

# Angle de la caméra (stocké entre les reruns)
if "angle" not in st.session_state:
    st.session_state.angle = 0

with col2:
    st.subheader("🔎 Visualisation 3D tournante")

    chemin_fichier = "static/Jet_Engine_Fan-Blades.stl"

    if os.path.exists(chemin_fichier):
        mesh = trimesh.load_mesh(chemin_fichier)

        # Position de la caméra qui tourne autour de l'axe Y
        r = 2.5  # rayon
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

        # Mise à jour de l'angle pour la prochaine frame
        st.session_state.angle = (st.session_state.angle + 3) % 360
        time.sleep(0.1)
        st.experimental_rerun()
    else:
        st.warning("Fichier STL introuvable.")


# st.header("🧩 Caractérisation de la pièce")

# col1, col2 = st.columns([1, 2])

# with col1:
#     type_piece = st.selectbox(
#         "Quel type de pièce analysez-vous ?",
#         ["Support palier", "Nozzle", "Distributeur", "Roues", "Barettes", "Pales", "Autre (forme libre)"]
#     )
#     st.session_state["type_piece"] = type_piece
# st.subheader("🔎 Visualisation 3D")
# nom_fichier_stl = type_piece.replace(" ", "_").lower() + ".stl"
# chemin_url = f"/static/Jet_Engine_Fan-Blades.stl"
# chemin_fichier = os.path.join("static", "Jet_Engine_Fan-Blades.stl")

# if os.path.exists(chemin_fichier):
#     st.components.v1.html(f"""
#     <script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script>
#     <model-viewer src="{chemin_url}"
#                     alt="Modèle 3D {type_piece}"
#                     auto-rotate
#                     camera-controls
#                     background-color="#F0F0F0"
#                     style="width: 100%; height: 500px;">
#     </model-viewer>
#     """, height=520)
# else:
#     st.info("🛑 Aucun modèle 3D disponible pour cette pièce.")
