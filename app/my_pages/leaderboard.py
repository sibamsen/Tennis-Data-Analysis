import streamlit as st
import pandas as pd

@st.cache_data
def load_data():
    competitors = pd.read_csv("data/processed_data/competitors.csv")
    rankings = pd.read_csv("data/processed_data/rankings.csv")
    return pd.merge(rankings, competitors, on="competitor_id")

def show():
    st.title("🏆 Top Performers")

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

    # ---------------- FILTER ----------------
    filtered_df = df.copy()

    if selected_country != "Global":
        filtered_df = filtered_df[filtered_df['country'] == selected_country]

    filtered_df = filtered_df[
        (filtered_df['rank_position'] >= rank_limit[0]) &
        (filtered_df['rank_position'] <= rank_limit[1])
    ]

    # ---------------- TABLE ----------------
    display_df = filtered_df.sort_values("rank_position")[[
        'rank_position', 'name', 'country', 'points', 'movement', 'competitions_played'
    ]]

    display_df.columns = [
        "Rank", "Name", "Country", "Points", "Move", "Matches"
    ]

    def color_movement(val):
        if val > 0:
            return "color: green"
        elif val < 0:
            return "color: red"
        return "color: gray"

    st.dataframe(
        display_df.style.map(color_movement, subset=["Move"]),
        use_container_width=True,
        hide_index=True
    )