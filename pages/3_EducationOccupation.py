# pages/3_EducationOccupation.py
import streamlit as st
import pandas as pd
import altair as alt
import numpy as np

# ------------------------
# Load datasets and clean column names
# ------------------------


def load_educ_pivot(path="data/educ_pivot.csv"):
    df = pd.read_csv(path)
    df = df.fillna(0)
    # Clean column names
    df.columns = [col.replace('_', ' ').title() for col in df.columns]
    return df


def load_occu_pivot(path="data/occu_pivot.csv"):
    df = pd.read_csv(path)
    df = df.fillna(0)
    # Clean column names
    df.columns = [col.replace('_', ' ').title() for col in df.columns]
    return df


# Load data with error handling
try:
    educ_df = load_educ_pivot()
    occu_df = load_occu_pivot()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

st.title("📚 Education and Occupation Analysis")

# Introduction
st.markdown("""
This interactive dashboard explores the evolution of education levels and occupation patterns over time. 
Use the filters below to analyze specific trends and patterns in the data.
""")

# ------------------------
# Sidebar Filters
# ------------------------
st.sidebar.header("🔍 Filter Settings")

# Year range filter
year_range = st.sidebar.slider(
    "Select Year Range",
    min_value=int(educ_df['Year'].min()),
    max_value=int(educ_df['Year'].max()),
    value=(int(educ_df['Year'].min()), int(educ_df['Year'].max()))
)

# Education level filter
educ_columns = [col for col in educ_df.columns if col != 'Year']
selected_educ_levels = st.sidebar.multiselect(
    "Filter Education Levels",
    options=educ_columns,
    default=educ_columns[:3] if len(educ_columns) > 3 else educ_columns
)

# Occupation filter
occu_columns = [col for col in occu_df.columns if col != 'Year']
selected_occupations = st.sidebar.multiselect(
    "Filter Occupations",
    options=occu_columns,
    default=occu_columns[:3] if len(occu_columns) > 3 else occu_columns
)

# Apply year filters
educ_filtered = educ_df[(educ_df['Year'] >= year_range[0])
                        & (educ_df['Year'] <= year_range[1])]
occu_filtered = occu_df[(occu_df['Year'] >= year_range[0])
                        & (occu_df['Year'] <= year_range[1])]

# ------------------------
# Education Level Analysis
# ------------------------
st.header("🎓 Education Level Analysis")

if selected_educ_levels:
    # Prepare education data for heatmap
    educ_melted = educ_filtered.melt(id_vars=['Year'],
                                     value_vars=selected_educ_levels,
                                     var_name='Education Level',
                                     value_name='Count')

    # Create improved education heatmap
    educ_heatmap = alt.Chart(educ_melted).mark_rect().encode(
        x=alt.X('Year:O', title='Year', axis=alt.Axis(labelAngle=0)),
        y=alt.Y('Education Level:N', title='Education Level', sort='-x'),
        color=alt.Color('Count:Q',
                        title='Count',
                        scale=alt.Scale(scheme='blues')),
        tooltip=['Year', 'Education Level', 'Count']
    ).properties(
        width=700,
        height=400,
        title='Education Level Distribution Over Time'
    )

    st.altair_chart(educ_heatmap, use_container_width=True)
else:
    st.info("Please select at least one education level to display the heatmap.")

# Education insights
st.markdown("""
**Interpretation:**
- Darker blue shades indicate higher concentrations of individuals with specific education levels
- Look for vertical patterns to identify years with significant educational shifts
- Horizontal patterns reveal how specific education levels evolve over time
- Watch for emerging trends in higher education adoption
""")

# ------------------------
# Occupation Analysis
# ------------------------
st.header("💼 Occupation Analysis")

if selected_occupations:
    # Prepare occupation data for heatmap
    occu_melted = occu_filtered.melt(id_vars=['Year'],
                                     value_vars=selected_occupations,
                                     var_name='Occupation',
                                     value_name='Count')

    # Create improved occupation heatmap
    occu_heatmap = alt.Chart(occu_melted).mark_rect().encode(
        x=alt.X('Year:O', title='Year', axis=alt.Axis(labelAngle=0)),
        y=alt.Y('Occupation:N', title='Occupation', sort='-x'),
        color=alt.Color('Count:Q',
                        title='Count',
                        scale=alt.Scale(scheme='reds')),
        tooltip=['Year', 'Occupation', 'Count']
    ).properties(
        width=700,
        height=400,
        title='Occupation Distribution Over Time'
    )

    st.altair_chart(occu_heatmap, use_container_width=True)
else:
    st.info("Please select at least one occupation to display the heatmap.")

# Occupation insights
st.markdown("""
**Interpretation:**
- Red intensity shows concentration of workforce in different occupations
- Identify growing occupations (increasing red intensity over time)
- Spot declining occupations (decreasing red intensity)
- Note any occupational shifts that correlate with economic or technological changes
""")

# ------------------------
# Comparative Trend Analysis
# ------------------------
st.header("📈 Comparative Trend Analysis")

col1, col2 = st.columns(2)

with col1:
    if selected_educ_levels:
        # Education trend comparison
        educ_comparison_data = educ_filtered.melt(id_vars=['Year'],
                                                  value_vars=selected_educ_levels,
                                                  var_name='Education Level',
                                                  value_name='Count')

        educ_trend_chart = alt.Chart(educ_comparison_data).mark_line(point=True).encode(
            x=alt.X('Year:O', title='Year'),
            y=alt.Y('Count:Q', title='Number of Individuals'),
            color=alt.Color('Education Level:N', title='Education Level'),
            tooltip=['Year', 'Education Level', 'Count']
        ).properties(
            title='Education Level Trends Comparison',
            height=300
        )
        st.altair_chart(educ_trend_chart, use_container_width=True)

with col2:
    if selected_occupations:
        # Occupation trend comparison
        occu_comparison_data = occu_filtered.melt(id_vars=['Year'],
                                                  value_vars=selected_occupations,
                                                  var_name='Occupation',
                                                  value_name='Count')

        occu_trend_chart = alt.Chart(occu_comparison_data).mark_line(point=True).encode(
            x=alt.X('Year:O', title='Year'),
            y=alt.Y('Count:Q', title='Number of Individuals'),
            color=alt.Color('Occupation:N', title='Occupation'),
            tooltip=['Year', 'Occupation', 'Count']
        ).properties(
            title='Occupation Trends Comparison',
            height=300
        )
        st.altair_chart(occu_trend_chart, use_container_width=True)

# ------------------------
# Individual Trend Analysis
# ------------------------
st.header("🔍 Individual Trend Analysis")

col3, col4 = st.columns(2)

with col3:
    selected_education = st.selectbox(
        "Select Education Level for Detailed Analysis",
        options=educ_columns,
        key="educ_select"
    )

with col4:
    selected_occupation = st.selectbox(
        "Select Occupation for Detailed Analysis",
        options=occu_columns,
        key="occu_select"
    )

col5, col6 = st.columns(2)

with col5:
    # Education trend line chart
    educ_trend_data = educ_filtered[['Year', selected_education]].copy()
    educ_trend_chart = alt.Chart(educ_trend_data).mark_line(point=True, color='blue').encode(
        x=alt.X('Year:O', title='Year'),
        y=alt.Y(f'{selected_education}:Q', title='Count'),
        tooltip=['Year', selected_education]
    ).properties(
        title=f'{selected_education} Trend Over Time',
        height=300
    )
    st.altair_chart(educ_trend_chart, use_container_width=True)

with col6:
    # Occupation trend line chart
    occu_trend_data = occu_filtered[['Year', selected_occupation]].copy()
    occu_trend_chart = alt.Chart(occu_trend_data).mark_line(point=True, color='red').encode(
        x=alt.X('Year:O', title='Year'),
        y=alt.Y(f'{selected_occupation}:Q', title='Count'),
        tooltip=['Year', selected_occupation]
    ).properties(
        title=f'{selected_occupation} Trend Over Time',
        height=300
    )
    st.altair_chart(occu_trend_chart, use_container_width=True)

# ------------------------
# Key Metrics and Insights
# ------------------------
st.header("💡 Key Insights")

# Calculate some key metrics
col7, col8, col9 = st.columns(3)

with col7:
    if selected_educ_levels:
        total_education_entries = educ_filtered[selected_educ_levels].sum(
        ).sum()
        st.metric("Total Education Records", f"{total_education_entries:,}")

with col8:
    if selected_occupations:
        total_occupation_entries = occu_filtered[selected_occupations].sum(
        ).sum()
        st.metric("Total Occupation Records", f"{total_occupation_entries:,}")

with col9:
    year_span = year_range[1] - year_range[0] + 1
    st.metric("Years Analyzed", year_span)

# Data Quality Notes
st.markdown("---")
st.caption("""
**Data Notes:** 
- All values represent counts of individuals in each category
- Empty cells are treated as zero values
- Use the sidebar filters to focus on specific time periods and categories
- Trends should be interpreted in the context of the selected year range
""")
