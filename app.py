import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Filipino Migrators Dashboard",
    page_icon="🇵🇭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar navigation
st.sidebar.title("🇵🇭 Filipino Migrators Dashboard")
st.sidebar.markdown("### Navigation")

# Main content area
st.title("Welcome to Filipino Migrators Dashboard")
st.markdown("""
This application provides insights into Filipino migration patterns and trends.

Use the sidebar to navigate between different pages:
- **Dashboard**: Overview of Filipino migrators
- **Migration Pattern**: Explore migration trends by region and country
- **Related Dataset**: Compare variables across regions and countries
""")

st.markdown("---")
st.info("👈 Select a page from the sidebar to get started!")
