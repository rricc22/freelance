import streamlit as st

st.set_page_config(page_title="test", layout="wide")


import plotly.graph_objects as go
import numpy as np

# st.title("📏 Vue en coupe verticale angulaire")

# --- Paramètres
angles = [0, 60, 120, 180, 240, 300]
hauteurs = {
    "Rayon fond": 0,
    "Rayon intérieur": 50,
    "Rayon extérieur": 100,
}
cotes = {
    "Rayon fond": dict(base=40.0, tol_plus=40.1, tol_moins=39.9),
    "Rayon intérieur": dict(base=210.0, tol_plus=210.3, tol_moins=209.7),
    "Rayon extérieur": dict(base=275.0, tol_plus=275.1, tol_moins=274.8),
}

# --- Générer données simulées
for nom, val in cotes.items():
    val["mesures"] = np.round(np.random.normal(loc=val["base"], scale=0.05, size=6), 3)

# --- Sélecteur d’angle
angle_selectionne = st.selectbox("🎯 Choisissez un angle :", angles)
idx = angles.index(angle_selectionne)

# --- Graphique radar individuel
def radar_individuel(nom, mesures, tol_plus, tol_moins, base):
    mesures_c = list(mesures) + [mesures[0]]
    tol_plus_c = [tol_plus]*6 + [tol_plus]
    tol_moins_c = [tol_moins]*6 + [tol_moins]
    angles_c = angles + [angles[0]]

    # Calculer la plage autour de la valeur nominale
    centre = base
    marge = max(abs(tol_plus - base), abs(tol_moins - base)) + 0.1  # marge visuelle

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=mesures_c, theta=angles_c,
        mode='lines+markers', name="Mesure"
    ))
    fig.add_trace(go.Scatterpolar(
        r=tol_plus_c, theta=angles_c,
        mode='lines', name="Tolérance +",
        line=dict(dash='dot')
    ))
    fig.add_trace(go.Scatterpolar(
        r=tol_moins_c, theta=angles_c,
        mode='lines', name="Tolérance -",
        line=dict(dash='dot')
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[centre - marge, centre + marge]),
            angularaxis=dict(direction="clockwise")
        ),
        title=nom,
        height=300,
        margin=dict(l=30, r=30, t=40, b=20),
        showlegend=False,
        width=300,
    )
    return fig

# --- Graphique linéaire de coupe verticale
fig_section = go.Figure()
x_points = []
y_points = []

for nom, val in cotes.items():
    y = hauteurs[nom]
    x = val["mesures"][idx]
    tol_plus = val["tol_plus"]
    tol_moins = val["tol_moins"]

    x_points.append(x)
    y_points.append(y)

    fig_section.add_trace(go.Scatter(
        x=[x], y=[y],
        mode='markers+text',
        text=[nom], textposition="middle right",
        marker=dict(size=10),
        name=nom
    ))

    fig_section.add_shape(type="line", x0=tol_moins, x1=tol_plus, y0=y, y1=y,
                          line=dict(color="gray", dash="dot"))

# Ligne reliant les trois points
fig_section.add_trace(go.Scatter(
    x=x_points,
    y=y_points,
    mode='lines',
    name='Liaison verticale',
    line=dict(color='lightgreen', width=2)
))

# --- Graphe des écarts par rapport au nominal
fig_bar = go.Figure()
noms = []
deviations = []

for nom, val in cotes.items():
    nominal = val["base"]
    mesure = val["mesures"][idx]  # idx = angle sélectionné
    noms.append(nom)
    deviations.append(mesure - nominal)

fig_bar.add_trace(go.Bar(
    x=noms,
    y=deviations,
    text=[f"{dev:+.3f} mm" for dev in deviations],
    textposition="outside",
    marker_color=['red' if abs(dev) > 0.1 else 'green' for dev in deviations]
))

fig_bar.update_layout(
    title=f"📊 Écart par rapport au nominal à {angle_selectionne}°",
    xaxis_title="Rayon",
    yaxis_title="Écart (mm)",
    height=300
)


fig_section.update_layout(
    title=f"🧩 Coupe verticale à {angle_selectionne}°",
    xaxis_title="Mesure (mm)",
    yaxis_title="Hauteur",
    yaxis=dict(range=[-10, 110]),
    height=500
)
# --- Affichage
col1, col2 = st.columns([1.1, 1])
with col1:
    # 1. Coupe verticale
    st.plotly_chart(fig_section, use_container_width=True, key="graph_section",height=800)

    # 2. Graphe des écarts par rapport au nominal
    noms = []
    deviations = []
    couleurs = []

    for nom, val in cotes.items():
        nominal = val["base"]
        tol_plus = val["tol_plus"]
        tol_moins = val["tol_moins"]
        mesure = val["mesures"][idx]

        noms.append(nom)
        deviations.append(mesure - nominal)

        if mesure < tol_moins or mesure > tol_plus:
            couleurs.append("red")
        else:
            couleurs.append("lightgreen")

    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        x=noms,
        y=deviations,
        text=[f"{dev:+.3f} mm" for dev in deviations],
        textposition="outside",
        marker_color=couleurs
    ))

    fig_bar.update_layout(
        title=f"📊 Écart par rapport au nominal à {angle_selectionne}°",
        xaxis_title="Rayon",
        yaxis_title="Écart (mm)",
        height=450,
    )

    st.plotly_chart(fig_bar, use_container_width=True, key="graph_bar")

with col2:
    for i, (nom, val) in enumerate(cotes.items()):
        fig = radar_individuel(nom, val["mesures"], val["tol_plus"], val["tol_moins"], val["base"])
        st.plotly_chart(fig, use_container_width=True, key=f"radar_{i}")
