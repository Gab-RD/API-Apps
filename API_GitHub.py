import os
import requests as rqst
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

# --- Interface utilisateur ---
with st.expander("📁 Options (affichage)", expanded=False):
    plage = st.selectbox("Plage de temps", ["Aujourd'hui", "Cette semaine", "Ce mois", "Cette année", "5 ans", "10 ans"], index=3)
    afficher_tableau_merged = st.checkbox("Afficher tableau PR mergées", True)
    afficher_tableau_closed = st.checkbox("Afficher tableau PR fermées", True)
    afficher_graph_merged = st.checkbox("Afficher Graphique PR mergées", True)
    afficher_graph_closed = st.checkbox("Afficher Graphique PR fermées", True)
    afficher_evolution_pr = st.checkbox("Afficher évolution des PRs dans le temps", value=True)
    bouton_reload = st.button("🔄 Rafraîchir les données")

# --- Paramètres ---
plages_jours = {"Aujourd'hui": 1, "Cette semaine": 7, "Ce mois": 30, "Cette année": 365, "5 ans": 1825, "10 ans": 3650}
limit_date = datetime.now(timezone.utc) - timedelta(days=plages_jours[plage])

# --- Authentification GitHub ---
load_dotenv()
token = os.getenv("GITHUB_TOKEN")
if not token:
    st.error("Le token GITHUB_TOKEN est manquant.")
    st.stop()

headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github+json"}

# --- Récupération des PRs GitHub ---
def get_all_prs(owner, repo, pages=5):
    all_data = []
    for page in range(1, pages + 1):
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
        params = {"state": "closed", "per_page": 100, "page": page}
        r = rqst.get(url, headers=headers, params=params)
        if r.status_code != 200 or not r.json():
            break
        all_data.extend(r.json())
    return all_data

# --- Récupération des données ---
st.title("📊 Pull Requests GitHub")
url_saisie = st.text_input(
    "🔗 GitHub URL",
    value="",
    placeholder="Enter your repository or account  URL (https://github.com/owner/repo | https://github.com/username)"
)

if not url_saisie.strip():
    st.info("🕵️‍♂️ Veuillez saisir une URL GitHub pour commencer l’analyse.")
    st.stop()

# Détection automatique du mode selon l'URL
path_parts = urlparse(url_saisie).path.strip("/").split("/")

data = []

if len(path_parts) == 2:
    # Mode Dépôt unique détecté automatiquement
    owner, repo = path_parts
    st.caption("Mode détecté : dépôt unique")
    data = get_all_prs(owner, repo)

elif len(path_parts) == 1 and path_parts[0]:
    # Mode Compte GitHub détecté automatiquement
    username = path_parts[0]
    st.caption("Mode détecté : compte complet")
    r = rqst.get(f"https://api.github.com/users/{username}/repos?per_page=100", headers=headers)
    if r.status_code != 200:
        st.error("Erreur lors de la récupération des dépôts.")
        st.stop()
    for repo_obj in r.json():
        repo_name = repo_obj["name"]
        prs = get_all_prs(username, repo_name)
        for pr in prs:
            pr["repo"] = repo_name
        data.extend(prs)

else:
    st.error("URL invalide. Format attendu : https://github.com/owner/repo ou https://github.com/username")

# --- Sélection d’auteur ---
auteurs_possibles = sorted({pr["user"]["login"] for pr in data if pr.get("user")})
auteurs_selectionnes = st.multiselect(
    "Filtrer par un ou plusieurs auteurs",
    options=auteurs_possibles,
    default=[],
    help= "Commence à taper un nom pour filtrer (autocomplete)")

# --- Traitement des PRs ---
merged_rows, closed_rows = [], []

for pr in data:
    # récupération du login et avatar
    login = pr.get("user", {}).get("login", "")
    avatar_url = pr.get("user", {}).get("avatar_url", "")

    # (filtrage d’auteur en multi-select)
    if auteurs_selectionnes and login not in auteurs_selectionnes:
        continue

    repo_name = pr.get("repo", repo if len(path_parts) == 2 else "")

    if auteurs_selectionnes and login not in auteurs_selectionnes:
        continue
    repo_name = pr.get("repo", repo if len(path_parts) == 2 else "")
    if pr.get("merged_at"):
        d = datetime.strptime(pr["merged_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        if d >= limit_date:
            merged_rows.append([repo_name, pr["number"], pr["title"], login, d.strftime("%Y-%m-%d"), pr["html_url"], avatar_url])

    if pr.get("closed_at"):
        d = datetime.strptime(pr["closed_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        if d >= limit_date:
            closed_rows.append([repo_name, pr["number"], pr["title"], login, d.strftime("%Y-%m-%d"), pr["html_url"], avatar_url])

# --- Affichage des tableaux ---
columns = ["Dépôt", "Numéro", "Titre", "Auteur", "Date", "Lien", "Avatar"]
merged_df = pd.DataFrame(merged_rows, columns=columns)
closed_df = pd.DataFrame(closed_rows, columns=columns)

if (merged_df.empty and closed_df.empty):
    st.info("Aucune donnée à afficher.")
    st.stop()

st.markdown("""
<style>
    table {
        width: 100%;
        border-collapse: collapse;
        background-color: #fff;
    }
    th, td {
        padding: 6px 10px;
        text-align: left;
        border-bottom: 1px solid #ddd;
        font-size: 14px;
        color: #111;
    }
    th {
        background-color: #f0f0f0;
        color: #111;
        position: sticky;
        top: 0;
        z-index: 1;
    }
</style>
""", unsafe_allow_html=True)

def render_table_with_scroll(df_html):
    return f'''
    <div style="overflow: auto; max-height: 500px; border: 1px solid #ddd; border-radius: 6px; padding: 10px;">
        {df_html}
    </div>
    '''

def format_avatar(url):
    return f'<img src="{url}" width="30" style="border-radius:50%;margin:2px"/>'

merged_df_affichable = merged_df.copy()
closed_df_affichable = closed_df.copy()

ordre_colonnes = ["Numéro", "Avatar", "Auteur", "Titre", "Numéro", "Dépôt", "Date", "Lien"]

merged_df_affichable = merged_df_affichable[ordre_colonnes]
closed_df_affichable = closed_df_affichable[ordre_colonnes]


# Ajout des avatars stylés
merged_df_affichable["Avatar"] = merged_df_affichable["Avatar"].apply(format_avatar)
closed_df_affichable["Avatar"] = closed_df_affichable["Avatar"].apply(format_avatar)

col1, col2 = st.columns(2)

with col1:
    st.subheader("PR mergées")
    if afficher_tableau_merged:
        if not merged_df.empty:
            df = merged_df.copy()
            df["Avatar"] = df["Avatar"].apply(lambda url: f'<img src="{url}" width="30" style="border-radius:50%"/>')
            st.markdown(render_table_with_scroll(df.to_html(escape=False, index=False)), unsafe_allow_html=True)
        else:
            st.info("Aucune PR mergée trouvée.")

with col2:
    st.subheader("PR fermées")
    if afficher_tableau_closed:
        if not closed_df.empty:
            df = closed_df.copy()
            df["Avatar"] = df["Avatar"].apply(lambda url: f'<img src="{url}" width="30" style="border-radius:50%"/>')
            st.markdown(render_table_with_scroll(df.to_html(escape=False, index=False)), unsafe_allow_html=True)
        else:
            st.info("Aucune PR fermée trouvée.")

# --- Graphiques ---
if afficher_graph_merged or afficher_graph_closed:
    st.subheader("📈 Répartition des PR par auteur")
    colg1, colg2 = st.columns(2)

    if afficher_graph_merged:
        with colg1:
            st.markdown("#### PR mergées")
            if not merged_df.empty:
                fig, ax = plt.subplots(figsize=(5, 5))
                merged_df["Auteur"].value_counts().head(10).plot(kind="barh", ax=ax, color="#0083B8")
                ax.invert_yaxis()
                st.pyplot(fig)
            else:
                st.info("Aucune PR mergée trouvée.")
    else:
        st.warning("Affichage du tableau PR mergées désactivé.")

    if afficher_graph_closed:
        with colg2:
            st.markdown("#### PR fermées")
            if not closed_df.empty:
                fig, ax = plt.subplots(figsize=(5, 5))
                closed_df["Auteur"].value_counts().head(10).plot(kind="barh", ax=ax, color="#0083B8")
                ax.invert_yaxis()
                st.pyplot(fig)
            else:
                st.info("Aucune PR fermée trouvée.")
    else:
        st.warning("Affichage du tableau PR mergées désactivé.")

if afficher_evolution_pr:
    if not (merged_df.empty and closed_df.empty):

        st.subheader("📈 Évolution temporelle des contributions")

        # Préparation des données temporelles
        df_merged = merged_df.copy()
        df_closed = closed_df.copy()

        df_merged["Date"] = pd.to_datetime(df_merged["Date"])
        df_closed["Date"] = pd.to_datetime(df_closed["Date"])

        evolution_merged = df_merged.set_index("Date").resample("W").size()
        evolution_closed = df_closed.set_index("Date").resample("W").size()

        fig, ax = plt.subplots(figsize=(8, 4))
        evolution_merged.plot(ax=ax, label="PR mergées", color="#2ECC71")
        evolution_closed.plot(ax=ax, label="PR fermées", color="#E67E22")
        ax.set_title("Évolution des PRs mergées & fermées")
        ax.set_ylabel("Nombre de PRs")
        ax.set_xlabel("Semaine")
        ax.legend()
        st.pyplot(fig)
    else :
        st.info("Aucune PR mergée ou fermée à afficher dans ce graphique")

# Custom CSS
st.markdown("""
<style>
.block-container {
    max-width: 100%;
    padding-right: 320px;
}
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
.stDataFrame > div {
    overflow-x: auto;
}
</style>
""", unsafe_allow_html=True)
