import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go

st.set_page_config(page_title="test", layout="wide")

import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.title("📏 Analyse des rayons angulaires - Radar et Section")

# === Fonctions ===

def generer_radar(nom, base=275.0):
    angles = [0, 60, 120, 180, 240, 300]
    mesures = np.round(np.random.normal(loc=base, scale=0.05, size=6), 3).tolist()
    tol_plus = [base + 0.1] * 6
    tol_moins = [base - 0.2] * 6

    # Boucler
    angles_c = angles + [angles[0]]
    mesures_c = mesures + [mesures[0]]
    tol_plus_c = tol_plus + [tol_plus[0]]
    tol_moins_c = tol_moins + [tol_moins[0]]

    centre = np.mean(mesures + tol_plus + tol_moins)
    marge = 0.15
    r_min = centre - marge
    r_max = centre + marge

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=mesures_c, theta=angles_c, mode='lines+markers', name='Mesure', line=dict(width=3)))
    fig.add_trace(go.Scatterpolar(r=tol_plus_c, theta=angles_c, mode='lines', name='Tolérance +', line=dict(dash='dot')))
    fig.add_trace(go.Scatterpolar(r=tol_moins_c, theta=angles_c, mode='lines', name='Tolérance -', line=dict(dash='dot')))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[r_min, r_max]),
            angularaxis=dict(direction="clockwise")
        ),
        title=nom,
        showlegend=False,
        margin=dict(l=10, r=10, t=40, b=10)
    )
    return fig, angles, mesures, tol_plus, tol_moins

def section_lineaire_combinee(cotes):
    fig = go.Figure()
    colors = ['blue', 'green', 'red']

    for idx, (nom, base) in enumerate(cotes):
        angles = [0, 60, 120, 180, 240, 300]
        mesures = np.round(np.random.normal(loc=base, scale=0.05, size=6), 3).tolist()
        tol_plus = [base + 0.1] * 6
        tol_moins = [base - 0.2] * 6

        fig.add_trace(go.Scatter(
            x=angles, y=mesures,
            mode='lines+markers',
            name=f'{nom} - Mesure',
            line=dict(color=colors[idx])
        ))

        fig.add_trace(go.Scatter(
            x=angles, y=tol_plus,
            mode='lines',
            name=f'{nom} - Tol+',
            line=dict(color=colors[idx], dash='dot'),
            showlegend=False
        ))

        fig.add_trace(go.Scatter(
            x=angles, y=tol_moins,
            mode='lines',
            name=f'{nom} - Tol-',
            line=dict(color=colors[idx], dash='dot'),
            showlegend=False
        ))

    fig.update_layout(
        title="📈 Comparaison des sections angulaires",
        xaxis_title="Angle (°)",
        yaxis_title="Mesure",
        legend_title="Cotes",
        height=450
    )
    return fig

# === Données simulées ===
cotes = [
    ("Rayon extérieur ANGx", 275.0),
    ("Rayon intérieur ANGx", 210.0),
    ("Rayon fond ANGx", 40.0)
]

# === Mise en page deux colonnes ===
col_gauche, col_droite = st.columns([1.1, 1])

with col_gauche:
    st.markdown("### 🔎 Vue linéaire combinée")
    fig_section = section_lineaire_combinee(cotes)
    st.plotly_chart(fig_section, use_container_width=True)

with col_droite:
    st.markdown("### 🌟 Graphiques en étoile")
    for nom, base in cotes:
        fig_radar, *_ = generer_radar(nom, base)
        st.plotly_chart(fig_radar, use_container_width=True)
