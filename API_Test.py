import streamlit as st
import requests
import pandas as pd

st.title("🔍 Recherche d’entreprises en France")

# Saisie de l'utilisateur
mot_cle = st.text_input("Entrez un mot-clé (activité, nom, etc.)", value="boulangerie")
nb = st.slider("Nombre d’entreprises à afficher", 5, 50, 10)

# Lancer la recherche
if st.button("Rechercher") and mot_cle:
    with st.spinner("Chargement des résultats..."):
        url = "https://recherche-entreprises.api.gouv.fr/search"
        params = {"q": mot_cle, "per_page": nb}
        response = requests.get(url, params=params)
        data = response.json()
        entreprises = data.get("results", [])

        if entreprises:
            rows = []
            for e in entreprises:
                rows.append({
                    "Nom de l'entreprise": e.get("nom_complet", ""),
                    "SIREN": e.get("siren", ""),
                    "Date de création": e.get("date_creation", ""),
                    "Statut": e.get("statut", ""),
                    "Catégorie": e.get("categorie_entreprise", ""),
                    "Activité principale": e.get("activite_principale", ""),
                    "Adresse": e.get("adresse", ""),
                    "Site web": e.get("site_internet", ""),
                    "Convention collective": e.get("convention_collective_renseignee", "")
                })

            df = pd.DataFrame(rows)
            st.success(f"{len(df)} entreprises trouvées pour « {mot_cle} »")
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("Aucune entreprise trouvée.")
