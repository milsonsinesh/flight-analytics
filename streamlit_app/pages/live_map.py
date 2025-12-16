import streamlit as st
import pandas as pd
import pydeck as pdk
import requests
from datetime import datetime


# OpenSky bounding box for INDIA

# lat_min, lat_max, lon_min, lon_max
INDIA_BOUNDS = (6.0, 35.0, 68.0, 97.0)



def fetch_live_aircraft():
    """
    Fetch live aircraft data inside India bounding box.
    OpenSky API requires NO API KEY.
    """
    lat_min, lat_max, lon_min, lon_max = INDIA_BOUNDS

    url = (
        f"https://opensky-network.org/api/states/all?"
        f"lamin={lat_min}&lamax={lat_max}&lomin={lon_min}&lomax={lon_max}"
    )

    response = requests.get(url)

    if response.status_code != 200:
        st.error("❌ Error fetching data from OpenSky API")
        return pd.DataFrame()

    data = response.json()

    if "states" not in data or not data["states"]:
        return pd.DataFrame()

    rows = []
    for s in data["states"]:
        rows.append({
            "icao24": s[0],
            "callsign": s[1],
            "country": s[2],
            "longitude": s[5],
            "latitude": s[6],
            "altitude_m": s[13],
            "velocity_mps": s[9],
            "heading_deg": s[10],
            "timestamp": datetime.utcfromtimestamp(data["time"]).strftime("%Y-%m-%d %H:%M:%S")
        })

    df = pd.DataFrame(rows)
    df = df.dropna(subset=["latitude", "longitude"])  
    return df


def show():
    st.title("🗺️ Live Flight Map — (India Only)")

    st.info("Live aircraft positions are updated from OpenSky API every time you click refresh.")

    if st.button("🔄 Refresh Live Data"):
        st.cache_data.clear()

    @st.cache_data(ttl=20)  
    def load_data():
        return fetch_live_aircraft()

    df = load_data()

    st.subheader(f"✈️ Live Aircraft Count: {len(df)}")

    if df.empty:
        st.warning("No live aircraft found in the region right now.")
        return

    # Display table
    st.dataframe(df[["callsign", "country", "latitude", "longitude", "altitude_m", "velocity_mps"]])


    # PLOT ON MAP

    layer = pdk.Layer(
        "ScatterplotLayer",
        df,
        get_position="[longitude, latitude]",
        get_color="[255, 0, 0]",
        get_radius=25000,
        pickable=True,
    )

    view_state = pdk.ViewState(
        latitude=20.5937,  # Center of India
        longitude=78.9629,
        zoom=4.3,
        pitch=30,
    )

    tooltip = {
        "html": "<b>Callsign:</b> {callsign}<br/>"
                "<b>Country:</b> {country}<br/>"
                "<b>Altitude:</b> {altitude_m} m<br/>"
                "<b>Speed:</b> {velocity_mps} m/s<br/>"
    }

    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip=tooltip,
    )

    st.pydeck_chart(deck)
