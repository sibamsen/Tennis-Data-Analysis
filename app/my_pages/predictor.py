import streamlit as st
import pandas as pd
import numpy as np
from utils.prediction import predict, train_model

st.set_page_config(layout="wide")

# -------------------------------
# LOAD DATA
# -------------------------------
@st.cache_data
def load_data():
    competitors = pd.read_csv("data/processed_data/competitors.csv")
    rankings = pd.read_csv("data/processed_data/rankings.csv")

    df = pd.merge(rankings, competitors, on="competitor_id")

    # FIX TYPES
    df["rank_position"] = pd.to_numeric(df["rank_position"], errors="coerce")
    df["points"] = pd.to_numeric(df["points"], errors="coerce")

    # REMOVE NULLS
    df = df.dropna(subset=["rank_position", "points"])

    # REMOVE DUPLICATES 
    df = df.sort_values("rank_position").drop_duplicates(
        subset=["competitor_id"], keep="first"
    )

    return df


# -------------------------------
# MONTE CARLO SIMULATION
# -------------------------------
def simulate_match(p1_prob: float, simulations: int = 500):
    p1_wins = np.random.binomial(simulations, p1_prob)
    p2_wins = simulations - p1_wins

    return p1_wins / simulations, p2_wins / simulations


# -------------------------------
# MAIN UI
# -------------------------------
def show():
    st.title("🤖 Match Predictor (ML Simulation)")

    df = load_data()

    if df.empty:
        st.error("No data available")
        return

    # -------------------------------
    # FILTER (OPTIONAL CATEGORY)
    # -------------------------------
    category = st.selectbox("Select Category", ["All", "Top Players", "Lower Ranked"])

    if category == "Top Players":
        df = df[df["points"] > df["points"].median()]
    elif category == "Lower Ranked":
        df = df[df["points"] <= df["points"].median()]

    # -------------------------------
    # PLAYER SELECTION
    # -------------------------------
    names = sorted(df["name"].unique())

    col1, col2 = st.columns(2)

    with col1:
        team1 = st.selectbox("Select Player 1", names)

    with col2:
        team2 = st.selectbox("Select Player 2", [n for n in names if n != team1])

    simulations = st.slider("Number of Simulations", 100, 2000, 500)

    # -------------------------------
    # RUN BUTTON
    # -------------------------------
    if st.button("Run ML Simulation"):

        if team1 == team2:
            st.error("Select different players")
            return

        # FETCH PLAYERS
        p1 = df[df["name"] == team1].iloc[0]
        p2 = df[df["name"] == team2].iloc[0]

        # TRAIN MODEL
        model = train_model(df)

        # ML PREDICTION
        base_prob, _ = predict(model, p1, p2)

        # SIMULATION
        sim_p1, sim_p2 = simulate_match(base_prob, simulations)

        # -------------------------------
        # RESULTS
        # -------------------------------
        st.markdown("## Prediction Result")

        if sim_p1 > sim_p2:
            winner = team1
            winner_prob = sim_p1
        else:
            winner = team2
            winner_prob = sim_p2

        # -------------------------------
        # PLAYER CARDS
        # -------------------------------
        c1, c2 = st.columns(2)

        with c1:
            st.markdown(f"""
            <div style="padding:20px;border-radius:15px;background:#1e2130">
                <h3>{team1}</h3>
                <p>Points: {int(p1['points'])}</p>
                <p>Rank: {int(p1['rank_position'])}</p>
                <p style="color:#00ffcc">Win %: {round(sim_p1*100,2)}%</p>
            </div>
            """, unsafe_allow_html=True)

        with c2:
            st.markdown(f"""
            <div style="padding:20px;border-radius:15px;background:#1e2130">
                <h3>{team2}</h3>
                <p>Points: {int(p2['points'])}</p>
                <p>Rank: {int(p2['rank_position'])}</p>
                <p style="color:#ff4b4b">Win %: {round(sim_p2*100,2)}%</p>
            </div>
            """, unsafe_allow_html=True)

        # -------------------------------
        # WINNER LOGIC
        # -------------------------------
        st.markdown("### Winner Analysis")

        if abs(sim_p1 - sim_p2) < 0.05:
            st.warning("⚖️ Very Close Match")
        elif winner_prob > 0.7:
            st.success(f"🏆 Strong Favorite: {winner}")
        else:
            st.info(f"🏆 Likely Winner: {winner}")

        # -------------------------------
        # CONFIDENCE
        # -------------------------------
        st.markdown("### Confidence Level")

        confidence = round(winner_prob * 100, 2)

        if confidence > 80:
            st.success(f"High Confidence ({confidence}%)")
        elif confidence > 65:
            st.info(f"Medium Confidence ({confidence}%)")
        else:
            st.warning(f"Low Confidence ({confidence}%)")

        # -------------------------------
        # METRICS
        # -------------------------------
        st.markdown("### Win Probability")

        col1, col2 = st.columns(2)

        col1.metric(team1, f"{round(sim_p1*100,2)}%")
        col2.metric(team2, f"{round(sim_p2*100,2)}%")

        # -------------------------------
        # PROGRESS BAR
        # -------------------------------
        st.progress(int(max(sim_p1, sim_p2) * 100))

        # -------------------------------
        # VISUAL BAR
        # -------------------------------
        st.markdown(f"""
        <div style="display:flex;height:25px;border-radius:10px;overflow:hidden;">
            <div style="width:{sim_p1*100}%;background:#00c853;"></div>
            <div style="width:{sim_p2*100}%;background:#d50000;"></div>
        </div>
        """, unsafe_allow_html=True)