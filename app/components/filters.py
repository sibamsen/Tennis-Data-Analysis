import streamlit as st

def render_filters(categories, competitions):

    st.sidebar.markdown("## 🎯 Event Explorer")

    category_name = st.sidebar.selectbox(
        "Category",
        sorted(categories["category_name"].unique())
    )

    category_id = categories[
        categories["category_name"] == category_name
    ]["category_id"].values[0]

    category_df = competitions[
        competitions["category_id"] == category_id
    ]

    # FIX ROOT
    tournaments = category_df[
        category_df["parent_id"].isna() | (category_df["parent_id"] == "")
    ]

    if tournaments.empty:
        tournaments = category_df

    tournament_name = st.sidebar.selectbox(
        "Tournament",
        sorted(tournaments["competition_name"].unique())
    )

    tournament_id = tournaments[
        tournaments["competition_name"] == tournament_name
    ]["competition_id"].values[0]

    # EVENTS
    events = category_df[
        category_df["parent_id"] == tournament_id
    ]

    if events.empty:
        event_name = "All Matches"
        event_id = tournament_id
    else:
        event_name = st.sidebar.selectbox(
            "Event (Singles / Doubles)",
            sorted(events["competition_name"].unique())
        )

        event_id = events[
            events["competition_name"] == event_name
        ]["competition_id"].values[0]

    return {
        "category_id": category_id,
        "tournament_id": tournament_id,
        "event_id": event_id,
        "category_name": category_name,
        "tournament_name": tournament_name,
        "event_name": event_name
    }