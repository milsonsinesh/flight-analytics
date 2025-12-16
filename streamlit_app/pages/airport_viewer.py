import streamlit as st
import pandas as pd
import requests
from st_aggrid import AgGrid, GridOptionsBuilder


# OpenSky API

OPENSKY_URL = "https://opensky-network.org/api/states/all"

# Radius (degrees) for nearby aircraft
AIRPORT_RADIUS = 1.0


def fetch_live_aircraft():
    """Fetch live aircraft over India"""
    params = {
        "lamin": 6.0,
        "lamax": 35.0,
        "lomin": 68.0,
        "lomax": 97.0,
    }

    try:
        r = requests.get(OPENSKY_URL, params=params, timeout=10)
        if r.status_code != 200:
            return pd.DataFrame()

        data = r.json()
        states = data.get("states", [])

        if not states:
            return pd.DataFrame()

        df = pd.DataFrame(states, columns=[
            "icao24","callsign","origin_country","time_position","last_contact",
            "longitude","latitude","baro_altitude","on_ground","velocity",
            "heading","vertical_rate","sensors","geo_altitude",
            "squawk","spi","position_source"
        ])

        df = df.dropna(subset=["latitude", "longitude"])
        return df

    except Exception:
        return pd.DataFrame()


def aggrid_table(df, height=300):
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(
        paginationAutoPageSize=False,
        paginationPageSize=15
    )
    gb.configure_default_column(
        filterable=True,
        sortable=True,
        resizable=True
    )
    return AgGrid(
        df,
        gridOptions=gb.build(),
        height=height,
        enable_enterprise_modules=False
    )


def show():
    st.title("🛫 Airport Explorer — India")

    st.info(
        "This view shows **Indian airports** with **live air traffic nearby** "
        "using OpenSky Network real-time aircraft data."
    )


    # LOAD INDIAN AIRPORTS (FROM DB / OPENFLIGHTS)

    from streamlit_app.utils.db import run_query

    airports = run_query("""
        SELECT iata_code, name, city, country, latitude, longitude
        FROM airports
        WHERE country = 'India'
        ORDER BY name;
    """)

    if airports.empty:
        st.warning("No Indian airports found.")
        return


    # AIRPORT TABLE
 
    st.subheader("🇮🇳 Indian Airports")
    aggrid_table(airports, height=250)


    # AIRPORT SELECTOR

    codes = airports["iata_code"].dropna().tolist()
    selected = st.selectbox("Select an Airport", codes)

    airport = airports[airports["iata_code"] == selected].iloc[0]

    st.markdown("---")

    # AIRPORT DETAILS
 
    c1, c2, c3 = st.columns(3)
    c1.metric("Airport", airport["name"])
    c2.metric("City", airport["city"])
    c3.metric("IATA", airport["iata_code"])

    st.markdown("---")

    # FETCH LIVE AIRCRAFT

    with st.spinner("Fetching live aircraft near airport..."):
        live_df = fetch_live_aircraft()

    if live_df.empty:
        st.warning("Live aircraft data unavailable.")
        return

    # FILTER AIRCRAFT NEAR SELECTED AIRPORT

    nearby = live_df[
        (live_df["latitude"].between(
            airport["latitude"] - AIRPORT_RADIUS,
            airport["latitude"] + AIRPORT_RADIUS
        )) &
        (live_df["longitude"].between(
            airport["longitude"] - AIRPORT_RADIUS,
            airport["longitude"] + AIRPORT_RADIUS
        ))
    ]

    st.subheader(f"✈️ Live Aircraft Near {airport['iata_code']}")

    c1, c2 = st.columns(2)
    c1.metric("Nearby Aircraft", len(nearby))
    c2.metric("Grounded Aircraft", len(nearby[nearby["on_ground"] == True]))


    # MAP VIEW

    map_df = pd.concat([
        pd.DataFrame({
            "lat": [airport["latitude"]],
            "lon": [airport["longitude"]],
            "type": ["Airport"]
        }),
        pd.DataFrame({
            "lat": nearby["latitude"],
            "lon": nearby["longitude"],
            "type": ["Aircraft"] * len(nearby)
        })
    ])

    st.map(map_df.rename(columns={"lat": "latitude", "lon": "longitude"}))


    # AIRCRAFT TABLE

    with st.expander(" View Nearby Aircraft Details"):
        st.dataframe(
            nearby[[
                "callsign",
                "origin_country",
                "velocity",
                "geo_altitude",
                "on_ground"
            ]],
            use_container_width=True
        )


    # FOOTNOTE

    st.caption(
        " Airports sourced from OpenFlights dataset | "
        "Live aircraft data from OpenSky Network (Free API)"
    )
