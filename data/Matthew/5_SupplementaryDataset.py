import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="Supplementary Dataset - Filipino Migrators", layout="wide")

# Load the dataset


@st.cache_data
def load_health_data():
    try:
        # Load the CSV file
        base = "data"
        df = pd.read_csv(f"{base}/Matthew/all_countries_supplementary_updated.csv")
        df2 = pd.read_csv(f"{base}/merged_data.csv")
        return df,df2
    except FileNotFoundError:
        st.error(
            "File 'all_countries_supplementary.csv' not found. Please make sure it's in the same directory.")
        return None
    except Exception as e:
        st.error(f"Error loading dataset: {e}")
        return None


# Load the data
df, migrant = load_health_data()
country_list = {'united_states_of_america','united_arab_emirates','united_kingdom','saudi_arabia','canada','australia',
                'japan','singapore','hongkong','italy','germany','france','south_korea','spain','malaysia','qatar',
                'kuwait','israel','china_(p.r.o.c.)', 'russian_federation_/_ussr'}
health_country_list = {'United States', 'Hong Kong SAR, China', 'Russian Federation','Korea, Rep.','United Arab Emirates',
                        'United Kingdom','Saudi Arabia','Canada','Australia','Japan','Singapore','Italy','Germany','France','Spain',
                        'Malaysia','Qatar','Kuwait','Israel','China'}                
country_mapping = {
            'united_states_of_america': 'USA',
            'united_arab_emirates': 'United Arab Emirates',
            'united_kingdom': 'United Kingdom',
            'saudi_arabia': 'Saudi Arabia',
            'canada': 'Canada',
            'australia': 'Australia',
            'japan': 'Japan',
            'singapore': 'Singapore',
            'hongkong': 'Hong Kong',
            'italy': 'Italy',
            'germany': 'Germany',
            'france': 'France',
            'south_korea': 'South Korea',
            'spain': 'Spain',
            'malaysia': 'Malaysia',
            'qatar': 'Qatar',
            'kuwait': 'Kuwait',
            'israel': 'Israel',
            'china_(p.r.o.c.)': 'China',
            'russian_federation_/_ussr': 'Russia'
        }
health_country_mapping = {
    'United States': 'USA',
    'Hong Kong SAR, China':'Hong Kong',
    'Russian Federation':'Russia',
    'Korea, Rep.': 'South Korea'}
    
migrant_fixed = migrant.melt(id_vars=['year'], value_vars = country_list, var_name = 'country',value_name = 'migrants')
migrant_fixed['country'] = migrant_fixed['country'].replace(country_mapping)
df = df[df['Country Name'].isin(health_country_list)]
df['Country Name'] = df['Country Name'].replace(health_country_mapping)
migrant_fixed.rename(columns = {'country':'Country Name','year':'Year'}, inplace=True)
migrant_final = pd.merge(df,migrant_fixed,on=['Country Name','Year'],how = 'left')

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
        col1, col2, col3,col4 = st.columns(4)

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

        # GDP
        with col3:
            GDP = row.get(
                'GDP')
            if pd.notna(GDP):
                st.metric(
                    label="Gross Domestic Product (US Dollars)",
                    value=f"{GDP:.1f}%",
                    help="Gross Domestic Product in US Dollars"
                )
            else:
                st.metric(
                    label="Gross Domestic Product (US Dollars)",
                    value="No data",
                    delta="Data unavailable",
                    help="No GDP data available for this year"
                )
        
        # Unemployment Rate
        with col4:
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
        col5, col6, col7, col8 = st.columns(4)

        # Diabetes Prevalence
        with col5:
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
        with col6:
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
        with col7:
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
            
         # Adult Mortality Rate (Male)
        with col8:
            mortality_male = row.get(
                'Mortality rate, adult, male (per 1,000 male adults)')
            if pd.notna(mortality_female):
                st.metric(
                    label="Adult Male Mortality",
                    value=f"{mortality_female:.1f} per 1,000",
                    help="Adult male mortality rate per 1,000"
                )
            else:
                st.metric(
                    label="Adult Male Mortality",
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


        # Show available years for the selected country
        country_years = df[df['Country Name'] ==
                           selected_country]['Year'].unique()
        if len(country_years) > 0:
            st.info(
                f"Available years for {selected_country}: {sorted(country_years)}")
        else:
            st.warning(
                f"No data available for {selected_country} in {selected_year}")

    # Show trend data for the selected country
    st.markdown("---")
    st.subheader(f"Health and Economic Indicator Trends for {selected_country}")
    chart_data = migrant_final[(migrant_final['Country Name'] == selected_country)]

    #Life Expectancy
    st.subheader("⌛ Life Expectancy")
    
    col9, col10 = st.columns(2)

    with col9:
        fig_life = go.Figure()
        fig_life.add_trace(
            go.Scatter(
                x=chart_data['Year'], 
                y=chart_data['Life expectancy at birth, total (years)'],
                mode='lines+markers',
                hovertemplate=(
                    "<b>Year %{x}</b><br>"
                    "Life Expectancy: <span style='color:#00d4ff'><b>%{y:,.0f}</b></span><br>"
                )
            )
        )
        fig_life.update_layout(
            xaxis_title="Years",
            yaxis_title="Life Expectancy (Years)",
            title = "Life Expectancy (Years) Trend"
        )
        st.plotly_chart(fig_life, use_container_width=True)
    with col10:
        fig_life2 = go.Figure()
        fig_life2.add_trace(
            go.Scatter(
                x=chart_data['Life expectancy at birth, total (years)'], 
                y=chart_data['migrants'],
                text = chart_data['Year'],
                mode='markers',
                hovertemplate=(
                    "<b>Year %{text}</b><br>"
                    "Life Expectancy: <span style='color:#00d4ff'><b>%{x:,.2f}</b></span><br>"
                    "Migrant: <span style='color:#00d4ff'><b>%{y:,.0f}</b></span><br>"
                )
            )
        )
        fig_life2.update_layout(
            xaxis_title="Life Expectancy (Years)",
            yaxis_title="Migrants",
            title = "Life Expectancy (Years) vs Migrants"
        )
        st.plotly_chart(fig_life2, use_container_width=True)
    
    #Health Expenditure
    st.subheader("🏥 Health Expenditure")
    
    col11, col12 = st.columns(2)

    with col11:
        fig_health = go.Figure()
        fig_health.add_trace(
            go.Scatter(
                x=chart_data['Year'], 
                y=chart_data['Domestic general government health expenditure (% of GDP)'],
                mode='lines+markers',
                hovertemplate=(
                    "<b>Year %{x}</b><br>"
                    "Domestic Health Expenditure: <span style='color:#00d4ff'><b>%{y:,.2f}%</b></span><br>"
                )
            )
        )
        fig_health.update_layout(
            xaxis_title="Years",
            yaxis_title="Health Expenditure (% of GDP)",
            title = "Health Expenditure (% of GDP) Trend"
        )
        st.plotly_chart(fig_health, use_container_width=True)
    with col12:
        fig_health2 = go.Figure()
        fig_health2.add_trace(
            go.Scatter(
                x=chart_data['Domestic general government health expenditure (% of GDP)'], 
                y=chart_data['migrants'],
                text = chart_data['Year'],
                mode='markers',
                hovertemplate=(
                    "<b>Year %{text}</b><br>"
                    "Domestic Health Expenditure: <span style='color:#00d4ff'><b>%{x:,.2f}%</b></span><br>"
                    "Migrant: <span style='color:#00d4ff'><b>%{y:,.0f}</b></span><br>"
                )
            )
        )
        fig_health2.update_layout(
            xaxis_title="Health Expenditure (% of GDP)",
            yaxis_title="Migrants",
            title = "Health Expenditure (% of GDP) vs Migrants"
        )
        st.plotly_chart(fig_health2, use_container_width=True)
    
    #GDP
    st.subheader("💵 Gross Domestic Product (GDP)")
    
    col13, col14 = st.columns(2)

    with col13:
        fig_gdp = go.Figure()
        fig_gdp.add_trace(
            go.Scatter(
                x=chart_data['Year'], 
                y=chart_data['GDP'],
                mode='lines+markers',
                hovertemplate=(
                    "<b>Year %{x}</b><br>"
                    "Gross Domestic Product (US Dollars): <span style='color:#00d4ff'><b>%{y:,.0f}</b></span><br>"
                )
            )
        )
        fig_gdp.update_layout(
            xaxis_title="Years",
            yaxis_title="Gross Domestic Product (US Dollars)",
            title = "Gross Domestic Product (US Dollars) Trend"
        )
        st.plotly_chart(fig_gdp, use_container_width=True)
    with col14:
        fig_gdp2 = go.Figure()
        fig_gdp2.add_trace(
            go.Scatter(
                x=chart_data['GDP'], 
                y=chart_data['migrants'],
                text = chart_data['Year'],
                mode='markers',
                hovertemplate=(
                    "<b>Year %{text}</b><br>"
                    "Gross Domestic Product (US Dollars): <span style='color:#00d4ff'><b>%{x:,.0f}</b></span><br>"
                    "Migrant: <span style='color:#00d4ff'><b>%{y:,.0f}</b></span><br>"
                )
            )
        )
        fig_gdp2.update_layout(
            xaxis_title="Gross Domestic Product (US Dollars)",
            yaxis_title="Migrants",
            title = "Gross Domestic Product (US Dollars) vs Migrants"
        )
        st.plotly_chart(fig_gdp2, use_container_width=True)
    
    #Unemployment
    st.subheader("💼 Unemployment (%)")
    
    col15, col16 = st.columns(2)

    with col15:
        fig_unemp = go.Figure()
        fig_unemp.add_trace(
            go.Scatter(
                x=chart_data['Year'], 
                y=chart_data['Unemployment, total (% of total labor force)'],
                mode='lines+markers',
                hovertemplate=(
                    "<b>Year %{x}</b><br>"
                    "Unemployment (%): <span style='color:#00d4ff'><b>%{y:,.2f}%</b></span><br>"
                )
            )
        )
        fig_unemp.update_layout(
            xaxis_title="Years",
            yaxis_title="Unemployment (%)",
            title = "Unemployment (%) Trend"
        )
        st.plotly_chart(fig_unemp, use_container_width=True)
    with col16:
        fig_unemp2 = go.Figure()
        fig_unemp2.add_trace(
            go.Scatter(
                x=chart_data['Unemployment, total (% of total labor force)'], 
                y=chart_data['migrants'],
                text = chart_data['Year'],
                mode='markers',
                hovertemplate=(
                    "<b>Year %{text}</b><br>"
                    "Unemployment (%): <span style='color:#00d4ff'><b>%{x:,.2f}%</b></span><br>"
                    "Migrant: <span style='color:#00d4ff'><b>%{y:,.0f}</b></span><br>"
                )
            )
        )
        fig_unemp2.update_layout(
            xaxis_title="Unemployment (%)",
            yaxis_title="Migrants",
            title = "Unemployment (%) vs Migrants"
        )
        st.plotly_chart(fig_unemp2, use_container_width=True)

    #Diabetes
    st.subheader("🩸 Diabetes Prevalence (% of population ages 20 to 79)")
    
    col17, col18 = st.columns(2)

    with col17:
        fig_diab = go.Figure()
        fig_diab.add_trace(
            go.Scatter(
                x=chart_data['Year'], 
                y=chart_data['Diabetes prevalence (% of population ages 20 to 79)'],
                mode='lines+markers',
                hovertemplate=(
                    "<b>Year %{x}</b><br>"
                    "Diabetes Prevalence (% of population ages 20 to 79): <span style='color:#00d4ff'><b>%{y:,.2f}%</b></span><br>"
                )
            )
        )
        fig_diab.update_layout(
            xaxis_title="Year",
            yaxis_title="Diabetes Prevalence (% of Population Ages 20 to 79)",
            title = "Diabetes Prevalence (% of Population Ages 20 to 79) Trend"
        )
        st.plotly_chart(fig_diab, use_container_width=True)
    with col18:
        fig_diab2 = go.Figure()
        fig_diab2.add_trace(
            go.Scatter(
                x=chart_data['Diabetes prevalence (% of population ages 20 to 79)'], 
                y=chart_data['migrants'],
                text = chart_data['Year'],
                mode='markers',
                hovertemplate=(
                    "<b>Year %{text}</b><br>"
                    "Diabetes Prevalence (% of population ages 20 to 79): <span style='color:#00d4ff'><b>%{x:,.2f}%</b></span><br>"
                    "Migrant: <span style='color:#00d4ff'><b>%{y:,.0f}</b></span><br>"
                )
            )
        )
        fig_diab2.update_layout(
            xaxis_title="Diabetes Prevalence (% of Population Ages 20 to 79)",
            yaxis_title="Migrants",
            title = "Diabetes Prevalence (% of Population Ages 20 to 79) vs Migrants"
        )
        st.plotly_chart(fig_diab2, use_container_width=True)
    
    #Hypertension
    st.subheader("🫀 Hypertension Prevalence (% of population ages 30 to 79)")
    
    col19, col20 = st.columns(2)

    with col19:
        fig_hype = go.Figure()
        fig_hype.add_trace(
            go.Scatter(
                x=chart_data['Year'], 
                y=chart_data['Prevalence of hypertension (% of adults ages 30-79)'],
                mode='lines+markers',
                hovertemplate=(
                    "<b>Year %{x}</b><br>"
                    "Hypertension Prevalence (% of population ages 30 to 79): <span style='color:#00d4ff'><b>%{y:,.2f}%</b></span><br>"
                )
            )
        )
        fig_hype.update_layout(
            xaxis_title="Years",
            yaxis_title="Hypertension Prevalence (% of Population Ages 30 to 79)",
            title = "Hypertension Prevalence (% of Population Ages 30 to 79) Trend"
        )
        st.plotly_chart(fig_hype, use_container_width=True)
    with col20:
        fig_hype2 = go.Figure()
        fig_hype2.add_trace(
            go.Scatter(
                x=chart_data['Prevalence of hypertension (% of adults ages 30-79)'], 
                y=chart_data['migrants'],
                text = chart_data['Year'],
                mode='markers',
                hovertemplate=(
                    "<b>Year %{text}</b><br>"
                    "Hypertension Prevalence (% of population ages 30 to 79): <span style='color:#00d4ff'><b>%{x:,.2f}%</b></span><br>"
                    "Migrant: <span style='color:#00d4ff'><b>%{y:,.0f}</b></span><br>"
                )
            )
        )
        fig_hype2.update_layout(
            xaxis_title="Hypertension Prevalence (% of Population Ages 30 to 79)",
            yaxis_title="Migrants",
            title = "Hypertension Prevalence (% of Population Ages 30 to 79) vs Migrants"
        )
        st.plotly_chart(fig_hype2, use_container_width=True)

    #Mortality Rate (Female)
    st.subheader("♀️ Mortality Rate (Female)")
    
    col21, col22 = st.columns(2)

    with col21:
        fig_mrf = go.Figure()
        fig_mrf.add_trace(
            go.Scatter(
                x=chart_data['Year'], 
                y=chart_data['Mortality rate, adult, female (per 1,000 female adults)'],
                mode='lines+markers',
                hovertemplate=(
                    "<b>Year %{x}</b><br>"
                    "Mortality Rate (per 1,000 female adults): <span style='color:#00d4ff'><b>%{y:,.2f}</b></span><br>"
                )
            )
        )
        fig_mrf.update_layout(
            xaxis_title="Years",
            yaxis_title="Mortality Rate (per 1,000 Female Adults)",
            title = "Mortality Rate (per 1,000 Female Adults) Trend"
        )
        st.plotly_chart(fig_mrf, use_container_width=True)
    with col22:
        fig_mrf2 = go.Figure()
        fig_mrf2.add_trace(
            go.Scatter(
                x=chart_data['Mortality rate, adult, female (per 1,000 female adults)'], 
                y=chart_data['migrants'],
                text = chart_data['Year'],
                mode='markers',
                hovertemplate=(
                    "<b>Year %{text}</b><br>"
                    "Mortality Rate (per 1,000 female adults): <span style='color:#00d4ff'><b>%{x:,.2f}</b></span><br>"
                    "Migrant: <span style='color:#00d4ff'><b>%{y:,.0f}</b></span><br>"
                )
            )
        )
        fig_mrf2.update_layout(
            xaxis_title="Mortality Rate (per 1,000 Female Adults)",
            yaxis_title="Migrants",
            title = "Mortality Rate (per 1,000 Female Adults) vs Migrants"
        )
        st.plotly_chart(fig_mrf2, use_container_width=True)

    #Mortality Rate (Male)
    st.subheader("♂️ Mortality Rate (Male)")
    
    col23, col24 = st.columns(2)

    with col23:
        fig_mrm = go.Figure()
        fig_mrm.add_trace(
            go.Scatter(
                x=chart_data['Year'], 
                y=chart_data['Mortality rate, adult, male (per 1,000 male adults)'],
                mode='lines+markers',
                hovertemplate=(
                    "<b>Year %{x}</b><br>"
                    "Mortality Rate (per 1,000 female adults): <span style='color:#00d4ff'><b>%{y:,.2f}</b></span><br>"
                )
            )
        )
        fig_mrm.update_layout(
            xaxis_title="Year",
            yaxis_title="Mortality Rate (per 1,000 Male Adults)",
            title = "Mortality Rate (per 1,000 Male Adults) Trend"
        )
        st.plotly_chart(fig_mrm, use_container_width=True)
    with col24:
        fig_mrm2 = go.Figure()
        fig_mrm2.add_trace(
            go.Scatter(
                x=chart_data['Mortality rate, adult, male (per 1,000 male adults)'], 
                y=chart_data['migrants'],
                text = chart_data['Year'],
                mode='markers',
                hovertemplate=(
                    "<b>Year %{text}</b><br>"
                    "Mortality Rate (per 1,000 male adults): <span style='color:#00d4ff'><b>%{x:,.2f}</b></span><br>"
                    "Migrant: <span style='color:#00d4ff'><b>%{y:,.0f}</b></span><br>"
                )
            )
        )
        fig_mrm2.update_layout(
            xaxis_title="Mortality Rate (per 1,000 Male Adults)",
            yaxis_title="Migrants",
            title = "Mortality Rate (per 1,000 Male Adults) vs Migrants"
        )
        st.plotly_chart(fig_mrm2, use_container_width=True)
    
    # Show sample of the full dataset
    st.markdown("---")
    st.subheader("Full Dataset Sample")
    st.dataframe(df.head(10), use_container_width=True)

     

    

else:
    st.warning("No data loaded. Please check if the CSV file exists.")
    