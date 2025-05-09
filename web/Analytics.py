import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta
import random
import numpy as np
import json
from collections import Counter

# ------------------ Page Config ------------------ #
st.set_page_config(
    page_title="CodeBrew Analytics",
    layout="wide"
)
st.sidebar.header("Analytics")
# Load external CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("static/style.css")

# Add custom header to the top bar
st.markdown(
    """
    <div class="custom-header">
        ☕ CodeBrew Dashboard
    </div>
    """,
    unsafe_allow_html=True
)

# Overlay steam effect and welcome message in a container
st.markdown("""
<div class="steam-overlay-container">
""", unsafe_allow_html=True)

steam_elements = []
for i in range(30):
    left = random.randint(0, 100)
    delay = random.uniform(0, 4)
    duration = random.uniform(4, 8)
    size = random.uniform(0.8, 1.2)
    steam_elements.append(
        f'<div class="steam" style="left:{left}%; animation-delay:{delay}s; animation-duration:{duration}s; transform: scale({size});"></div>'
    )

st.markdown(
    f"""
    <div class='steam-effect'>
        {''.join(steam_elements)}
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("### Welcome! Here's how your code has been brewing 🍵")
st.markdown("</div>", unsafe_allow_html=True)

# --- Read and aggregate data from data/data.json ---
with open('data/data.json', 'r') as f:
    entries = json.load(f)

if isinstance(entries, dict):
    entries = [entries]

# Parse dates and flatten summaries for charting
for e in entries:
    e['date'] = pd.to_datetime(e.get('date', ''))
    if not isinstance(e.get('optimization_summary', []), list):
        e['optimization_summary'] = [e['optimization_summary']]

df = pd.DataFrame(entries)
df = df.sort_values(by="date", ascending=False).head(4)

# Global stats
total_lines_optimized = df['no_of_lines_optmized'].sum() if 'no_of_lines_optmized' in df else 0
total_unused_lines_removed = df['no_of_unused_lines_removed'].sum() if 'no_of_unused_lines_removed' in df else 0
total_entries = len(df)
unique_repos = sorted(df['repo_name'].unique()) if 'repo_name' in df else []
unique_users = sorted(df['user'].unique()) if 'user' in df else []

# --- Display global stats below header ---
global_cols = st.columns(4)
global_cols[0].metric("Total Lines Optimized", total_lines_optimized)
global_cols[1].metric("Unused Lines Removed", total_unused_lines_removed)
global_cols[2].metric("Total Optimizations", total_entries)
global_cols[3].metric("Repositories Optimized", len(unique_repos))

# --- Optimization Over Time Chart (using all entries, not just top 4) ---
df_all = pd.DataFrame(entries)
df_all['date'] = pd.to_datetime(df_all['date'])
df_grouped = df_all.groupby('date', as_index=False)['no_of_lines_optmized'].sum()

st.subheader("📈 Optimization Over Time")
if not df_grouped.empty:
    chart = alt.Chart(df_grouped).mark_line(point=True).encode(
        x=alt.X('date:T', title='Date'),
        y=alt.Y('no_of_lines_optmized:Q', title='Lines Optimized'),
        tooltip=['date:T', 'no_of_lines_optmized']
    ).properties(height=300)
    chart = chart.configure_view(fill='#232323').configure(background='#232323')
    st.altair_chart(chart, use_container_width=True)
else:
    st.info("No data available for chart.")

# --- User leaderboard ---
user_counts = Counter(df['user']) if 'user' in df else {}
leaderboard = sorted(user_counts.items(), key=lambda x: x[1], reverse=True)
leaderboard_df = pd.DataFrame(leaderboard, columns=["User", "Entries Submitted"])
st.dataframe(leaderboard_df, use_container_width=True)

# --- Repo dropdown and repo stats ---
selected_repo = st.selectbox("Select Repository", unique_repos)
repo_df = df[df['repo_name'] == selected_repo]
repo_lines_optimized = repo_df['no_of_lines_optmized'].sum() if not repo_df.empty else 0
repo_unused_lines_removed = repo_df['no_of_unused_lines_removed'].sum() if not repo_df.empty else 0
repo_entries_count = len(repo_df)
repo_summaries = []
for summaries in repo_df['optimization_summary']:
    repo_summaries.extend(summaries)

repo_cols = st.columns(3)
repo_cols[0].metric("Repository Lines Optimized", repo_lines_optimized)
repo_cols[1].metric("Unused Lines Removed", repo_unused_lines_removed)
repo_cols[2].metric("Number of Optimizations for Repo", repo_entries_count)

# st.markdown('<span class="repo-summary-title">Optimization Summaries for this Repo:</span>', unsafe_allow_html=True)
st.markdown(
    "<div style='margin-bottom: -10px;'>Optimization Summaries for this Repo:</div>",
    unsafe_allow_html=True
)

if repo_summaries:
    st.markdown(
        "<ul style='margin-bottom:0.2rem'>"
        + "".join(f"<li>{summary}</li>" for summary in repo_summaries)
        + "</ul>",
        unsafe_allow_html=True
    )


# ------------------ Footer ------------------ #
st.markdown("<div class='footer'>Made with ❤️ by CodeBrew</div>", unsafe_allow_html=True)
