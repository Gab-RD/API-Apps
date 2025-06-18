import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import pydeck as pdk

st.set_page_config(page_title="Recherche d’entreprises 🇫🇷", layout="wide")
st.title("🔍 Recherche d’entreprises en France")

# Saisie utilisateur
mot_cle = st.text_input("🔤 Mot-clé (activité, nom...)", value="Boulangerie")
ville = st.text_input("📍 Filtrer par ville ou département (optionnel)")
nb = st.slider("📄 Nombre d’entreprises à afficher", 5, 25, 10)

# Lancer la recherche
if st.button("Rechercher") and mot_cle:
    with st.spinner("⏳ Chargement des résultats..."):
        params = {"q": mot_cle, "per_page": nb}
        if ville:
            params["departement"] = ville

        url = "https://recherche-entreprises.api.gouv.fr/search"
        response = requests.get(url, params=params)
        data = response.json()
        entreprises = data.get("results", [])

        if entreprises:
            rows = []
            for e in entreprises:
                site = e.get("site_internet", "")
                adresse = e.get("adresse", "")
                rows.append({
                    "Nom": e.get("nom_complet", ""),
                    "SIREN": e.get("siren", ""),
                    "Date création": e.get("date_creation", ""),
                    "Statut": e.get("statut") or "Non précisé",
                    "Catégorie": e.get("categorie_entreprise", ""),
                    "Activité principale": e.get("activite_principale", ""),
                    "Adresse": e.get("adresse") or "Non renseignée",
                    "Site web": f"[{e.get('site_internet')}]({e.get('site_internet')})" if e.get("site_internet") else "Aucun",
                    "Convention collective": e.get("convention_collective_renseignee") or "Non renseignée",
                })

            df = pd.DataFrame(rows)
            st.success(f"{len(df)} entreprises trouvées pour « {mot_cle} »")

            st.dataframe(df.style.set_properties(**{'white-space': 'pre-wrap'}), use_container_width=True)

            # Télécharger CSV
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Télécharger les résultats au format CSV", csv, "entreprises.csv", "text/csv")
            

            # Graphe des activités principales
            if not df["Activité principale"].isnull().all():
                st.subheader("📊 Répartition des activités principales")
                fig, ax = plt.subplots(figsize=(5, 5))
                df["Activité principale"].value_counts().head(10).plot(kind="barh", ax=ax, color="#0083B8")
                ax.invert_yaxis()
                col1, col2 = st.columns([1, 1])  # col1 plus étroite
                with col1:
                    st.pyplot(fig)
        else:
            st.warning("😕 Aucune entreprise trouvée. Essaie un autre mot-clé ou une autre ville.")
         