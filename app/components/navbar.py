import streamlit as st

def render_navbar():
    pages = ["Home", "Players", "Country", "Leaderboard", "Simulation", "Predictor"]

    if "page" not in st.session_state:
        st.session_state.page = "Home"

    cols = st.columns(len(pages))

    for i, p in enumerate(pages):
        if cols[i].button(p, use_container_width=True):
            st.session_state.page = p

    return st.session_state.page

