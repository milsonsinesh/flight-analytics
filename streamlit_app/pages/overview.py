import streamlit as st
import plotly.express as px
import pandas as pd
import requests
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
def fetch_live_states():
    """Fetch live aircraft states over India"""
    r = requests.get(OPEN_SKY_URL, params=INDIA_BOUNDS, timeout=10)
    if r.status_code != 200:
        return None, None

    data = r.json()
    states = data.get("states", [])

    if not states:
        return None, None

    df = pd.DataFrame(states, columns=[
        "icao24","callsign","origin_country","time_position","last_contact",
        "longitude","latitude","baro_altitude","on_ground","velocity",
        "heading","vertical_rate","sensors","geo_altitude",
        "squawk","spi","position_source"
    ])

    df = df.dropna(subset=["latitude", "longitude"])
    return df, data["time"]


def show():
    st.header("🌍 Live Air Traffic Overview — (India)")

    st.info(
        "This dashboard shows **REAL-TIME aircraft traffic over India** "
        "using the OpenSky Network free API."
    )


    # FETCH LIVE DATA

    with st.spinner("Fetching live aircraft data..."):
        df, ts = fetch_live_states()

    if df is None or df.empty:
        st.warning("Live OpenSky data unavailable.")
        return


    # KPI METRICS (INDIA ONLY)

    live_aircraft = len(df)
    avg_speed = round(df["velocity"].mean() * 3.6, 1)  # km/h
    avg_altitude = round(df["geo_altitude"].mean() * 3.28084, 0)  # ft
    last_update = datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("✈️ Live Aircraft", live_aircraft)
    c2.metric("🚀 Avg Speed (km/h)", avg_speed)
    c3.metric("🛫 Avg Altitude (ft)", avg_altitude)
    c4.metric("🕒 Last Update (UTC)", last_update)

    st.markdown("---")


    # FLIGHTS OVER TIME (LAST 30 SECONDS)

    st.subheader("📈 Aircraft Activity (Last 30 Seconds)")

    # Simulate short-term trend
    activity = df.copy()
    activity["time"] = pd.to_datetime(ts, unit="s")

    fig = px.histogram(
        activity,
        x="time",
        nbins=10,
        title="Live Aircraft Snapshot (Real-Time)",
        labels={"time": "Timestamp"}
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")


    # LIVE DATA TABLE

    st.subheader("🧾 Live Aircraft Details (India)")

    st.dataframe(
        df[
            [
                "callsign",
                "origin_country",
                "latitude",
                "longitude",
                "velocity",
                "geo_altitude",
                "on_ground",
            ]
        ],
        use_container_width=True
    )


    # FOOTNOTE (VERY IMPORTANT)

    st.caption(
        "ℹ️ OpenSky Network provides **live aircraft state data only**. "
        "Airport-level, schedule, and delay analytics are not available in the free API."
    )
