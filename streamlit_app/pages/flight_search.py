import streamlit as st
import pandas as pd
import requests
from datetime import datetime


# INDIA BOUNDING BOX

INDIA_BOUNDS = {
    "lamin": 6.0,
    "lamax": 35.0,
    "lomin": 68.0,
    "lomax": 97.0
}

OPEN_SKY_URL = "https://opensky-network.org/api/states/all"


def fetch_live_flights():
    """Fetch live flights over India from OpenSky"""
    response = requests.get(
        OPEN_SKY_URL,
        params=INDIA_BOUNDS,
        timeout=10
    )

    if response.status_code != 200:
        return pd.DataFrame()

    data = response.json()

    if not data.get("states"):
        return pd.DataFrame()

    flights = []
    for s in data["states"]:
        flights.append({
            "icao24": s[0],
            "callsign": (s[1] or "").strip(),
            "country": s[2],
            "longitude": s[5],
            "latitude": s[6],
            "altitude_m": s[13],
            "speed_mps": s[9],
            "heading": s[10],
            "on_ground": s[8],
            "last_update": datetime.utcfromtimestamp(data["time"])
        })

    df = pd.DataFrame(flights)
    return df.dropna(subset=["latitude", "longitude"])


def show():
    st.title("🟢 Live Flight Search (India)")

    st.info(
        "This page shows **REAL-TIME live aircraft over India** using OpenSky free API.\n\n"
        "**No database required.**"
    )

    
    # SEARCH FILTERS

    col1, col2, col3 = st.columns(3)

    with col1:
        callsign = st.text_input(
            "Flight / Callsign (e.g. 6E, AI, SG)",
            placeholder="Example: 6E"
        )

    with col2:
        airline_country = st.selectbox(
            "Country",
            ["", "India", "United States", "United Kingdom", "Germany"]
        )

    with col3:
        on_ground = st.selectbox(
            "Aircraft Status",
            ["", "Airborne", "On Ground"]
        )

    if st.button("🔍 Search Live Flights"):
        with st.spinner("Fetching live aircraft over India..."):
            df = fetch_live_flights()

    
        # APPLY FILTERS
    
        if callsign:
            df = df[df["callsign"].str.contains(callsign, case=False, na=False)]

        if airline_country:
            df = df[df["country"] == airline_country]

        if on_ground == "Airborne":
            df = df[df["on_ground"] == False]

        if on_ground == "On Ground":
            df = df[df["on_ground"] == True]

    
        # DISPLAY RESULTS
    
        st.success(f"✈️ {len(df)} live flights found")

        if df.empty:
            st.warning("No live flights match your filters.")
            return

        st.dataframe(
            df[
                [
                    "callsign",
                    "country",
                    "latitude",
                    "longitude",
                    "altitude_m",
                    "speed_mps",
                    "on_ground",
                ]
            ],
            use_container_width=True
        )
