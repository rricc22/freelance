import streamlit as st
import pandas as pd
import numpy as np
import os
from io import StringIO

# --- CONFIG ---
st.set_page_config(page_title="Étude dimensionnelle", layout="wide")
st.title("📏 Dashboard d'Étude Dimensionnelle")

# --- SIDEBAR ---
st.sidebar.header("📂 Options")
image_folder = st.sidebar.text_input("Dossier des vues CAO (images)", "images/")

# --- MAIN ---
st.subheader("📋 Coller les données CSV depuis Excel")
text_input = st.text_area("Collez ici les données copiées depuis Excel", height=300)

if text_input:
    try:
        df = pd.read_csv(StringIO(text_input), sep="\t")

        # Vérification des colonnes attendues
        expected_cols = ["Datetime", "Serial", "OF", "Cote", "Mesure_Theorique", "Tolérance_Min", "Tolérance_Max"]
        if not all(col in df.columns for col in expected_cols):
            st.error(f"Colonnes attendues : {expected_cols}. Colonnes détectées : {df.columns.tolist()}")
        else:
            # Nettoyage des valeurs de cote (virgule à point si besoin)
            df["Cote"] = df["Cote"].astype(str).str.replace(",", ".").astype(float)

            # Calculs élémentaires
            df["Écart (mm)"] = df["Mesure_Theorique"] - df["Cote"]
            df["Écart (%)"] = 100 * df["Écart (mm)"] / df["Cote"]
            df["Hors tolérance"] = ~df["Mesure_Theorique"].between(df["Tolérance_Min"], df["Tolérance_Max"])

            # --- Sélection OF ---
            st.subheader("📊 Données Mesure")
            selected_of = st.selectbox("Sélectionnez un OF :", df["OF"].astype(str).unique())
            df_filtered = df[df["OF"].astype(str) == selected_of]

            st.dataframe(df_filtered, use_container_width=True)

            # --- IMAGE ---
            st.subheader("🖼️ Vue CAO associée")
            image_path = os.path.join(image_folder, f"{selected_of}.png")
            if os.path.exists(image_path):
                st.image(image_path, caption=f"Vue CAO de l'OF {selected_of}", use_column_width=True)
            else:
                st.warning(f"Image non trouvée pour l'OF {selected_of} dans {image_folder}")

            # --- STATISTIQUES PAR COTE ---
            st.subheader("📈 Statistiques par cote")

            def compute_stats(group):
                if len(group) < 2:
                    return pd.Series({
                        "N Mesures": len(group),
                        "Moyenne": group["Mesure_Theorique"].mean(),
                        "Écart-type": np.nan,
                        "Écart moyen absolu": group["Écart (mm)"].abs().mean(),
                        "Cp": np.nan,
                        "Cpk": np.nan,
                        "% hors tolérance": 100 * group["Hors tolérance"].mean()
                    })
                else:
                    std = group["Mesure_Theorique"].std()
                    mean = group["Mesure_Theorique"].mean()
                    tol_min = group["Tolérance_Min"].iloc[0]
                    tol_max = group["Tolérance_Max"].iloc[0]
                    cp = (tol_max - tol_min) / (6 * std) if std > 0 else np.nan
                    cpk = min(tol_max - mean, mean - tol_min) / (3 * std) if std > 0 else np.nan

                    return pd.Series({
                        "N Mesures": len(group),
                        "Moyenne": mean,
                        "Écart-type": std,
                        "Écart moyen absolu": group["Écart (mm)"].abs().mean(),
                        "Cp": cp,
                        "Cpk": cpk,
                        "% hors tolérance": 100 * group["Hors tolérance"].mean()
                    })


            stats_df = df_filtered.groupby("Cote").apply(compute_stats).reset_index()
            st.dataframe(
                stats_df.style.format({
                    "Moyenne": "{:.3f}",
                    "Écart-type": "{:.3f}",
                    "Écart moyen absolu": "{:.3f}",
                    "Cp": "{:.2f}",
                    "Cpk": "{:.2f}",
                    "% hors tolérance": "{:.1f} %"
                }),
                use_container_width=True
                )

    except Exception as e:
        st.error(f"Erreur de lecture des données : {e}")
else:
    st.info("Veuillez copier-coller les données depuis Excel avec les colonnes correctes.")
