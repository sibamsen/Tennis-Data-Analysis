import streamlit as st
import pandas as pd
import plotly.express as px

# --- LOAD DATA ---
@st.cache_data
def load_data():
    competitors = pd.read_csv("data/processed_data/competitors.csv")
    rankings = pd.read_csv("data/processed_data/rankings.csv")
    return pd.merge(rankings, competitors, on="competitor_id")

def show():
    st.title("Global Analytics")

    df = load_data()

    # ---------------- SIDEBAR ----------------
    with st.sidebar:
        st.title("Filters")

        country_list = sorted(df['country'].dropna().unique())
        selected_country = st.selectbox("🌍 Country", ["Global"] + country_list)

        rank_limit = st.slider(
            "🏆 Rank Range",
            1,
            int(df['rank_position'].max()),
            (1, 100)
        )

        points_limit = st.slider(
            "🔥 Points Minimum",
            int(df['points'].min()),
            int(df['points'].max()),
            int(df['points'].min())
        )

    # ---------------- FILTER ----------------
    filtered_df = df.copy()

    if selected_country != "Global":
        filtered_df = filtered_df[filtered_df['country'] == selected_country]

    filtered_df = filtered_df[
        (filtered_df['rank_position'] >= rank_limit[0]) &
        (filtered_df['rank_position'] <= rank_limit[1]) &
        (filtered_df['points'] >= points_limit)
    ]

    # ---------------- METRICS ----------------
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Athletes", len(filtered_df))
    m2.metric("Avg Points", f"{filtered_df['points'].mean():.0f}")
    m3.metric("Countries", filtered_df['country'].nunique())
    m4.metric("Top Region", filtered_df['country'].value_counts().idxmax())

    # ---------------- CHARTS ----------------
    col1, col2 = st.columns([2,1])

    with col1:
        fig = px.scatter(
            filtered_df,
            x="rank_position",
            y="points",
            color="points",
            size="competitions_played",
            hover_name="name",
            template="plotly_dark"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        country_counts = filtered_df['country'].value_counts().head(10).reset_index()
        country_counts.columns = ['Country', 'Count']

        fig2 = px.pie(
            country_counts,
            values="Count",
            names="Country",
            hole=0.4,
            template="plotly_dark"
        )
        st.plotly_chart(fig2, use_container_width=True)

    fig3 = px.bar(
        filtered_df.groupby('country')['points'].sum().reset_index(),
        x='country',
        y='points',
        template="plotly_dark"
    )
    st.plotly_chart(fig3, use_container_width=True)