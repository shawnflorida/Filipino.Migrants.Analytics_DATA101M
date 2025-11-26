import streamlit as st
import pandas as pd
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Supplementary Dataset - Filipino Migrators", layout="wide")

# Load the dataset


@st.cache_data
def load_health_data():
    try:
        # Load the CSV file
        df = pd.read_csv('all_countries_supplementary.csv')
        return df
    except FileNotFoundError:
        st.error(
            "File 'all_countries_supplementary.csv' not found. Please make sure it's in the same directory.")
        return None
    except Exception as e:
        st.error(f"Error loading dataset: {e}")
        return None


# Load the data
df = load_health_data()

st.title("Health and Economic Indicators Dashboard")

if df is not None:
    # Display dataset info
    st.sidebar.markdown("### Dataset Info")
    st.sidebar.write(f"📊 **Rows:** {df.shape[0]:,}")
    st.sidebar.write(f"📈 **Columns:** {df.shape[1]}")
    st.sidebar.write(f"🌍 **Countries:** {df['Country Name'].nunique()}")
    st.sidebar.write(
        f"📅 **Year Range:** {df['Year'].min()} - {df['Year'].max()}")

    # Country selection
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Country Selection")
    available_countries = sorted(df['Country Name'].unique())
    selected_country = st.sidebar.selectbox(
        "Select a Country:",
        options=available_countries,
        index=available_countries.index(
            'Germany') if 'Germany' in available_countries else 0
    )

    # Year selection
    available_years = sorted(df['Year'].unique())
    selected_year = st.sidebar.selectbox(
        "Select Year:",
        options=available_years,
        index=len(available_years) - 1  # Default to latest year
    )

    # Filter data for selected country and year
    country_data = df[(df['Country Name'] == selected_country)
                      & (df['Year'] == selected_year)]

    # Display country information
    st.header(f"{selected_country} - {selected_year}")

    if not country_data.empty:
        # Get the specific row for the selected country and year
        row = country_data.iloc[0]

        # Display 3 KPI cards
        col1, col2, col3 = st.columns(3)

        # Life Expectancy
        with col1:
            life_exp = row.get('Life expectancy at birth, total (years)')
            if pd.notna(life_exp):
                st.metric(
                    label="Life Expectancy",
                    value=f"{life_exp:.1f} years",
                    help="Life expectancy at birth"
                )
            else:
                st.metric(
                    label="Life Expectancy",
                    value="No data",
                    delta="Data unavailable",
                    help="No life expectancy data available for this year"
                )

        # Health Expenditure
        with col2:
            health_exp = row.get(
                'Domestic general government health expenditure (% of GDP)')
            if pd.notna(health_exp):
                st.metric(
                    label="Health Expenditure",
                    value=f"{health_exp:.1f}% of GDP",
                    help="Government health expenditure as percentage of GDP"
                )
            else:
                st.metric(
                    label="Health Expenditure",
                    value="No data",
                    delta="Data unavailable",
                    help="No health expenditure data available for this year"
                )

        # Unemployment Rate
        with col3:
            unemployment = row.get(
                'Unemployment, total (% of total labor force)')
            if pd.notna(unemployment):
                st.metric(
                    label="Unemployment Rate",
                    value=f"{unemployment:.1f}%",
                    help="Total unemployment rate"
                )
            else:
                st.metric(
                    label="Unemployment Rate",
                    value="No data",
                    delta="Data unavailable",
                    help="No unemployment data available for this year"
                )

        # Additional metrics in a second row
        st.subheader("Additional Health Indicators")
        col4, col5, col6 = st.columns(3)

        # Diabetes Prevalence
        with col4:
            diabetes = row.get(
                'Diabetes prevalence (% of population ages 20 to 79)')
            if pd.notna(diabetes):
                st.metric(
                    label="Diabetes Prevalence",
                    value=f"{diabetes:.1f}%",
                    help="Diabetes prevalence among population ages 20-79"
                )
            else:
                st.metric(
                    label="Diabetes Prevalence",
                    value="No data",
                    help="No diabetes data available"
                )

        # Hypertension Prevalence
        with col5:
            hypertension = row.get(
                'Prevalence of hypertension (% of adults ages 30-79)')
            if pd.notna(hypertension):
                st.metric(
                    label="Hypertension Prevalence",
                    value=f"{hypertension:.1f}%",
                    help="Hypertension prevalence among adults ages 30-79"
                )
            else:
                st.metric(
                    label="Hypertension Prevalence",
                    value="No data",
                    help="No hypertension data available"
                )

        # Adult Mortality Rate (Female)
        with col6:
            mortality_female = row.get(
                'Mortality rate, adult, female (per 1,000 female adults)')
            if pd.notna(mortality_female):
                st.metric(
                    label="Adult Female Mortality",
                    value=f"{mortality_female:.1f} per 1,000",
                    help="Adult female mortality rate per 1,000"
                )
            else:
                st.metric(
                    label="Adult Female Mortality",
                    value="No data",
                    help="No mortality data available"
                )

        # Show trend data for the selected country
        st.markdown("---")
        st.subheader(f"Trend Data for {selected_country}")

        # Get all data for the selected country
        country_trend_data = df[df['Country Name'] == selected_country]

        # Display trend metrics if available
        trend_col1, trend_col2, trend_col3 = st.columns(3)

        with trend_col1:
            if 'Life expectancy at birth, total (years)' in country_trend_data.columns:
                life_data = country_trend_data['Life expectancy at birth, total (years)'].dropna(
                )
                if len(life_data) > 1:
                    life_change = life_data.iloc[-1] - life_data.iloc[0]
                    st.metric(
                        label="Life Expectancy Trend",
                        value=f"{life_data.iloc[-1]:.1f} years",
                        delta=f"{life_change:+.1f} years",
                        help="Change over available data period"
                    )

        with trend_col2:
            if 'Domestic general government health expenditure (% of GDP)' in country_trend_data.columns:
                health_data = country_trend_data['Domestic general government health expenditure (% of GDP)'].dropna(
                )
                if len(health_data) > 1:
                    health_change = health_data.iloc[-1] - health_data.iloc[0]
                    st.metric(
                        label="Health Expenditure Trend",
                        value=f"{health_data.iloc[-1]:.1f}%",
                        delta=f"{health_change:+.1f}%",
                        help="Change over available data period"
                    )

        with trend_col3:
            if 'Unemployment, total (% of total labor force)' in country_trend_data.columns:
                unemployment_data = country_trend_data['Unemployment, total (% of total labor force)'].dropna(
                )
                if len(unemployment_data) > 1:
                    unemployment_change = unemployment_data.iloc[-1] - \
                        unemployment_data.iloc[0]
                    st.metric(
                        label="Unemployment Trend",
                        value=f"{unemployment_data.iloc[-1]:.1f}%",
                        delta=f"{unemployment_change:+.1f}%",
                        help="Change over available data period"
                    )

        # Show data table for the selected country
        with st.expander(f"View all data for {selected_country}"):
            display_columns = ['Year', 'Life expectancy at birth, total (years)',
                               'Domestic general government health expenditure (% of GDP)',
                               'Unemployment, total (% of total labor force)',
                               'Diabetes prevalence (% of population ages 20 to 79)',
                               'Prevalence of hypertension (% of adults ages 30-79)']

            # Only show columns that exist in the dataframe
            available_columns = [
                col for col in display_columns if col in country_trend_data.columns]
            st.dataframe(country_trend_data[available_columns].sort_values('Year', ascending=False),
                         use_container_width=True)

    else:
        st.warning(
            f"No data available for {selected_country} in {selected_year}")

        # Show available years for the selected country
        country_years = df[df['Country Name'] ==
                           selected_country]['Year'].unique()
        if len(country_years) > 0:
            st.info(
                f"Available years for {selected_country}: {sorted(country_years)}")

    # Show sample of the full dataset
    st.markdown("---")
    st.subheader("Full Dataset Sample")
    st.dataframe(df.head(10), use_container_width=True)

else:
    st.warning("No data loaded. Please check if the CSV file exists.")
