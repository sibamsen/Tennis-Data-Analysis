import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

@st.cache_data
def load_data():
    competitors = pd.read_csv("data/processed_data/competitors.csv")
    rankings = pd.read_csv("data/processed_data/rankings.csv")

    # ✅ Merge data
    df = pd.merge(rankings, competitors, on="competitor_id")

    # ✅ Fix column types
    df["rank_position"] = pd.to_numeric(df["rank_position"], errors="coerce")
    df["points"] = pd.to_numeric(df["points"], errors="coerce")

    # ✅ Remove nulls
    df = df.dropna(subset=["rank_position", "points"])

    # ✅ Remove duplicates (CRITICAL)
    df = df.sort_values("rank_position").drop_duplicates(
        subset=["competitor_id"], keep="first"
    )

    return df


def show():

    st.title("🔍 Player Deep Dive")

    df = load_data()

    if df.empty:
        st.warning("No data available")
        return

    # ---------------- FILTERS ---------------- #
    st.sidebar.header("Filters")

    country = st.sidebar.selectbox(
        "Select Country",
        ["All"] + sorted(df["country"].dropna().unique())
    )

    min_rank = int(df["rank_position"].min())
    max_rank = int(df["rank_position"].max())

    rank_range = st.sidebar.slider(
        "Rank Range",
        min_rank,
        max_rank,
        (min_rank, max_rank)
    )

    min_points = int(df["points"].min())

    points_filter = st.sidebar.slider(
        "Points Minimum",
        min_points,
        int(df["points"].max()),
        min_points
    )

    # ---------------- APPLY FILTER ---------------- #
    filtered_df = df[
        (df["rank_position"] >= rank_range[0]) &
        (df["rank_position"] <= rank_range[1]) &
        (df["points"] >= points_filter)
    ]

    if country != "All":
        filtered_df = filtered_df[filtered_df["country"] == country]

    # ---------------- PLAYER SELECT ---------------- #
    player_list = sorted(filtered_df["name"].dropna().unique())

    selected_player = st.selectbox("Select Player", player_list)

    player = filtered_df[filtered_df["name"] == selected_player].iloc[0]

    # ---------------- LAYOUT ---------------- #
    col1, col2 = st.columns([1, 2])

    # ---------------- PLAYER CARD ---------------- #
    with col1:
        movement = int(player["movement"])

        if movement > 0:
            move_icon = "🔼"
            move_color = "#00ff00"
        elif movement < 0:
            move_icon = "🔽"
            move_color = "#ff4b4b"
        else:
            move_icon = "⏺"
            move_color = "#aaa"

        st.markdown(f"""
        <div style="
        background: linear-gradient(135deg,#1e2130,#2e3341);
        padding:20px;
        border-radius:15px;
        border-left:5px solid #00d4ff;
        ">

        <h3>{player['name']}</h3>
        <p style="color:#00d4ff">{player['country']}</p>

        <hr>

        <p><b>Rank:</b> #{int(player['rank_position'])}</p>
        <p><b>Points:</b> {int(player['points'])}</p>

        <p><b>Movement:</b>
        <span style="color:{move_color}">
        {move_icon} {movement}
        </span></p>

        </div>
        """, unsafe_allow_html=True)

    # ---------------- GAUGE ---------------- #
    with col2:
        import plotly.graph_objects as go

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=int(player["points"]),
            title={'text': "Points Capacity"},
            gauge={
                'axis': {'range': [0, 9000]},
                'bar': {'color': "#00d4ff"},
            }
        ))

        st.plotly_chart(fig, width="stretch")