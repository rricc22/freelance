import streamlit as st
import pandas as pd
from io import StringIO


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

# --- LAYOUT ---

st.subheader("📋 Coller les données CSV depuis Excel")
text_input = st.text_area("Collez ici les données copiées depuis Excel", height=300)

if text_input:
    try:
        df = pd.read_csv(StringIO(text_input), sep="\t")

        # Vérification des colonnes attendues
        expected_cols = ["Date", "Serial", "OF", "Nom_Cote", "Mesure", "Nominal", "Tolérance_Min", "Tolérance_Max"]
        if not all(col in df.columns for col in expected_cols):
            st.error(f"❌ Colonnes attendues : {expected_cols}. Colonnes détectées : {df.columns.tolist()}")
        else:
            st.success("✅ Données chargées avec succès !")

            # Supprimer les doublons de Nom_Cote
            unique_cotes = df["Nom_Cote"].dropna().unique()

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


# --- LAYOUT ---

            st.subheader("🧩 Caractérisation des cotes principales")

            # Initialisation si besoin
            if "df_cotes" not in st.session_state or not set(st.session_state.df_cotes["Nom_Cote"]) == set(unique_cotes):
                st.session_state.df_cotes = pd.DataFrame({
                    "Nom_Cote": unique_cotes,
                    "Type_Cote": [None] * len(unique_cotes)
                })

            # Liste des types possibles
            types_possibles = ["Diamètre extérieur", "Alésage", "Épaisseur", "Rayon", "Longueur", "Angle", "Autre"]
            
            # Ajout d'une nouvelle structure pour les spécifications GPS
            gps_options = {
                "Forme": ["Planéité", "Rectitude", "Circularité", "Cylindricité"],
                "Orientation": ["Parallélisme", "Perpendicularité", "Inclinaison"],
                "Position": ["Position vraie", "Battement", "Symétrie"],
                "Autres": ["Rugosité", "Référentiel A", "Référentiel B"]
}
            # Création des colonnes
            col1, col2 = st.columns([1, 2])

            with col1:
                st.markdown("### 🛠️ Sélection du type et des tolérances GPS")

                for i, row in st.session_state.df_cotes.iterrows():
                    st.markdown(f"**🔹 Cote : {row['Nom_Cote']}**")

                    # Choix du type fonctionnel
                    type_choisi = st.selectbox(
                        "Type fonctionnel",
                        types_possibles,
                        index=types_possibles.index(row["Type_Cote"]) if row["Type_Cote"] in types_possibles else 0,
                        key=f"type_cote_{i}"
                    )
                    st.session_state.df_cotes.at[i, "Type_Cote"] = type_choisi

                    # Multiselect GPS fusionné
                    gps_flat_list = sum(gps_options.values(), [])  # liste aplatie
                    gps_key = f"gps_{i}"
                    gps_choix = st.multiselect("Tolérances GPS associées :", gps_flat_list, key=gps_key)
                    st.session_state.df_cotes.at[i, "Tolérances_GPS"] = ", ".join(gps_choix)

                    st.markdown("---")

            with col2:
                st.markdown("### 📊 Visualisation des cotes caractérisées")
                selected_type = st.selectbox("Filtrer par type de cote :", ["Tous"] + types_possibles)
                df_filtered = st.session_state.df_cotes if selected_type == "Tous" else st.session_state.df_cotes[st.session_state.df_cotes["Type_Cote"] == selected_type]
                st.dataframe(df_filtered)

    except Exception as e:
        st.error(f"Erreur lors du chargement des données : {e}")
