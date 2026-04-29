import streamlit as st
import pandas as pd
import plotly.express as px
from components.filters import render_filters


# -------------------------------
# UI STYLING
# -------------------------------
st.markdown("""
<style>
.main {
    background-color: #0e1117;
}

/* Title Gradient */
.title {
    font-size: 40px;
    font-weight: bold;
    background: -webkit-linear-gradient(#00d4ff, #7efff5);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* Cards */
.card {
    background: linear-gradient(135deg, #1e2130, #2e3341);
    padding: 20px;
    border-radius: 15px;
    border-left: 5px solid #00d4ff;
    box-shadow: 0 6px 20px rgba(0,0,0,0.5);
    text-align: center;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(#1e2130, #0e1117);
}
</style>
""", unsafe_allow_html=True)


# -------------------------------
# LOAD DATA
# -------------------------------
@st.cache_data
def load_data():
    competitions = pd.read_csv("data/processed_data/competitions.csv")
    categories = pd.read_csv("data/processed_data/categories.csv")

    competitions["parent_id"] = competitions["parent_id"].fillna("ROOT")
    competitions["type"] = competitions["type"].fillna("unknown")
    competitions["gender"] = competitions["gender"].fillna("unknown")

    competitions = competitions.merge(
        categories[["category_id", "category_name"]],
        on="category_id",
        how="left"
    )

    return categories, competitions


# -------------------------------
# MAIN PAGE
# -------------------------------
def show():

    st.markdown('<div class="title">Tournament Analytics Dashboard</div>', unsafe_allow_html=True)
    st.caption("Explore Tennis Event Hierarchies & Trends")

    categories, competitions = load_data()

    # -------------------------------
    # FILTERS
    # -------------------------------
    filters = render_filters(categories, competitions)

    st.success(
        f"📍 {filters['category_name']} → {filters['tournament_name']} → {filters['event_name']}"
    )

    # -------------------------------
    # DATA FILTERING
    # -------------------------------
    category_df = competitions[
        competitions["category_id"] == filters["category_id"]
    ]

    tournament_df = category_df[
        category_df["parent_id"] == "ROOT"
    ]

    event_df = category_df[
        category_df["parent_id"] == filters["tournament_id"]
    ]

    if event_df.empty:
        event_df = category_df[
            category_df["competition_id"] == filters["tournament_id"]
        ]

    # -------------------------------
    # KPIs (Styled Cards)
    # -------------------------------
    st.markdown("## Executive Overview")

    c1, c2, c3 = st.columns(3)

    c1.markdown(f"""
    <div class="card">
        <h3>Total Events</h3>
        <h1>{len(category_df)}</h1>
    </div>
    """, unsafe_allow_html=True)

    c2.markdown(f"""
    <div class="card">
        <h3>Tournaments</h3>
        <h1>{len(tournament_df)}</h1>
    </div>
    """, unsafe_allow_html=True)

    c3.markdown(f"""
    <div class="card">
        <h3>Matches</h3>
        <h1>{len(event_df)}</h1>
    </div>
    """, unsafe_allow_html=True)

    # -------------------------------
    # TREND ANALYSIS
    # -------------------------------
    st.markdown("## Trend Analysis")

    col1, col2 = st.columns(2)

    type_counts = category_df["type"].value_counts().reset_index()
    type_counts.columns = ["type", "count"]

    fig1 = px.bar(
        type_counts,
        x="type",
        y="count",
        color="count",
        color_continuous_scale="Blues",
        template="plotly_dark",
        title="Event Type Distribution"
    )

    col1.plotly_chart(fig1, use_container_width=True)

    gender_counts = category_df["gender"].value_counts().reset_index()
    gender_counts.columns = ["gender", "count"]

    fig2 = px.bar(
        gender_counts,
        x="gender",
        y="count",
        color="count",
        color_continuous_scale="Teal",
        template="plotly_dark",
        title="Gender Distribution"
    )

    col2.plotly_chart(fig2, use_container_width=True)

    # -------------------------------
    # EVENT STRUCTURE
    # -------------------------------
    st.markdown("## Event Structure")

    if not event_df.empty:
        sunburst_df = event_df.groupby(["gender", "type"]).size().reset_index(name="count")

        fig3 = px.sunburst(
            sunburst_df,
            path=["gender", "type"],
            values="count",
            template="plotly_dark"
        )

        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.warning("No event data available")

    # -------------------------------
    # COMPETITION LEVEL
    # -------------------------------
    st.markdown("## Competition Breakdown")

    comp_counts = category_df["category_name"].value_counts().reset_index()
    comp_counts.columns = ["category_name", "count"]

    fig4 = px.bar(
        comp_counts,
        x="category_name",
        y="count",
        color="count",
        color_continuous_scale="Viridis",
        template="plotly_dark",
        title="Competition Distribution"
    )

    st.plotly_chart(fig4, use_container_width=True)

    # -------------------------------
    # ADVANCED INSIGHTS
    # -------------------------------
    st.markdown("## Strategic Insights")

    if not category_df.empty:

        top_type = category_df["type"].mode()[0]
        top_gender = category_df["gender"].mode()[0]

        top_category = category_df["category_name"].value_counts().idxmax()

        st.markdown(f"""
<div style="
background: linear-gradient(135deg, #1e2130, #2e3341);
padding:20px;
border-radius:15px;
border-left:5px solid #00d4ff;
">

🔥 <b>Dominant Event Type:</b> {top_type} <br>

👥 <b>Primary Gender Category:</b> {top_gender} <br>

🏆 <b>Most Active Category:</b> {top_category} <br>

📊 <b>Total Records Processed:</b> {len(category_df)}

</div>
""", unsafe_allow_html=True)