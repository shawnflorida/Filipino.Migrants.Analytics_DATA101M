import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Filipino Migrators Dashboard",
    page_icon="🇵🇭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .subtitle {
        font-size: 1.2rem;
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("🇵🇭 Filipino Migrators Dashboard")
st.sidebar.markdown("### Navigation")
st.sidebar.markdown("---")
st.sidebar.info("Select a page above to explore different aspects of Filipino migration data.")

# Main content
st.markdown('<p class="main-header">🇵🇭 Filipino Migrators Dashboard</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Exploring Migration Patterns and Trends</p>', unsafe_allow_html=True)

# Introduction section
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 📊 Dashboard")
    st.markdown("Get a comprehensive overview of Filipino migration statistics and key metrics.")
    
with col2:
    st.markdown("### 🗺️ Migration Pattern")
    st.markdown("Explore detailed migration trends by region, country, and time period.")
    
with col3:
    st.markdown("### 📈 Related Dataset")
    st.markdown("Compare and analyze multiple variables across different regions and countries.")

st.markdown("---")

# Welcome message
st.markdown("""
### About This Dashboard

This interactive application provides comprehensive insights into Filipino migration patterns worldwide. 
Analyze trends, explore regional differences, and discover meaningful patterns in the data.

**👈 Get started by selecting a page from the sidebar!**
""")

# Footer
st.markdown("---")
st.caption("Data Source: Filipino Migration Statistics | Last Updated: 2024")
