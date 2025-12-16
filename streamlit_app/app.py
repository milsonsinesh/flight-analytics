import os
import sys
import streamlit as st
from streamlit_option_menu import option_menu

# FIX: Ensure Python can find streamlit_app package

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Import page modules

from streamlit_app.pages import (
    overview,
    airport_viewer,
    flight_search,
    delay_analysis,
    live_map,        
)

# Streamlit Page Configuration

st.set_page_config(
    page_title="AeroDataBox Flight Explorer",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# SIDEBAR NAVIGATION

with st.sidebar:

    # Display logo if exists
    logo_path = os.path.join(PROJECT_ROOT, "streamlit_app", "assets", "logo.png")
    if os.path.exists(logo_path):
        st.image(logo_path, width=160)

    st.markdown("## ✈️ Flight Analytics Dashboard")

    selected = option_menu(
        menu_title="Main Menu",
        options=[
            "Overview",
            "Airport Explorer",
            "Flight Search",
            "Delay Analysis",
            "Live Map",
        ],
        icons=[
            "bar-chart-line",
            "geo-alt",
            "search",
            "clock-history",
            "map",
        ],
        menu_icon="airplane",
        default_index=0,
        styles={
            "container": {"padding": "10px"},
            "icon": {"color": "#2E86C1", "font-size": "20px"},
            "nav-link": {"font-size": "16px", "padding": "8px"},
            "nav-link-selected": {"background-color": "#2E86C1"},
        },
    )

# GLOBAL UI STYLING

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 1.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("""
<style>
.metric-card {
    background: #f4f6f9;
    padding: 15px;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)



# PAGE ROUTING

if selected == "Overview":
    overview.show()

elif selected == "Airport Explorer":
    airport_viewer.show()

elif selected == "Flight Search":
    flight_search.show()

elif selected == "Delay Analysis":
    delay_analysis.show()

elif selected == "Live Map":
    live_map.show()


# FOOTER

with st.sidebar:
    st.markdown("---")
    st.caption("© 2025 AeroDataBox Flight Explorer")

