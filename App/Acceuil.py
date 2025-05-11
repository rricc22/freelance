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

# Sauvegarde dans session_state pour les autres pages
st.session_state["type_piece"] = type_piece
st.session_state["type_analyse"] = type_analyse

if type_analyse == "Étude statistique rapide (vie série)":
    st.success("✅ Vous avez sélectionné : **Étude statistique rapide**.")
    st.markdown("👉 Cliquez sur l’onglet **AnalyseStatRapide** dans la **barre latérale** pour lancer l’analyse.")

elif type_analyse == "Comparaison (cire / métal, ScanBox / CMM, etc.)":
    st.success("✅ Vous avez sélectionné : **Comparaison** dimensionnelle.")
    st.markdown("👉 Cliquez sur l’onglet **Comparaison** dans la **barre latérale** pour lancer l’analyse.")
else:
    st.warning("⚠️ Le type d’analyse sélectionné n’est pas encore pris en charge dans cette version.")

