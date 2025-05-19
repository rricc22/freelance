import pandas as pd

def nettoyer_donnees_brutes_excel(df_raw: pd.DataFrame) -> pd.DataFrame:
    # Paramètres de structure
    row_data_start = 10
    column_data_start = 7

    # Repères pour les tolérances
    row_cote_names = 2
    row_min = 5
    row_aim = 6
    row_max = 7

    # Colonnes d'identification
    column_datetime = 0
    column_serial = 1
    column_platcode = 5
    column_of = 6

    # Extraction des noms et tolérances
    cote_names = df_raw.iloc[row_cote_names, column_data_start:].values
    min_tol = df_raw.iloc[row_min, column_data_start:].values
    aim_tol = df_raw.iloc[row_aim, column_data_start:].values
    max_tol = df_raw.iloc[row_max, column_data_start:].values

    # Extraction des infos générales
    data_vals = df_raw.iloc[row_data_start:, column_data_start:]
    data_vals.columns = cote_names

    info_cols_sorted = df_raw.iloc[row_data_start:, [column_datetime, column_serial, column_platcode, column_of]].rename(
        columns={column_datetime: "Date", column_serial: "Serial", column_platcode: "plantcode", column_of: "OF"}
    )

    # Conversion explicite de la colonne Date en format AAAA-MM-JJ (YYYY-MM-DD)
    info_cols_sorted["Date"] = pd.to_datetime(info_cols_sorted["Date"], errors="coerce", dayfirst=True).dt.strftime("%Y-%m-%d")
    info_cols_sorted["Date"] = info_cols_sorted["Date"].fillna("")

    # Transformation en format long
    records = []
    for idx, row in data_vals.iterrows():
        info = info_cols_sorted.iloc[idx - row_data_start]
        for i, val in enumerate(row):
            records.append({
                "Date": info["Date"],
                "Serial": info["Serial"],
                "OF": info["OF"],
                "Nom_Cote": cote_names[i],
                "Mesure": val,
                "Nominal": aim_tol[i],
                "Tolérance_Min": min_tol[i],
                "Tolérance_Max": max_tol[i]
            })

    df_long = pd.DataFrame(records)
    return df_long
