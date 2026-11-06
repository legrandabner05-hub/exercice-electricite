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
c1.metric("Consommation totale", f"{resultat['kwh'].sum() / 1_000_000:.2f} M kWh")
c2.metric("kWh par abonné", f"{resultat['kwh_par_abonne'].mean():.1f}")
c3.metric("Heures de courant (moy.)", f"{resultat['heures_courant'].mean():.1f} h")

# --- Onglets ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
"Quartiers", "Évolution", "Chaleur vs courant", "Coupures", "Pics"
])

# 1. Consommation par type
with tab1:
    st.subheader("kWh par abonné selon le type de quartier")
    moyennes_type = resultat.groupby("type")["kwh_par_abonne"].mean().round(1)
    st.bar_chart(moyennes_type, horizontal=True)
    st.write(f"Commercial : {moyennes_type.get('Commercial', 0):.1f} kWh/abonné, "
        f"Résidentiel : {moyennes_type.get('Résidentiel', 0):.1f} kWh/abonné.")
    
# 2. Évolution par commune
with tab2:
    st.subheader("Évolution du kWh par abonné, mois par mois et par commune")
    courbes = resultat.pivot_table(index="mois", columns="commune",
                                    values="kwh_par_abonne", aggfunc="mean")
st.line_chart(courbes)
totaux_commune = resultat.groupby("commune")["kwh"].sum() / 1_000_000
commune_top = totaux_commune.idxmax()
st.write(f"En {annee_selectionnee}, la commune la plus consommatrice est {commune_top} "
            f"avec {totaux_commune.max():.2f} M kWh.")

# 3. Chaleur ou courant
with tab3:
    st.subheader("Le courant disponible pèse plus que la température")
    residences = resultat[resultat["type"] == "Résidentiel"]
    st.scatter_chart(residences, x="heures_courant", y="kwh_par_abonne", color="commune",
                        x_label="Heures de courant par jour", y_label="kWh par abonné")
r_courant = residences["heures_courant"].corr(residences["kwh_par_abonne"])
r_temp = residences["temperature_c"].corr(residences["kwh_par_abonne"])
st.write(f"Résidentiel : corrélation de {r_courant:.2f} avec les heures de courant, "
        f"{r_temp:.2f} avec la température.")

# 4. Coupures
with tab4:
    st.subheader("Où les coupures durent-elles le plus longtemps ?")
    med_commune = resultat.groupby("commune")["heures_courant"].median().round(1)
    st.bar_chart(med_commune, horizontal=True)
    rares = resultat[resultat["heures_courant"] < 8]
    st.write(f"{len(rares)} relevé(s) sous 8 h de courant sur la période filtrée.")

# 5. Pics
with tab5:
    st.subheader("Top 5 des consommations les plus élevées")
    cinq = resultat.nlargest(5, "kwh")[["mois", "quartier", "type", "kwh"]]
    st.dataframe(cinq, hide_index=True)
    premier = cinq.iloc[0]
    st.write(f"Le pic se situe à {premier['quartier']} en {premier['mois']} "
                f"avec {premier['kwh']:.0f} kWh.")