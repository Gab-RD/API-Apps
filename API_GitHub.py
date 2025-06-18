import requests as rqst
import pandas as pd
import streamlit as st
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone

# 🔐 Chargement du token GitHub
load_dotenv()
token = os.getenv("GITHUB_TOKEN")
if not token:
    st.error("❗ Le token GITHUB_TOKEN est manquant.")
    st.stop()

headers = {
    "Authorization": f"token {token}",
    "Accept": "application/vnd.github+json"
}

# 🎯 Définir le dépôt cible
owner = "Shubhamsaboo"
repo = "awesome-llm-apps"
url = f"https://api.github.com/repos/{owner}/{repo}/pulls?state=closed&per_page=100"
limit_date = datetime.now(timezone.utc) - timedelta(days=365)

# 🔍 Requête API GitHub
response = rqst.get(url, headers=headers)
if response.status_code != 200:
    st.error(f"Erreur API GitHub ({response.status_code})")
    st.stop()

data = response.json()

# 🗃️ Extraction des PR
merged_prs = []
closed_prs = []

for pr in data:
    closed_at = pr.get("closed_at")
    merged_at = pr.get("merged_at")

    # PR fermées dans la période
    if closed_at:
        closed_date = datetime.strptime(closed_at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        if closed_date >= limit_date:
            closed_prs.append({
                "Numéro": pr["number"],
                "Titre": pr["title"],
                "Auteur": pr["user"]["login"],
                "Date de fermeture": closed_at[:10],
                "Lien": pr["html_url"]
            })

    # PR mergées dans la période
    if merged_at:
        merged_date = datetime.strptime(merged_at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        if merged_date >= limit_date:
            merged_prs.append({
                "Numéro": pr["number"],
                "Titre": pr["title"],
                "Auteur": pr["user"]["login"],
                "Date de merge": merged_at[:10],
                "Lien": pr["html_url"]
            })

# 📊 Affichage Streamlit
st.title("📦 Pull Requests GitHub – 12 Derniers mois")
st.caption(f"Dépôt inspecté : `{owner}/{repo}`")

if merged_prs:
    st.subheader("✅ PR mergées")
    st.dataframe(pd.DataFrame(merged_prs), use_container_width=True)
else:
    st.info("Aucune PR mergée sur les 12 derniers mois.")

if closed_prs:
    st.subheader("📁 PR fermées")
    st.dataframe(pd.DataFrame(closed_prs), use_container_width=True)
else:
    st.info("Aucune PR fermée sur les 12 derniers mois.")
