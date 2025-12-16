"""
Real-Time Delay Analysis (India)
Derived from OpenSky Network live aircraft data
"""

import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime


# OpenSky India Bounding Box

INDIA_BOUNDS = {
    "lamin": 6.0,
    "lamax": 35.0,
    "lomin": 68.0,
    "lomax": 97.0
}

OPEN_SKY_URL = "https://opensky-network.org/api/states/all"


@st.cache_data(ttl=30)
def fetch_live_opensky_data():
    """Fetch live aircraft data over India from OpenSky"""
    try:
        r = requests.get(OPEN_SKY_URL, params=INDIA_BOUNDS, timeout=10)
        if r.status_code != 200:
            return pd.DataFrame(), None

        data = r.json()
        states = data.get("states", [])

        if not states:
            return pd.DataFrame(), None

        df = pd.DataFrame(states, columns=[
            "icao24","callsign","origin_country","time_position","last_contact",
            "longitude","latitude","baro_altitude","on_ground","velocity",
            "heading","vertical_rate","sensors","geo_altitude",
            "squawk","spi","position_source"
        ])

        df = df.dropna(subset=["latitude", "longitude"])

        df["velocity_kmh"] = df["velocity"] * 3.6
        df["altitude_ft"] = df["geo_altitude"] * 3.28084
        df["timestamp"] = datetime.utcfromtimestamp(data["time"])

        return df, data["time"]

    except Exception:
        return pd.DataFrame(), None


def show():
    st.title("⏱️ Real-Time Delay Analysis — India")

    st.info(
        "This dashboard shows **real-time delay risk indicators** derived from live aircraft "
        "behavior over India using the OpenSky Network free API.\n\n"
        "**Note:** OpenSky does NOT provide actual delay minutes. "
        "All delay insights are analytically derived from aircraft speed, altitude, "
        "and ground status."
    )


    # FETCH LIVE DATA

    with st.spinner("Fetching live OpenSky aircraft data..."):
        df, ts = fetch_live_opensky_data()

    if df.empty:
        st.warning("Live OpenSky data is currently unavailable.")
        return

    # DERIVED DELAY INDICATORS

    grounded = df[df["on_ground"] == True]
    slow_aircraft = df[df["velocity_kmh"] < 150]
    low_altitude = df[df["altitude_ft"] < 3000]

    # KPI METRICS

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("✈️ Live Aircraft", len(df))
    c2.metric("🛬 Grounded Aircraft", len(grounded))
    c3.metric("🐢 Slow Aircraft (<150 km/h)", len(slow_aircraft))
    c4.metric("📉 Low Altitude (<3000 ft)", len(low_altitude))

    st.markdown("---")

    # CONGESTION / DELAY RISK SCORE

    congestion_score = round(
        ((len(grounded) + len(slow_aircraft)) / max(len(df), 1)) * 100,
        1
    )

    st.subheader("🚦 Live Delay Risk Indicator")

    st.progress(min(congestion_score / 100, 1.0))
    st.write(f"**Estimated Delay Risk:** `{congestion_score}%`")

    if congestion_score > 60:
        st.error("High congestion detected — potential delays likely.")
    elif congestion_score > 35:
        st.warning("Moderate congestion — monitor operations.")
    else:
        st.success("Low congestion — operations normal.")

    st.markdown("---")

    # SPEED VS ALTITUDE VISUALIZATION

    st.subheader(" Speed vs Altitude — Live Aircraft")

    fig = px.scatter(
        df,
        x="velocity_kmh",
        y="altitude_ft",
        color="on_ground",
        hover_data=["callsign", "origin_country"],
        labels={
            "velocity_kmh": "Speed (km/h)",
            "altitude_ft": "Altitude (ft)",
            "on_ground": "On Ground"
        },
        title="Operational Delay Indicators from Live Air Traffic"
    )

    st.plotly_chart(fig, use_container_width=True)

    # LIVE AIRCRAFT TABLE (OPTIONAL)

    with st.expander(" View Live Aircraft Data"):
        st.dataframe(
            df[
                [
                    "callsign",
                    "origin_country",
                    "velocity_kmh",
                    "altitude_ft",
                    "on_ground"
                ]
            ],
            use_container_width=True
        )

  
    # FOOTNOTE

    st.caption(
        " Data Source: OpenSky Network (Free API) | "
        "Delay metrics are **derived operational indicators**, not airline-reported delays."
    )
