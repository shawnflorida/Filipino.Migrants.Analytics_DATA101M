import streamlit as st
import pandas as pd
import numpy as np

# Page configuration
st.set_page_config(page_title="Dashboard - Filipino Migrators", layout="wide")

st.title("Dashboard of Filipino Migrators")

# Create a multi-column layout similar to the design
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Total Migrators", value="2.3M", delta="+12%")
    st.metric(label="Top Destination", value="USA", delta="+5%")

with col2:
    st.metric(label="Average Age", value="34", delta="-2%")
    st.metric(label="Female Migrators", value="58%", delta="+3%")

with col3:
    st.metric(label="OFW Remittances", value="$32B", delta="+8%")
    st.metric(label="Top Occupation", value="Healthcare", delta="+15%")

with col4:
    st.metric(label="Regions", value="17", delta="0%")
    st.metric(label="Countries", value="190+", delta="+2")

# Main grid layout
st.markdown("### Migration Overview")

# First row of charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("Migration Trends (2000-2025)")
    # Placeholder chart data
    years = list(range(2000, 2026))
    migrants = [1000000 + i * 50000 +
                np.random.randint(-20000, 20000) for i in range(len(years))]

    chart_data = pd.DataFrame({
        'Year': years,
        'Migrants': migrants
    }).set_index('Year')

    st.line_chart(chart_data)

with col2:
    st.subheader("Top Destination Countries")
    countries = ['USA', 'Saudi Arabia', 'UAE',
                 'Singapore', 'Japan', 'UK', 'Canada', 'Australia']
    percentages = [35, 18, 12, 8, 7, 6, 5, 4]

    country_data = pd.DataFrame({
        'Country': countries,
        'Percentage': percentages
    }).set_index('Country')

    st.bar_chart(country_data)

# Second row of charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("Occupation Distribution")
    occupations = ['Healthcare', 'Domestic', 'Construction',
                   'Seafarers', 'Engineering', 'Others']
    counts = [450000, 380000, 320000, 280000, 220000, 700000]

    occ_data = pd.DataFrame({
        'Occupation': occupations,
        'Count': counts
    }).set_index('Occupation')

    st.bar_chart(occ_data)

with col2:
    st.subheader("Regional Distribution")
    regions = ['NCR', 'Region IV-A', 'Region III',
               'Region I', 'Region VII', 'Others']
    migrants = [550000, 480000, 320000, 280000, 220000, 450000]

    region_data = pd.DataFrame({
        'Region': regions,
        'Migrants': migrants
    }).set_index('Region')

    st.area_chart(region_data)

# Placeholder text section
st.markdown("---")
st.markdown("""
### About the Data
This dashboard provides comprehensive insights into Filipino migration patterns worldwide. 
The data showcases trends, demographics, and economic impacts of overseas Filipino workers.

**Key Insights:**
- Steady increase in migration numbers since 2000
- Healthcare professionals represent the largest occupational group
- North America and Middle East remain primary destinations
- Significant contribution to Philippine economy through remittances

*Note: This dashboard uses sample data for demonstration purposes.*
""")
