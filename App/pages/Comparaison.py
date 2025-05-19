import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
from streamlit_drawable_canvas import st_canvas
from io import StringIO
import altair as alt
from modules.data_cleaning import nettoyer_donnees_brutes

# --- CONFIG ---
st.set_page_config(page_title="Comparaison", layout="wide")
st.title("📊 Comparaison des Données")


# Vérifie que le type d’analyse est bien “stat rapide”
if st.session_state.get("type_analyse") != "Comparaison (cire / métal, ScanBox / CMM, etc.)":
    st.error("❌ Cette page est réservée à la comparaison dimensionnelle.")
    st.stop()

# 🔁 Chargement d'un fichier JSON de caractérisation si disponible
st.sidebar.markdown("## 📂 Charger les données caractéristiques")
uploaded_json = st.sidebar.file_uploader("Fichier JSON des cotes (cotes_info.json)", type="json")

if uploaded_json is not None:
    import json
    try:
        loaded_info = json.load(uploaded_json)
        st.session_state.cotes_info = loaded_info

        # Reconstruire groupes à partir des tags Groupe_Profil
        groupes = {}
        for cote, infos in loaded_info.items():
            group = infos.get("Groupe_Profil")
            if group:
                groupes.setdefault(group, []).append(cote)
        st.session_state.groupes_cotes = list(groupes.values())

        st.sidebar.success("✅ Données chargées avec succès.")
    except Exception as e:
        st.sidebar.error(f"Erreur lors du chargement du JSON : {e}")

# --- FONCTION DE PRÉPARATION ---
def preparer_donnees_comparaison(df_metal, df_cire):
    df_metal['Nom_Cote_Normalisé'] = df_metal['Nom_Cote']
    df_cire['Nom_Cote_Normalisé'] = df_cire['Nom_Cote'].str.replace("Cire_", "", regex=False)
    df_metal['Type'] = 'Métal'
    df_cire['Type'] = 'Cire'
    return pd.concat([df_metal, df_cire], ignore_index=True)

def traiter_df_comparaison(df: pd.DataFrame, nom_type="Données"):
    try:
        expected_cols = ["Date", "Serial", "OF", "Nom_Cote", "Mesure", "Nominal", "Tolérance_Min", "Tolérance_Max"]
        if not all(col in df.columns for col in expected_cols):
            st.error(f"🛑 Colonnes attendues pour {nom_type} : {expected_cols}. Colonnes détectées : {df.columns.tolist()}")
            return None

        # ✅ Conversion des colonnes numériques
        for col in ["Mesure", "Nominal", "Tolérance_Min", "Tolérance_Max"]:
            df[col] = df[col].astype(str).str.replace(",", ".").astype(float)

        df["Écart (mm)"] = df["Mesure"] - df["Nominal"]
        df["Écart (%)"] = 100 * df["Écart (mm)"] / df["Nominal"]
        df["Hors tolérance"] = ~df["Mesure"].between(df["Tolérance_Min"], df["Tolérance_Max"])
        return df
    except Exception as e:
        st.error(f"❌ Erreur de traitement pour {nom_type} : {e}")
        return None


# --- FONCTION GRAPHIQUE ---
def afficher_graphique_comparaison(df_metal, df_cire):
    # Préparation
    df_comparaison = preparer_donnees_comparaison(df_metal, df_cire)

    st.subheader("📉 Distribution des mesures par cote (toutes pièces)")

    # Sélection du nom de cote
    selected_nom_cote = st.selectbox(
        "Sélectionnez un nom de cote :", 
        df_comparaison["Nom_Cote_Normalisé"].unique()
    )

    # Filtrage
    df_graph = df_comparaison[df_comparaison["Nom_Cote_Normalisé"] == selected_nom_cote]

    # Ajout bande de tolérance (une seule paire pour le graphe)
    tol_min = df_graph["Tolérance_Min"].iloc[0]
    tol_max = df_graph["Tolérance_Max"].iloc[0]
    band = alt.Chart(pd.DataFrame({'y': [tol_min], 'y2': [tol_max]})).mark_rect(opacity=0.1, color='green').encode(
        y='y:Q',
        y2='y2:Q'
    )

    # Chart avec points
    chart = alt.Chart(df_graph).mark_circle(size=60).encode(
        x=alt.X('OF:N', title='Ordre de Fabrication (OF)', sort=alt.EncodingSortField(field="OF", order="ascending")),
        y=alt.Y('Mesure:Q', title='Mesure (mm)', scale=alt.Scale(zero=False)),
        color=alt.Color('Type:N', title='Type'),
        shape=alt.Shape('Type:N'),
        tooltip=['Serial', 'OF', 'Type', 'Mesure', 'Nominal', 'Tolérance_Min', 'Tolérance_Max']
    ).properties(
        title=f"Comparaison des Mesures pour {selected_nom_cote}",
        width=800,
        height=400
    ).interactive()

    # Fusion bande de tolérance + données
    final_chart = band + chart
    st.altair_chart(final_chart, use_container_width=True)

    # Alerte auto si écart moyen > seuil
    df_metal_sel = df_graph[df_graph["Type"] == "Métal"]
    df_cire_sel = df_graph[df_graph["Type"] == "Cire"]

    if not df_metal_sel.empty and not df_cire_sel.empty:
        moyenne_metal = df_metal_sel["Mesure"].mean()
        moyenne_cire = df_cire_sel["Mesure"].mean()
        ecart_moyen = abs(moyenne_metal - moyenne_cire)

        if ecart_moyen > 0.05:
            st.warning(f"⚠️ L'écart moyen entre métal et cire pour la cote '{selected_nom_cote}' est de {ecart_moyen:.3f} mm.")

def afficher_boxplot_comparaison(df_metal, df_cire):
    st.subheader("📦 Boxplot des mesures par cote")

    # Préparer les données
    df_comparaison = preparer_donnees_comparaison(df_metal, df_cire)

    selected_nom_cote = st.selectbox(
        "Sélectionnez une cote pour afficher le boxplot :",
        df_comparaison["Nom_Cote_Normalisé"].unique(),
        key="boxplot_select"
    )

    df_graph = df_comparaison[df_comparaison["Nom_Cote_Normalisé"] == selected_nom_cote]

    box = alt.Chart(df_graph).mark_boxplot(extent='min-max').encode(
        x=alt.X('Type:N', title='Type (Cire ou Métal)'),
        y=alt.Y('Mesure:Q', title='Mesure (mm)', scale=alt.Scale(zero=False)),
        color=alt.Color('Type:N', title='Type')
    )

    points = alt.Chart(df_graph).mark_circle(size=60, opacity=0.4).encode(
        x='Type:N',
        y='Mesure:Q',
        color='Type:N',
        tooltip=['Serial', 'OF', 'Mesure', 'Nominal']
    )

    st.altair_chart((box + points).properties(
        width=600,
        height=400,
        title=f"📦 Boxplot des mesures pour la cote : {selected_nom_cote}"
    ), use_container_width=True)

# --- LAYOUT ---
tab1, tab2 = st.tabs(["📂 Données métal", "🕯️ Données cire"])

df_cire, df_metal = None, None

with tab1:
    texte_metal = st.text_area("Collez ici les données pour Métal copiées depuis Excel", height=300, key="metal")
    if texte_metal.strip():
        try:
            df_metal_base = nettoyer_donnees_brutes(texte_metal)
            df_metal = traiter_df_comparaison(df_metal_base.copy(), nom_type="Métal")
            st.success("✅ Données métal prêtes !")
            st.dataframe(df_metal, use_container_width=True)
        except Exception as e:
            st.error(f"Erreur données métal : {e}")

with tab2:
    texte_cire = st.text_area("Collez ici les données pour Cire copiées depuis Excel", height=300, key="cire")
    if texte_cire.strip():
        try:
            df_cire_base = nettoyer_donnees_brutes(texte_cire)
            df_cire = traiter_df_comparaison(df_cire_base.copy(), nom_type="Cire")
            st.success("✅ Données cire prêtes !")
            st.dataframe(df_cire, use_container_width=True)
        except Exception as e:
            st.error(f"Erreur données cire : {e}")

if df_metal is not None and df_cire is not None:
    afficher_graphique_comparaison(df_metal, df_cire)
    afficher_boxplot_comparaison(df_metal, df_cire)

# --- AFFICHAGE DES COTES LIÉES (GROUPES DE PROFIL) ---
st.subheader("📐 Profil de forme à partir des mesures réelles (métal & cire)")

if "groupes_cotes" in st.session_state and "cotes_info" in st.session_state:
    if df_metal is None or df_cire is None:
        st.warning("Veuillez d'abord importer les données métal et cire.")
        
    elif not st.session_state.groupes_cotes:
        st.info("Aucun groupe de cotes liées n’est défini.")
    else:
        groupe = st.session_state.groupes_cotes[0]
        cotes_rayon = [c for c in groupe if c in st.session_state.cotes_info and st.session_state.cotes_info[c]["Type_Cote"] == "Rayon"]

        if len(cotes_rayon) < 2:
            st.warning("❗ Le groupe doit contenir au moins deux cotes de type 'Rayon'.")
        else:
            of_cire_dispo = df_cire["OF"].unique().tolist()
            of_metal_dispo = df_metal["OF"].unique().tolist()

            col1, col2 = st.columns(2)
            with col1:
                of_cire_select = st.selectbox("Sélectionnez un OF (cire) :", of_cire_dispo)
            with col2:
                of_metal_select = st.selectbox("Sélectionnez un OF (métal) :", of_metal_dispo)

            def nettoyer_nom_cote(nom):
                return str(nom).replace("Cire_", "").replace(".", ",").strip()

            df_cire_sel = df_cire[df_cire["OF"] == of_cire_select].copy()
            df_metal_sel = df_metal[df_metal["OF"] == of_metal_select].copy()

            df_cire_sel["Nom_Cote_Normalisé"] = df_cire_sel["Nom_Cote"].apply(nettoyer_nom_cote)
            df_metal_sel["Nom_Cote_Normalisé"] = df_metal_sel["Nom_Cote"].apply(nettoyer_nom_cote)

            df_cire_sel["Type"] = "Cire"
            df_metal_sel["Type"] = "Métal"

            df_all = pd.concat([df_cire_sel, df_metal_sel], ignore_index=True)
            df_all = df_all[df_all["Nom_Cote_Normalisé"].isin(cotes_rayon)]
            df_all["OF_affiché"] = df_all["Type"] + " – " + df_all["OF"].astype(str)

            # === DEBUG ===
            colonnes_obligatoires = ["Nom_Cote_Normalisé", "Mesure", "Nominal", "Type", "OF"]
            missing_cols = [col for col in colonnes_obligatoires if col not in df_all.columns]
            if missing_cols:
                st.error(f"❌ Colonnes manquantes dans df_all : {missing_cols}")

            if df_all.isnull().any().any():
                st.warning("⚠️ Des valeurs manquantes détectées dans df_all")
                st.dataframe(df_all[df_all.isnull().any(axis=1)])

            if df_all.empty:
                st.warning("Aucune donnée trouvée pour les cotes du groupe sélectionné.")
                st.write("🔍 df_all (vide) :", df_all)
            else:
                mapping_hauteur = {cote: i * 50 for i, cote in enumerate(cotes_rayon)}
                df_all["Hauteur"] = df_all["Nom_Cote_Normalisé"].map(mapping_hauteur)

                df_all["Tol_min"] = df_all["Nominal"] - 0.5
                df_all["Tol_max"] = df_all["Nominal"] + 0.5
                df_all["Écart"] = df_all["Mesure"] - df_all["Nominal"]

                # Tolérances visuelles
                bande_data = []
                for cote in cotes_rayon:
                    try:
                        h = mapping_hauteur[cote]
                        nom = df_all[df_all["Nom_Cote_Normalisé"] == cote]["Nominal"].dropna().iloc[0]
                        bande_data.append({"Hauteur": h, "Nominal": nom, "Borne": nom - 0.5})
                        bande_data.append({"Hauteur": h, "Nominal": nom, "Borne": nom + 0.5})
                    except IndexError:
                        st.warning(f"⚠️ Cote {cote} manquante dans df_all pour le tracé")

                df_bande = pd.DataFrame(bande_data)

                bande = alt.Chart(df_bande).mark_area(opacity=0.1, color="green").encode(
                    x='Hauteur',
                    y='Borne',
                    y2='Nominal'
                )

                ligne = alt.Chart(df_all).mark_line(point=True).encode(
                    x='Hauteur',
                    y=alt.Y('Écart', scale=alt.Scale(domain=[-0.6, 0.6]), title="Écart par rapport au nominal (mm)"),
                    color='Type:N',
                    strokeDash='OF_affiché:N',
                    tooltip=['Nom_Cote_Normalisé', 'OF', 'Type', 'Mesure', 'Nominal']
                ).properties(
                    width=700,
                    height=400,
                    title="Profil de forme – Données mesurées"
                )

                st.altair_chart(bande + ligne, use_container_width=True)

                
