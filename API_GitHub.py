import requests as rqst
import pandas as pd
import streamlit as st
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
import matplotlib.pyplot as plt

load_dotenv()
token = os.getenv("GITHUB_TOKEN")
if not token:
    st.error("Le token GITHUB_TOKEN est manquant.")
    st.stop()

headers = {
    "Authorization": f"token {token}",
    "Accept": "application/vnd.github+json"
}

owner = "Shubhamsaboo"
repo = "awesome-llm-apps"
url = f"https://api.github.com/repos/{owner}/{repo}/pulls?state=closed&per_page=100"
limit_date = datetime.now(timezone.utc) - timedelta(days=365)

response = rqst.get(url, headers=headers)
if response.status_code != 200:
    st.error(f"Erreur API GitHub ({response.status_code})")
    st.stop()

data = response.json()
merged_rows = []
closed_rows = []

for pr in data:
    merged_at = pr.get("merged_at")
    closed_at = pr.get("closed_at")
    if merged_at:
        merged_date = datetime.strptime(merged_at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        if merged_date >= limit_date:
            merged_rows.append([pr["number"], pr["title"], pr["user"]["login"], merged_at[:10], pr["html_url"]])
    if closed_at:
        closed_date = datetime.strptime(closed_at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        if closed_date >= limit_date:
            closed_rows.append([pr["number"], pr["title"], pr["user"]["login"], closed_at[:10], pr["html_url"]])

merged_df = pd.DataFrame(merged_rows, columns=["Numéro", "Titre", "Auteur", "Date de merge", "Lien"])
closed_df = pd.DataFrame(closed_rows, columns=["Numéro", "Titre", "Auteur", "Date de fermeture", "Lien"])


st.title("Pull Requests GitHub – 12 derniers mois")
st.caption(f"Dépôt : {owner}/{repo}")

col1, col2 = st.columns(2)

with col1:
    st.subheader("PR mergées")
    if not merged_df.empty:
        st.dataframe(merged_df, use_container_width=True)
    else:
        st.info("Aucune PR mergée.")

with col2:
    st.subheader("PR fermées")
    if not closed_df.empty:
        st.dataframe(closed_df, use_container_width=True)
    else:
        st.info("Aucune PR fermée.")

with st.expander("📁 Options (affichage)", expanded=False):
    auteur = st.text_input("Filtrer par auteur")
    plage = st.selectbox("Plage de temps", ["30 derniers jours", "6 mois", "12 mois"])
    afficher_merged = st.checkbox("Afficher PR mergées", value=True)
    afficher_closed = st.checkbox("Afficher PR fermées", value=True)
    afficher_graph_merged = st.checkbox("Afficher Graphique PR mergées", value=True)
    afficher_graph_closed = st.checkbox("Afficher Graphique PR fermées", value=True)
    bouton_reload = st.button("🔄 Rafraîchir les données")

if afficher_graph_merged or afficher_graph_closed :
    st.subheader("📊 Répartition des PR par auteurs")

    col1, col2, col3 = st.columns([1, 2, 1])

    if afficher_graph_merged and afficher_graph_closed == False:
        with col2:
            st.markdown("#### PR mergées")
            fig1, ax1 = plt.subplots(figsize=(5, 5))
            merged_df["Auteur"].value_counts().head(10).plot(kind="barh", ax=ax1, color="#0083B8")
            ax1.invert_yaxis()
            st.pyplot(fig1)
    elif afficher_graph_merged and afficher_graph_closed:
        with col1:
            st.markdown("#### PR mergées")
            fig1, ax1 = plt.subplots(figsize=(5, 5))
            merged_df["Auteur"].value_counts().head(10).plot(kind="barh", ax=ax1, color="#0083B8")
            ax1.invert_yaxis()
            st.pyplot(fig1)

    if afficher_graph_closed and afficher_graph_merged == False:
        with col2:
            st.markdown("#### PR fermées")
            fig2, ax2 = plt.subplots(figsize=(5, 5))
            closed_df["Auteur"].value_counts().head(10).plot(kind="barh", ax=ax2, color="#0083B8")
            ax2.invert_yaxis()
            st.pyplot(fig2)
    elif afficher_graph_closed and afficher_graph_merged :
        with col3:
            st.markdown("#### PR fermées")
            fig2, ax2 = plt.subplots(figsize=(5, 5))
            closed_df["Auteur"].value_counts().head(10).plot(kind="barh", ax=ax2, color="#0083B8")
            ax2.invert_yaxis()
            st.pyplot(fig2)


st.markdown("""
    <style>
        /* 🔧 Réserve l'espace pour la sidebar sans décaler tout le contenu */
        .block-container {
            max-width: 100%;
            padding-right: 320px;
        }

        /* 🎨 Style personnalisé pour la sidebar (expander) */
        div[data-testid="stExpander"] {
            position: fixed;
            top: 100px;
            right: 20px;
            width: 300px;
            z-index: 100;
            background-color: #111;
            border: 1px solid #444;
            border-radius: 8px;
            box-shadow: 2px 2px 12px rgba(0,0,0,0.3);
            color: #fff;
        }

        div[data-testid="stExpander"] summary {
            font-weight: 600;
            color: #fff;
        }

        div[data-testid="stExpander"] details[open] > summary {
            border-bottom: 1px solid #666;
            margin-bottom: 8px;
        }

        div[data-testid="stExpander"] p,
        div[data-testid="stExpander"] li,
        div[data-testid="stExpander"] label,
        div[data-testid="stExpander"] span {
            color: #eee !important;
        }

        /* 🔍 Scroll horizontal forcé sur les DataFrames si besoin */
        .stDataFrame > div {
            overflow-x: auto;
        }
    </style>
""", unsafe_allow_html=True)
