import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
from streamlit_drawable_canvas import st_canvas
from io import StringIO
import altair as alt

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

# --- FONCTION D'IMPORT ---
def traiter_csv_brut(texte_csv, nom_type):
    try:
        df = pd.read_csv(StringIO(texte_csv), sep="\t")
        expected_cols = ["Date", "Serial", "OF", "Nom_Cote", "Mesure","Nominal", "Tolérance_Min", "Tolérance_Max"]
        if not all(col in df.columns for col in expected_cols):
            st.error(f"🛑 Colonnes attendues pour {nom_type} : {expected_cols}. Colonnes détectées : {df.columns.tolist()}")
            return None
        df["Mesure"] = df["Mesure"].astype(str).str.replace(",", ".").astype(float)
        df["Écart (mm)"] = df["Nominal"] - df["Mesure"]
        df["Écart (%)"] = 100 * df["Écart (mm)"] / df["Mesure"]
        df["Hors tolérance"] = ~df["Mesure"].between(df["Tolérance_Min"], df["Tolérance_Max"])
        return df
    except Exception as e:
        st.error(f"❌ Erreur de lecture des données pour {nom_type} : {e}")
        return None

# --- FONCTION DE PRÉPARATION ---
def preparer_donnees_comparaison(df_metal, df_cire):
    # Préparation des données pour la comparaison
    df_metal['Nom_Cote_Normalisé'] = df_metal['Nom_Cote']
    df_cire['Nom_Cote_Normalisé'] = df_cire['Nom_Cote'].str.replace("Cire_", "", regex=False)

    df_metal['Type'] = 'Métal'
    df_cire['Type'] = 'Cire'

    return pd.concat([df_metal, df_cire], ignore_index=True)

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
col1, col2 = st.columns(2)

with col1:
    st.subheader("📋 Données pour Métal")
    metal_text_input = st.text_area("Collez ici les données pour Métal copiées depuis Excel", height=300, key="metal")

with col2:
    st.subheader("📋 Données pour Cote Cire")
    cire_text_input = st.text_area("Collez ici les données pour Cote Cire copiées depuis Excel", height=300, key="cire")

# --- TRAITEMENT DES DEUX BLOCS ---
if metal_text_input:
    df_metal = traiter_csv_brut(metal_text_input, "Métal")
    if df_metal is not None:
        st.subheader("✅ Données analysées pour Métal")
        st.dataframe(df_metal, use_container_width=True)

if cire_text_input:
    df_cire = traiter_csv_brut(cire_text_input, "Cire")
    if df_cire is not None:
        st.subheader("✅ Données analysées pour Cire")
        st.dataframe(df_cire, use_container_width=True)

# --- APPEL DE LA FONCTION GRAPHIQUE ---
# Call the function if both datasets are available
if metal_text_input and cire_text_input:
    if df_metal is not None and df_cire is not None:
        afficher_graphique_comparaison(df_metal, df_cire)

# if metal_text_input and cire_text_input:
#     if df_metal is not None and df_cire is not None:
#         afficher_boxplot_comparaison(df_metal, df_cire)


# --- AFFICHAGE DES COTES LIÉES (GROUPES DE PROFIL) ---
st.subheader("📎 Groupes de cotes liées par tolérance de profil")

if "cotes_info" in st.session_state and "groupes_cotes" in st.session_state:
    
    if len(st.session_state.groupes_cotes) == 0:
        st.info("Aucun groupe de cotes liées n’a encore été défini.")
    else:
        # Affichage en cartes
        for idx, groupe in enumerate(st.session_state.groupes_cotes):
            st.markdown(f"### 🔹 Groupe {idx + 1}")

            cols = st.columns(len(groupe))
            for col, cote in zip(cols, groupe):
                info = st.session_state.cotes_info.get(cote, {})
                with col:
                    st.markdown(f"**Cote : `{cote}`**")
                    st.markdown(f"- Type : `{info.get('Type_Cote', '—')}`")
                    st.markdown(f"- Tolérances GPS : `{', '.join(info.get('Tolérances_GPS', [])) or '—'}`")

        # Affichage en tableau résumé
        st.markdown("### 🗂️ Tableau récapitulatif des groupes")
        group_rows = []
        for group_id, groupe in enumerate(st.session_state.groupes_cotes, 1):
            for cote in groupe:
                info = st.session_state.cotes_info.get(cote, {})
                group_rows.append({
                    "Groupe": group_id,
                    "Nom_Cote": cote,
                    "Type_Cote": info.get("Type_Cote", ""),
                    "Tolérances_GPS": ", ".join(info.get("Tolérances_GPS", []))
                })
        df_groupes = pd.DataFrame(group_rows)
        st.dataframe(df_groupes, use_container_width=True)

else:
    st.warning("Aucune information de groupe n’est disponible (session vide ?)")

# --- AFFICHAGE DES COTES LIÉES (GROUPES DE PROFIL) ---

st.subheader("📐 Profil de forme à partir des mesures réelles (métal & cire)")

if "groupes_cotes" in st.session_state and "cotes_info" in st.session_state:
    if df_metal is None or df_cire is None:
        st.warning("❗ Veuillez d'abord importer les données métal et cire.")
    elif not st.session_state.groupes_cotes:
        st.info("Aucun groupe de cotes liées n’est défini.")
    else:
        groupe = st.session_state.groupes_cotes[0]  # Premier groupe
        cotes_rayon = [c for c in groupe if c in st.session_state.cotes_info and st.session_state.cotes_info[c]["Type_Cote"] == "Rayon"]

        if len(cotes_rayon) < 2:
            st.warning("❗ Le groupe doit contenir au moins deux cotes de type 'Rayon'.")
        else:
            # Sélection des OF dispo
            of_cire_dispo = df_cire["OF"].unique().tolist()
            of_metal_dispo = df_metal["OF"].unique().tolist()

            col1, col2 = st.columns(2)
            with col1:
                of_cire_select = st.selectbox("Sélectionnez un OF (cire) :", of_cire_dispo)
            with col2:
                of_metal_select = st.selectbox("Sélectionnez un OF (métal) :", of_metal_dispo)

            # Normalisation des noms
            def normaliser(cote):
                return cote.replace("Cire_", "") if cote.startswith("Cire_") else cote

            # Fusion + préparation
            # Filtrage (remplacé multiselect par selectbox donc liste → simple str)
            df_cire_sel = df_cire[df_cire["OF"] == of_cire_select].copy()
            df_metal_sel = df_metal[df_metal["OF"] == of_metal_select].copy()

            def nettoyer_nom_cote(nom):
                return str(nom).replace("Cire_", "").replace(".", ",").strip()

            df_cire_sel["Nom_Cote_Normalisé"] = df_cire_sel["Nom_Cote"].apply(nettoyer_nom_cote)
            df_metal_sel["Nom_Cote_Normalisé"] = df_metal_sel["Nom_Cote"].apply(nettoyer_nom_cote)

            df_cire_sel["Type"] = "Cire"
            df_metal_sel["Type"] = "Métal"

            df_all = pd.concat([df_cire_sel, df_metal_sel], ignore_index=True)
            df_all = df_all[df_all["Nom_Cote_Normalisé"].isin(cotes_rayon)]
            df_all["OF_affiché"] = df_all["Type"] + " – " + df_all["OF"].astype(str)


            if df_all.empty:
                st.warning("Aucune donnée trouvée pour les cotes du groupe sélectionné.")
                st.write("🔍 Données combinées :", df_all)

                # st.write("🔍 Cotes rayon retenues :", cotes_rayon)
                # st.write("📊 Cotes disponibles dans les données :", df_cire_sel)

            else:
                # Attribution d’une position sur X
                mapping_hauteur = {cote: i * 50 for i, cote in enumerate(cotes_rayon)}  # espacés de 50 pour lisibilité
                df_all["Hauteur"] = df_all["Nom_Cote_Normalisé"].map(mapping_hauteur)

                # Fixer la tolérance de forme à ±0.5
                df_all["Nominal"] = df_all["Nominal"]
                df_all["Tol_min"] = df_all["Nominal"] - 0.5
                df_all["Tol_max"] = df_all["Nominal"] + 0.5
                df_all["Écart"] = df_all["Mesure"] - df_all["Nominal"]

                # Bande de tolérance
                bande_data = []
                for cote in cotes_rayon:
                    h = mapping_hauteur[cote]
                    nom = df_all[df_all["Nom_Cote_Normalisé"] == cote]["Nominal"].iloc[0]
                    bande_data.append({"Hauteur": h, "Nominal": nom, "Borne": nom - 0.5})
                    bande_data.append({"Hauteur": h, "Nominal": nom, "Borne": nom + 0.5})
                df_bande = pd.DataFrame(bande_data)

                bande = alt.Chart(df_bande).mark_area(opacity=0.1, color="green").encode(
                    x='Hauteur',
                    y='Borne',
                    y2='Nominal'
                )

                # Courbe par OF
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
                
