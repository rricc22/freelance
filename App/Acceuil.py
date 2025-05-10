import streamlit as st

st.set_page_config(page_title="Accueil - Étude dimensionnelle", layout="wide")
st.title("🏭 Outil d'Étude Dimensionnelle")

st.header("🧩 Caractérisation de la pièce")

type_piece = st.selectbox(
    "Quel type de pièce analysez-vous ?",
    ["Je ne sais pas", "Pièce de révolution entière", "Pièce de révolution partielle", 
     "Autre (forme libre)", "Support palier", "Nozzle", "Distributeur"]
)

type_analyse = st.radio(
    "Quel est le type d’analyse souhaité ?",
    [
        "Étude statistique rapide (vie série)",
        "Comparaison (cire / métal, ScanBox / CMM, etc.)",
        "Étude des dérives (vie série)",
        "Étude dimensionnelle (développement pièce)"
    ]
)

# Sauvegarde dans session_state pour partage avec d'autres pages
st.session_state["type_piece"] = type_piece
st.session_state["type_analyse"] = type_analyse

if type_analyse == "Étude statistique rapide (vie série)":
    if st.button("🔄 Aller à l'analyse statistique rapide"):
        st.session_state["page"] = "AnalyseStatRapide"
        st.stop()
else:
    st.warning("⚠️ Le type d’analyse sélectionné n’est pas encore pris en charge dans cette version.")

# Handle navigation based on session state
if "page" in st.session_state and st.session_state["page"] == "AnalyseStatRapide":
    st.write("🔄 Redirection vers AnalyseStatRapide...")
    # Add logic to load AnalyseStatRapide page here
