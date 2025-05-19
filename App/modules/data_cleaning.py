# import pandas as pd

# def nettoyer_donnees_brutes_excel(df_raw: pd.DataFrame) -> pd.DataFrame:
#     # Paramètres de structure
#     row_data_start = 10
#     column_data_start = 7

#     # Repères pour les tolérances
#     row_cote_names = 2
#     row_min = 5
#     row_aim = 6
#     row_max = 7

#     # Colonnes d'identification
#     column_datetime = 0
#     column_serial = 1
#     column_platcode = 5
#     column_of = 6

#     # Extraction des noms et tolérances
#     cote_names = df_raw.iloc[row_cote_names, column_data_start:].values
#     min_tol = df_raw.iloc[row_min, column_data_start:].values
#     aim_tol = df_raw.iloc[row_aim, column_data_start:].values
#     max_tol = df_raw.iloc[row_max, column_data_start:].values

#     # Extraction des infos générales
#     data_vals = df_raw.iloc[row_data_start:, column_data_start:]
#     data_vals.columns = cote_names

#     info_cols_sorted = df_raw.iloc[row_data_start:, [column_datetime, column_serial, column_platcode, column_of]].rename(
#         columns={column_datetime: "datetime", column_serial: "serial", column_platcode: "plantcode", column_of: "OF"}
#     )

#     # Transformation en format long
#     records = []
#     for idx, row in data_vals.iterrows():
#         info = info_cols_sorted.iloc[idx - row_data_start]
#         for i, val in enumerate(row):
#             records.append({
#                 "Date": info["datetime"],
#                 "Serial": info["serial"],
#                 "OF": info["OF"],
#                 "Nom_Cote": cote_names[i],
#                 "Mesure": val,
#                 "Nominal": aim_tol[i],
#                 "Tolérance_Min": min_tol[i],
#                 "Tolérance_Max": max_tol[i]
#             })

#     df_long = pd.DataFrame(records)
#     return df_long
import pandas as pd
from io import StringIO
import streamlit as st


def detect_type(nom):
    nom = nom.lower()
    if "rayon" in nom:
        return "Rayon"
    elif "diam" in nom or "ø" in nom:
        return "Diamètre extérieur"
    elif "épais" in nom or "patin" in nom:
        return "Épaisseur"
    elif "largeur" in nom or "hauteur" in nom or "gorge" in nom:
        return "Longueur"
    elif "perçage" in nom:
        return "Diamètre extérieur"
    elif "alésage" in nom:
        return "Alésage"
    elif "angle" in nom:
        return "Angle"
    else:
        return "Autre"

def nettoyer_donnees_brutes(text_input: str) -> pd.DataFrame:
    df_temp = pd.read_csv(StringIO(text_input), sep="\t", header=None)

    # --- Format brut ou structuré ?
    if df_temp.shape[0] > 12 and df_temp.shape[1] > 10 and "FCollAvg" not in df_temp.columns:
        # === Format BRUT détecté ===
        row_data_start = 10
        column_data_start = 7
        row_cote_names = 2
        row_min = 5
        row_aim = 6
        row_max = 7
        column_datetime = 0
        column_serial = 1
        column_platcode = 5
        column_of = 6

        cote_names = df_temp.iloc[row_cote_names, column_data_start:].values
        min_tol = df_temp.iloc[row_min, column_data_start:].values
        aim_tol = df_temp.iloc[row_aim, column_data_start:].values
        max_tol = df_temp.iloc[row_max, column_data_start:].values

        data_vals = df_temp.iloc[row_data_start:, column_data_start:]
        data_vals.columns = cote_names

        info_cols_sorted = df_temp.iloc[row_data_start:, [column_datetime, column_serial, column_platcode, column_of]].rename(
            columns={column_datetime: "datetime", column_serial: "serial", column_platcode: "plantcode", column_of: "OF"}
        )

        records = []
        for idx, row in data_vals.iterrows():
            info = info_cols_sorted.iloc[idx - row_data_start]
            for i, val in enumerate(row):
                records.append({
                    "Date": info["datetime"],
                    "Serial": info["serial"],
                    "OF": info["OF"],
                    "Nom_Cote": cote_names[i],
                    "Mesure": val,
                    "Nominal": aim_tol[i],
                    "Tolérance_Min": min_tol[i],
                    "Tolérance_Max": max_tol[i]
                })

        df_long = pd.DataFrame(records)

    else:
        # === Format STRUCTURÉ ===
        df_long = pd.read_csv(StringIO(text_input), sep="\t")
        df_long.columns = df_long.columns.str.strip()

    # === Validation colonnes attendues ===
    expected_cols = ["Date", "Serial", "OF", "Nom_Cote", "Mesure", "Nominal", "Tolérance_Min", "Tolérance_Max"]
    if not all(col in df_long.columns for col in expected_cols):
        raise ValueError(f"❌ Colonnes attendues : {expected_cols}. Colonnes détectées : {df_long.columns.tolist()}")

    # === Gestion de cotes_info global ===
    if "cotes_info" not in st.session_state:
        st.session_state.cotes_info = {}

    unique_cotes = df_long["Nom_Cote"].dropna().unique().tolist()
    for cote in unique_cotes:
        if cote not in st.session_state.cotes_info:
            st.session_state.cotes_info[cote] = {
                "Type_Cote": detect_type(cote),
                "Tolérances_GPS": [],
                "Groupe_Profil": None,
                "Position_Angulaire": "Non spécifié",
                "Angle_Degres": None
            }

    # Ajout des colonnes supplémentaires au DataFrame
    df_long["Angle_Degres"] = df_long["Nom_Cote"].map(
        lambda x: st.session_state.cotes_info.get(x, {}).get("Angle_Degres", None)
    )
    df_long["Type_Cote"] = df_long["Nom_Cote"].map(
        lambda x: st.session_state.cotes_info.get(x, {}).get("Type_Cote", detect_type(x))
    )

    return df_long
