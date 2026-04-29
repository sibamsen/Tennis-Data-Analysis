import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------- PAGE CONFIG ---------------- #
st.set_page_config(
    page_title="ProTennis Dashboard",
    layout="wide"
)

# ---------------- UI STYLE ---------------- #
st.markdown("""
<style>
.main {
    background-color: #0e1117;
}

/* Gradient Title */
.title {
    font-size: 40px;
    font-weight: bold;
    background: -webkit-linear-gradient(#00d4ff, #7efff5);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* Metric Cards */
.card {
    background: linear-gradient(135deg, #1e2130, #2e3341);
    padding: 20px;
    border-radius: 15px;
    border-left: 5px solid #00d4ff;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ---------------- DATA LOADER ---------------- #
@st.cache_data
def load_data():
    competitors = pd.read_csv("data/processed_data/competitors.csv")
    rankings = pd.read_csv("data/processed_data/rankings.csv")

    df = pd.merge(rankings, competitors, on="competitor_id")

    df["rank_position"] = pd.to_numeric(df["rank_position"], errors="coerce")
    df["points"] = pd.to_numeric(df["points"], errors="coerce")

    df = df.dropna(subset=["rank_position", "points"])

    df = df.sort_values("rank_position").drop_duplicates(
        subset=["competitor_id"], keep="first"
    )

    return df


# ---------------- MAIN ---------------- #
def show():

    st.markdown('<div class="title"> Game Analytics: Tennis Data with SportRadar API </div>', unsafe_allow_html=True)

    df = load_data()

    if df.empty:
        st.warning("No data available")
        return

    # ---------------- KPI ---------------- #
    total_players = len(df)
    total_countries = df["country"].nunique()
    avg_points = int(df["points"].mean())
    max_points = int(df["points"].max())

    def metric_card(title, value, color):
        return f"""
        <div class="card" style="border-left:5px solid {color}">
            <h4>{title}</h4>
            <h2 style="color:{color}">{value}</h2>
        </div>
        """

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(metric_card("👥 Players", total_players, "#00d4ff"), unsafe_allow_html=True)
    c2.markdown(metric_card("🌍 Countries", total_countries, "#00ffcc"), unsafe_allow_html=True)
    c3.markdown(metric_card("📊 Avg Points", avg_points, "#ffcc00"), unsafe_allow_html=True)
    c4.markdown(metric_card("🏆 Max Points", max_points, "#ff4b4b"), unsafe_allow_html=True)

    st.markdown("---")

    # ---------------- TOP PLAYERS ---------------- #
    st.subheader("Top 10 Players by Points")

    top_players = df.sort_values("points", ascending=False).head(10)

    fig1 = px.bar(
        top_players,
        x="name",
        y="points",
        color="points",
        color_continuous_scale="Plasma",
        template="plotly_dark"
    )
    fig1.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig1, use_container_width=True)

    # ---------------- COUNTRY POINTS ---------------- #
    st.subheader("Top 10 Countries by Total Points")

    country_points = (
        df.groupby("country", as_index=False)["points"]
        .sum()
        .sort_values("points", ascending=False)
        .head(10)
    )

    fig2 = px.bar(
        country_points,
        x="country",
        y="points",
        color="points",
        color_continuous_scale="Plasma",
        template="plotly_dark"
    )
    fig2.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig2, use_container_width=True)

    # ---------------- PLAYER DISTRIBUTION ---------------- #
    st.subheader("Player Distribution by Country")

    player_dist = (
        df["country"]
        .value_counts()
        .head(10)
        .reset_index()
    )
    player_dist.columns = ["country", "players"]

    fig3 = px.pie(
        player_dist,
        values="players",
        names="country",
        hole=0.4,
        template="plotly_dark"
    )
    st.plotly_chart(fig3, use_container_width=True)

    # ---------------- SCATTER ---------------- #
    st.subheader("Ranking vs Points")

    fig4 = px.scatter(
        df,
        x="rank_position",
        y="points",
        color="points",
        size="competitions_played",
        hover_name="name",
        template="plotly_dark"
    )
    st.plotly_chart(fig4, use_container_width=True)

    # ---------------- INSIGHTS ---------------- #
    st.markdown("## Strategic Insights")

    top_countries = (
        df.groupby("country")["points"]
        .sum()
        .sort_values(ascending=False)
        .head(3)
    )

    top_players3 = df.sort_values("points", ascending=False).head(3)

    top_player_base = df["country"].value_counts().head(3)

    st.markdown(f"""
    <div style="
    background: linear-gradient(135deg,#1e2130,#2e3341);
    padding:25px;
    border-radius:15px;
    border-left:5px solid #00d4ff;
    font-size:16px;
    line-height:1.7;
    ">

    🔥 <b>Top 3 Countries by Total Points</b><br>
    🥇 {top_countries.index[0]} → <span style="color:#00ffcc">{top_countries.iloc[0]:,}</span><br>
    🥈 {top_countries.index[1]} → {top_countries.iloc[1]:,}<br>
    🥉 {top_countries.index[2]} → {top_countries.iloc[2]:,}

    <br>

    🏆 <b>Top 3 Players</b><br>
    🥇 {top_players3.iloc[0]['name']} ({top_players3.iloc[0]['country']}) → {top_players3.iloc[0]['points']:,}<br>
    🥈 {top_players3.iloc[1]['name']} ({top_players3.iloc[1]['country']}) → {top_players3.iloc[1]['points']:,}<br>
    🥉 {top_players3.iloc[2]['name']} ({top_players3.iloc[2]['country']}) → {top_players3.iloc[2]['points']:,}

    <br>

    🌍 <b>Top Player Base Countries</b><br>
    🥇 {top_player_base.index[0]} → {top_player_base.iloc[0]} players<br>
    🥈 {top_player_base.index[1]} → {top_player_base.iloc[1]} players<br>
    🥉 {top_player_base.index[2]} → {top_player_base.iloc[2]} players

    </div>
    """, unsafe_allow_html=True)


# ---------------- RUN ---------------- #
if __name__ == "__main__":
    show()