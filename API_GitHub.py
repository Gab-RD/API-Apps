import os
import pandas as pd
import requests as rqst
import streamlit as st
import matplotlib.pyplot as plt

from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

# --- UI Options ---
with st.expander("📁 Display Options", expanded=False):
    time_range = st.selectbox(
        "Time Range",
        ["Today", "This week", "This month", "This year", "5 years", "10 years"],
        index=3
    )
    show_table_merged = st.checkbox("Show merged PR table", True)
    show_table_closed = st.checkbox("Show closed PR table", True)
    show_graph_merged = st.checkbox("Show merged PR graph", True)
    show_graph_closed = st.checkbox("Show closed PR graph", True)
    show_evolution = st.checkbox("Show PR evolution over time", value=True)
    refresh_button = st.button("🔄 Refresh data")

# --- Date Range ---
days_ranges = {
    "Today": 1,
    "This week": 7,
    "This month": 30,
    "This year": 365,
    "5 years": 1825,
    "10 years": 3650
}
limit_date = datetime.now(timezone.utc) - timedelta(days=days_ranges[time_range])

# --- GitHub Authentication ---
load_dotenv()
token = os.getenv("GITHUB_TOKEN")
if not token:
    st.error("Missing GITHUB_TOKEN.")
    st.stop()

headers = {
    "Authorization": f"token {token}",
    "Accept": "application/vnd.github+json"
}

# --- Fetch PRs ---
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

# --- Start UI ---
st.title("📊 GitHub Pull Requests")
input_url = st.text_input(
    "🔗 GitHub URL",
    value="",
    placeholder="Enter a repository or account URL (https://github.com/owner/repo | https://github.com/username)"
)

if not input_url.strip():
    st.info("🕵️ Please enter a GitHub URL to begin analysis.")
    st.stop()

path_parts = urlparse(input_url).path.strip("/").split("/")
data = []

if len(path_parts) == 2:
    owner, repo = path_parts
    st.caption("Detected mode: single repository")
    data = get_all_prs(owner, repo)

elif len(path_parts) == 1 and path_parts[0]:
    username = path_parts[0]
    st.caption("Detected mode: full GitHub account")
    r = rqst.get(f"https://api.github.com/users/{username}/repos?per_page=100", headers=headers)
    if r.status_code != 200:
        st.error("Failed to fetch repositories.")
        st.stop()
    for repo_obj in r.json():
        repo_name = repo_obj["name"]
        prs = get_all_prs(username, repo_name)
        for pr in prs:
            pr["repo"] = repo_name
        data.extend(prs)

# --- Author Filtering ---
authors = sorted({pr["user"]["login"] for pr in data if pr.get("user")})
selected_authors = st.multiselect(
    "Filter by one or more authors",
    options=authors,
    default=[],
    help="Start typing to filter (autocomplete)"
)

# --- Prepare PRs ---
merged_rows, closed_rows = [], []

for pr in data:
    login = pr.get("user", {}).get("login", "")
    avatar_url = pr.get("user", {}).get("avatar_url", "")
    repo_name = pr.get("repo", repo if len(path_parts) == 2 else "")

    if selected_authors and login not in selected_authors:
        continue

    if pr.get("merged_at"):
        d = datetime.strptime(pr["merged_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        if d >= limit_date:
            merged_rows.append([repo_name, pr["number"], pr["title"], login, d.strftime("%Y-%m-%d"), pr["html_url"], avatar_url])

    if pr.get("closed_at"):
        d = datetime.strptime(pr["closed_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        if d >= limit_date:
            closed_rows.append([repo_name, pr["number"], pr["title"], login, d.strftime("%Y-%m-%d"), pr["html_url"], avatar_url])

# --- Render Tables ---
columns = ["Repository", "Number", "Title", "Author", "Date", "Link", "Avatar"]
merged_df = pd.DataFrame(merged_rows, columns=columns)
closed_df = pd.DataFrame(closed_rows, columns=columns)

if merged_df.empty and closed_df.empty:
    st.info("No data to display.")
    st.stop()

st.markdown("""
<style>
table {
    width: 100%;
    border-collapse: collapse;
    background-color: #111;
    border: none !important;
    box-shadow: none !important;
}
th, td {
    padding: 6px 10px;
    text-align: left;
    border-bottom: 1px solid #444;
    font-size: 14px;
    color: #eee;
}
th {
    background-color: #222;
    color: #fff;
    position: sticky;
    top: 0;
    z-index: 1;
}
.stDataFrame > div {
    overflow-x: auto;
}
</style>
""", unsafe_allow_html=True)

def format_avatar(url):
    return f'<img src="{url}" width="30" style="border-radius:50%;margin:2px"/>'

def render_table_with_scroll(df_html):
    return f'''
    <div style="overflow: auto; max-height: 500px; padding: 10px; background-color: #111;">
        {df_html}
    </div>
    '''

merged_df["Avatar"] = merged_df["Avatar"].apply(format_avatar)
closed_df["Avatar"] = closed_df["Avatar"].apply(format_avatar)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Merged PRs")
    if show_table_merged:
        if not merged_df.empty:
            st.markdown(render_table_with_scroll(merged_df.to_html(escape=False, index=False)), unsafe_allow_html=True)
        else:
            st.info("No merged PRs found.")

with col2:
    st.subheader("Closed PRs")
    if show_table_closed:
        if not closed_df.empty:
            st.markdown(render_table_with_scroll(closed_df.to_html(escape=False, index=False)), unsafe_allow_html=True)
        else:
            st.info("No closed PRs found.")

# --- Graphs ---
if show_graph_merged or show_graph_closed:
    st.subheader("📈 PRs by Author")
    gcol1, gcol2 = st.columns(2)

    if show_graph_merged:
        with gcol1:
            st.markdown("#### Merged PRs")
            if not merged_df.empty:
                fig, ax = plt.subplots(figsize=(5, 5))
                merged_df["Author"].value_counts().head(10).plot(kind="barh", ax=ax, color="#0083B8")
                ax.invert_yaxis()
                st.pyplot(fig)
            else:
                st.info("No merged PRs found.")

    if show_graph_closed:
        with gcol2:
            st.markdown("#### Closed PRs")
            if not closed_df.empty:
                fig, ax = plt.subplots(figsize=(5, 5))
                closed_df["Author"].value_counts().head(10).plot(kind="barh", ax=ax, color="#0083B8")
                ax.invert_yaxis()
                st.pyplot(fig)
            else:
                st.info("No closed PRs found.")

# --- Evolution Graph ---
if show_evolution:
    if not (merged_df.empty and closed_df.empty):
        df_merged = merged_df.copy()
        df_closed = closed_df.copy()

        df_merged["Date"] = pd.to_datetime(df_merged["Date"])
        df_closed["Date"] = pd.to_datetime(df_closed["Date"])

        evo_merged = df_merged.set_index("Date").resample("W").size()
        evo_closed = df_closed.set_index("Date").resample("W").size()

        fig, ax = plt.subplots(figsize=(6, 2.5))
        evo_merged.plot(ax=ax, label="Merged PRs", color="#2ECC71")
        evo_closed.plot(ax=ax, label="Closed PRs", color="#E67E22")
        ax.set_facecolor("#111")
        fig.patch.set_facecolor("#111")
        ax.set_title("PR Trends Over Time", fontsize=7, color="#eee")
        ax.set_ylabel("Number of PRs", fontsize=5, color="#eee")
        ax.set_xlabel("Week", fontsize=5, color="#eee")
        ax.tick_params(axis='both', colors='white', labelcolor='white')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.legend(fontsize=10)
        st.pyplot(fig)
    else:
        st.info("No PRs to display in trend chart.")

st.markdown("""
<style>
table {
    width: 100%;
    border-collapse: collapse;
    background-color: #111;
    border: none !important;
    box-shadow: none !important;
}
th, td {
    padding: 6px 10px;
    text-align: left;
    border-bottom: 1px solid #444;
    font-size: 14px;
    color: #eee;
}
th {
    background-color: #222;
    color: #fff;
    position: sticky;
    top: 0;
    z-index: 1;
}
.element-container, .stDataFrame, .block-container {
    border: none !important;
    box-shadow: none !important;
}
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
.element-container:has(.stPlotlyChart), 
.element-container:has(.stPyplot) {
    margin-top: -10px;
    margin-bottom: -10px;
    padding: 0px;
}
</style>
""", unsafe_allow_html=True)
