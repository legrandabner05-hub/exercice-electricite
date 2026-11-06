from pathlib import Path

import pandas as pd
import streamlit as st

DOSSIER = Path(__file__).parent / "donnees"

@st.cache_data
def lire_donnees_propres():
    return pd.read_csv(DOSSIER / "consommation_propre.csv")

st.set_page_config(page_title="L'électricité dans 12 quartiers", page_icon="⚡", layout="wide")

st.title("L'électricité dans 12 quartiers")
st.caption("Relevés mensuels de janvier 2024 à décembre 2025. Données fictives.")

donnees_propres = lire_donnees_propres()

st.markdown(
    "Ce tableau de bord regroupe 279 relevés mensuels de consommation électrique "
    "répartis sur 12 quartiers de Port-au-Prince, Delmas, Pétion-Ville et Cap-Haïtien."
)
st.markdown(
    "La question posée : la consommation dépend-elle de la température ou des heures de courant ?"
)

# --- Filtres ---
liste_communes = sorted(donnees_propres["commune"].unique())
selection_communes = st.sidebar.multiselect(
"Communes", liste_communes, default=liste_communes
)
annee_selectionnee = st.sidebar.selectbox("Année", [2025, 2024])

if not selection_communes:
    st.warning("Aucune commune sélectionnée : choisissez-en au moins une à gauche.")
    st.stop()

resultat = donnees_propres[donnees_propres["commune"].isin(selection_communes)]
resultat = resultat[resultat["annee"] == annee_selectionnee]

# --- Indicateurs ---
c1, c2, c3 = st.columns(3)

total_mwh = resultat["kwh"].sum() / 1_000_000
moyenne_par_abonne = resultat["kwh_par_abonne"].mean()
moyenne_heures = resultat["heures_courant"].mean()

c1.metric("Consommation totale", f"{total_mwh:.2f} M kWh")
c2.metric("kWh par abonné", f"{moyenne_par_abonne:.1f}")
c3.metric("Heures de courant (moy.)", f"{moyenne_heures:.1f} h")

st.dataframe(resultat.head(10), hide_index=True)