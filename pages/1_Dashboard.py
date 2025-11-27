import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Set page config
st.set_page_config(
    page_title="Filipino Migrant Analytics 2000-2025",
    page_icon="🇵🇭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Dark mode custom CSS


class DataLoader:
    """Class to handle data loading and caching"""
    
    @staticmethod
    @st.cache_data
    def load_all_data():
        """Load all datasets with error handling"""
        try:
            educ_pivot = pd.read_csv('./data/educ_pivot.csv')
            age_pivot = pd.read_csv('./data/age_pivot.csv')
            occu_pivot = pd.read_csv('./data/occu_pivot.csv')
            countries_pivot = pd.read_csv('./data/countries_pivot.csv')
            sex_pivot = pd.read_csv('./data/sex_pivot.csv')
            civ_pivot = pd.read_csv('./data/civ_pivot.csv')
            origin_regions_pivot = pd.read_csv('./data/regions_pivot.csv')
            
            return {
                'education': educ_pivot,
                'age': age_pivot,
                'occupation': occu_pivot,
                'countries': countries_pivot,
                'gender': sex_pivot,
                'civil_status': civ_pivot,
                'origin_regions': origin_regions_pivot
            }
        except Exception as e:
            st.error(f"Error loading data: {e}")
            st.stop()
            return None

class DataProcessor:
    """Class to process and transform data"""
    
    def __init__(self, data_dict):
        self.data = data_dict
        
        # Mappings
        self.country_mapping = {
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
        
        self.region_mapping = {
            'region_i': 'Region I',
            'region_ii': 'Region II',
            'region_iii': 'Region III',
            'region_iv_a': 'Region IV-A',
            'region_iv_b': 'Region IV-B',
            'region_v': 'Region V',
            'region_vi': 'Region VI',
            'region_vii': 'Region VII',
            'region_viii': 'Region VIII',
            'region_ix': 'Region IX',
            'region_x': 'Region X',
            'region_xi': 'Region XI',
            'region_xii': 'Region XII',
            'region_xiii': 'Region XIII',
            'ncr': 'NCR',
            'car': 'CAR',
            'armm': 'ARMM'
        }
        
        self.occupation_mapping = {
            'Administrative Workers': 'administrative_workers',
            'Clerical Workers': 'clerical_workers',
            'Laborers & Operators': 'equipment_operators,_&_laborers',
            'Housewives': 'housewives',
            'Armed Forces': 'members_of_the_armed_forces',
            'Minors (Below 7)': 'minors_(below_7_years_old)',
            'No Occupation': 'no_occupation_reported',
            'Out of School Youth': 'out_of_school_youth',
            'Professionals & Technical': "prof'l,_tech'l,_&_related_workers",
            'Refugees': 'refugees',
            'Retirees': 'retirees',
            'Sales Workers': 'sales_workers',
            'Service Workers': 'service_workers',
            'Students': 'students',
            'Workers & Fishermen': 'workers_&_fishermen'
        }
        
        self.education_mapping = {
            'College Graduate': 'college_graduate',
            'High School': 'high_school_graduate',
            'Post Graduate': 'post_graduate',
            'Vocational': 'vocational_graduate',
            'Elementary': 'elementary_graduate',
        }
        
        self.all_age_options = ['15 - 19', '20 - 24', '25 - 29', '30 - 34', '35 - 39', 
                               '40 - 44', '45 - 49', '50 - 54', '55 - 59', '60 - 64']
        self.all_education_options = list(self.education_mapping.keys())
        self.all_occupation_options = list(self.occupation_mapping.keys())
    
    def get_year_data(self, pivot_df, year):
        """Get data for specific year"""
        result = pivot_df[pivot_df['year'] == year]
        return result.iloc[0] if not result.empty else None
    
    def get_country_columns(self):
        """Get list of country columns"""
        return [col for col in self.data['countries'].columns if col != 'year']
    
    def get_region_columns(self):
        """Get list of region columns"""
        return [col for col in self.data['origin_regions'].columns if col != 'year']
    
    def calculate_filtered_total(self, year_data, filter_categories, category_mapping, filter_list):
        """Calculate total for filtered categories"""
        if not filter_list:  # If no filter, return sum of all categories
            total = 0
            for category in filter_categories:
                col_name = category_mapping.get(category, category)
                if col_name in year_data:
                    total += year_data[col_name]
            return total
        
        # If filter applied, only sum selected categories
        total = 0
        for category in filter_list:
            col_name = category_mapping.get(category, category)
            if col_name in year_data:
                total += year_data[col_name]
        return total

class FilterManager:
    """Class to manage filter state and logic"""
    
    def __init__(self, processor):
        self.processor = processor
        self.initialize_filters()
    
    def initialize_filters(self):
        """Initialize filter state"""
        if 'filters_initialized' not in st.session_state:
            st.session_state.education_filter = []
            st.session_state.age_filter = []
            st.session_state.occupation_filter = []
            st.session_state.map_colorscale = "Viridis"
            st.session_state.top_n_countries = 10
            st.session_state.chart_height = 350
            st.session_state.filters_initialized = True
    
    def get_filters(self):
        """Get current filter values"""
        return {
            'education': st.session_state.education_filter,
            'age': st.session_state.age_filter,
            'occupation': st.session_state.occupation_filter,
            'map_colorscale': st.session_state.map_colorscale,
            'top_n_countries': st.session_state.top_n_countries,
            'chart_height': st.session_state.chart_height
        }
    
    def reset_filters(self):
        """Reset all filters to default"""
        st.session_state.education_filter = []
        st.session_state.age_filter = []
        st.session_state.occupation_filter = []
        st.session_state.map_colorscale = "Viridis"
        st.session_state.top_n_countries = 10
        st.session_state.chart_height = 350
        st.rerun()
    
    def render_sidebar_controls(self):
        """Render sidebar filter controls"""
        st.sidebar.markdown("""
            <div style='text-align: center; padding: 1.5rem 0.5rem; background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); border-radius: 12px; margin-bottom: 1.5rem;'>
                <h2 style='color: white; margin: 0; font-size: 1.5rem; text-shadow: 0 2px 4px rgba(0,0,0,0.3);'>🎛️ CONTROL PANEL</h2>
                <p style='color: #dbeafe; margin: 0.5rem 0 0 0; font-size: 0.85rem;'>Customize your analysis</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Year Selection
        st.sidebar.markdown("""
            <div style='background: rgba(59, 130, 246, 0.1); border: 1px solid #3b82f6; border-radius: 8px; padding: 0.8rem; margin-bottom: 1rem;'>
                <p style='color: #60a5fa; margin: 0; font-weight: 600; font-size: 0.9rem;'>📅 TIME PERIOD</p>
            </div>
        """, unsafe_allow_html=True)
        
        years = sorted(self.processor.data['education']['year'].unique())
        selected_year = st.sidebar.selectbox(
            "Select Year", 
            years, 
            index=len(years)-1
        )
        
        show_comparison = st.sidebar.checkbox("📊 Enable Year Comparison", value=False)
        comparison_year = None
        if show_comparison:
            comparison_year = st.sidebar.selectbox("Compare with", [y for y in years if y != selected_year])
        
        # Data Filters
        st.sidebar.markdown("""
            <div style='background: rgba(59, 130, 246, 0.1); border: 1px solid #3b82f6; border-radius: 8px; padding: 0.8rem; margin: 1rem 0;'>
                <p style='color: #60a5fa; margin: 0; font-weight: 600; font-size: 0.9rem;'>🔍 DATA FILTERS</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Education filter
        education_filter = st.sidebar.multiselect(
            "🎓 Education Levels",
            self.processor.all_education_options,
            default=st.session_state.education_filter,
            help="Filter by education level. Leave empty to include all education levels.",
            placeholder="All education levels"
        )
        
        # Age group filter
        age_filter = st.sidebar.multiselect(
            "👥 Age Groups",
            self.processor.all_age_options,
            default=st.session_state.age_filter,
            help="Filter by age groups. Leave empty to include all age groups.",
            placeholder="All age groups"
        )
        
        # Occupation filter
        occupation_filter = st.sidebar.multiselect(
            "💼 Occupations",
            self.processor.all_occupation_options,
            default=st.session_state.occupation_filter,
            help="Filter by occupation type. Leave empty to include all occupations.",
            placeholder="All occupations"
        )
        
        # Update session state
        # Update session state when button is clicked
        if st.sidebar.button("Apply Filters", use_container_width=True, help="Apply selected filters to dashboard"):
            st.session_state.education_filter = education_filter
            st.session_state.age_filter = age_filter
            st.session_state.occupation_filter = occupation_filter
            st.rerun()
        
        # Visualization Options
        st.sidebar.markdown("""
            <div style='background: rgba(59, 130, 246, 0.1); border: 1px solid #3b82f6; border-radius: 8px; padding: 0.8rem; margin: 1rem 0;'>
                <p style='color: #60a5fa; margin: 0; font-weight: 600; font-size: 0.9rem;'>🎨 VISUALIZATION</p>
            </div>
        """, unsafe_allow_html=True)
        
        map_colorscale = st.sidebar.selectbox(
            "🗺️ Map Color Scheme", 
            ["Viridis", "Plasma", "Turbo", "Blues", "Reds", "Greens", "YlOrRd", "RdYlBu"], 
            index=["Viridis", "Plasma", "Turbo", "Blues", "Reds", "Greens", "YlOrRd", "RdYlBu"].index(st.session_state.map_colorscale)
        )
        
        top_n_countries = st.sidebar.slider(
            "🏆 Top Destinations", 
            min_value=5, max_value=20, value=st.session_state.top_n_countries
        )
        
        chart_height = st.sidebar.slider(
            "📏 Chart Height (px)", 
            min_value=300, max_value=600, value=st.session_state.chart_height, step=50
        )
        
        # Update session state
        st.session_state.map_colorscale = map_colorscale
        st.session_state.top_n_countries = top_n_countries
        st.session_state.chart_height = chart_height
        
        # Action Buttons
        st.sidebar.markdown("<div style='margin-top: 1.5rem;'>", unsafe_allow_html=True)
        col_btn1, col_btn2 = st.sidebar.columns(2)
        with col_btn1:
            if st.button("🔄 Refresh", use_container_width=True, help="Reload dashboard with current settings"):
                st.rerun()
        with col_btn2:
            if st.button("♻️ Reset Filters", use_container_width=True, help="Reset all filters to default values"):
                self.reset_filters()
        st.sidebar.markdown("</div>", unsafe_allow_html=True)
        
        return selected_year, show_comparison, comparison_year

class VisualizationEngine:
    """Class to handle all visualizations"""
    
    def __init__(self):
        self.dark_template = {
            'paper_bgcolor': 'rgba(0,0,0,0)',
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'font': {'color': '#e4e6eb'},
            'xaxis': {'gridcolor': '#1e3a8a', 'color': '#94a3b8'},
            'yaxis': {'gridcolor': '#1e3a8a', 'color': '#94a3b8'},
        }
    
    def create_world_map(self, map_df, selected_year, total_migrants, colorscale="Viridis"):
        """Create world map visualization"""
        fig_map = px.choropleth(
            map_df,
            locations='country',
            locationmode='country names',
            color='migrants',
            hover_name='country',
            hover_data={'country': False},
            custom_data=['migrants', 'percentage'],
            color_continuous_scale=colorscale,
            height=600,
            labels={'migrants': 'Number of Migrants'}
        )

        # Enhanced hover with simple HTML (markdown-like styling)
        fig_map.update_traces(
            hovertemplate=(
            "<b style='font-size:14px;'>%{hovertext}</b><br><br>"
            "<span style='color:#94a3b8;'>Total Migrants:</span> <span style='color:#00d4ff;font-weight:bold;'>%{customdata[0]:,.0f}</span><br>"
            "<span style='color:#94a3b8;'>Share of Total:</span> <span style='color:#4ade80;font-weight:bold;'>%{customdata[1]:.2f}%</span><br>"
            "<span style='color:#94a3b8;'>Year:</span> <span style='color:#fbbf24;font-weight:bold;'>" + str(selected_year) + "</span><br>"
            "<extra></extra>"
            )
        )
        fig_map.update_geos(
            showcoastlines=True,
            coastlinecolor='#334155',
            showland=True,
            landcolor='#1e293b',
            showcountries=True,
            countrycolor='#334155',
            bgcolor='rgba(0,0,0,0)',
            showframe=False,
            projection_type='natural earth'
        )
        
        fig_map.update_layout(
            **self.dark_template,
            margin=dict(l=0, r=0, t=0, b=0),
            coloraxis_colorbar=dict(
                title=dict(text="Migrants", font=dict(color='#e4e6eb')),
                tickfont=dict(color='#e4e6eb')
            )
        )
        
        return fig_map
    
    def create_trend_chart(self, trend_df, height=400):
        """Create migration trend chart"""
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=trend_df['Year'],
            y=trend_df['Total'],
            mode='lines+markers',
            fill='tozeroy',
            line=dict(color='#00d4ff', width=3),
            marker=dict(size=6, color='#00d4ff'),
            fillcolor='rgba(0, 212, 255, 0.1)',
            name='Total OFWs'
        ))

        fig_trend.update_layout(
            **self.dark_template,
            height=height,
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis_title='Year',
            yaxis_title='Number of Migrants',
            hovermode='x unified',
            showlegend=False
        )
        
        return fig_trend
    
    def create_bar_chart(self, data_df, x, y, title, color_col=None, orientation='v', color_scale='Viridis', height=400):
        """Create a bar chart with dark theme"""
        if orientation == 'h':
            fig = px.bar(
                data_df,
                x=x,
                y=y,
                orientation='h',
                title=f'<b>{title}</b>',
                color=color_col,
                color_continuous_scale=color_scale
            )
        else:
            fig = px.bar(
                data_df,
                x=x,
                y=y,
                title=f'<b>{title}</b>',
                color=color_col,
                color_continuous_scale=color_scale
            )
        
        fig.update_layout(
            **self.dark_template,
            height=height,
            showlegend=False
        )
        
        return fig
    
    def create_stacked_bar_chart(self, data_df, x, y, color, title, height=400):
        """Create a stacked bar chart"""
        fig = px.bar(
            data_df,
            x=x,
            y=y,
            color=color,
            title=f'<b>{title}</b>',
            barmode='stack'
        )
        
        fig.update_layout(
            **self.dark_template,
            height=height
        )
        
        return fig
    
    def create_heatmap(self, data_df, x, y, z, title, height=500):
        """Create a heatmap"""
        fig = px.density_heatmap(
            data_df,
            x=x,
            y=y,
            z=z,
            title=f'<b>{title}</b>',
            color_continuous_scale='Viridis'
        )
        
        fig.update_layout(
            **self.dark_template,
            height=height
        )
        
        return fig

class Dashboard:
    """Main dashboard class"""
    
    def __init__(self):
        self.data_loader = DataLoader()
        self.data = self.data_loader.load_all_data()
        self.processor = DataProcessor(self.data)
        self.filter_manager = FilterManager(self.processor)
        self.viz = VisualizationEngine()
    
    def calculate_filtered_data(self, selected_year, filters):
        """Calculate all filtered data based on current filters"""
        # Get year data
        year_countries = self.processor.get_year_data(self.data['countries'], selected_year)
        year_regions = self.processor.get_year_data(self.data['origin_regions'], selected_year)
        year_educ = self.processor.get_year_data(self.data['education'], selected_year)
        year_gender = self.processor.get_year_data(self.data['gender'], selected_year)
        year_age = self.processor.get_year_data(self.data['age'], selected_year)
        year_occu = self.processor.get_year_data(self.data['occupation'], selected_year)
        year_civ = self.processor.get_year_data(self.data['civil_status'], selected_year)
        
        # Calculate filtered totals
        filtered_education_total = self.processor.calculate_filtered_total(
            year_educ, self.processor.all_education_options, self.processor.education_mapping, filters['education']
        ) if year_educ is not None else 0
        
        filtered_age_total = self.processor.calculate_filtered_total(
            year_age, self.processor.all_age_options, {}, filters['age']
        ) if year_age is not None else 0
        
        filtered_occupation_total = self.processor.calculate_filtered_total(
            year_occu, self.processor.all_occupation_options, self.processor.occupation_mapping, filters['occupation']
        ) if year_occu is not None else 0
        
        # Calculate overall filtered total
        if filters['education'] or filters['age'] or filters['occupation']:
            filtered_totals = []
            if filters['education']:
                filtered_totals.append(filtered_education_total)
            if filters['age']:
                filtered_totals.append(filtered_age_total)
            if filters['occupation']:
                filtered_totals.append(filtered_occupation_total)
            
            if filtered_totals:
                total_migrants = min(filtered_totals)
            else:
                total_migrants = year_countries[self.processor.get_country_columns()].sum() if year_countries is not None else 0
        else:
            total_migrants = year_countries[self.processor.get_country_columns()].sum() if year_countries is not None else 0
        
        return {
            'year_data': {
                'countries': year_countries,
                'regions': year_regions,
                'education': year_educ,
                'gender': year_gender,
                'age': year_age,
                'occupation': year_occu,
                'civil_status': year_civ
            },
            'totals': {
                'migrants': total_migrants,
                'education': filtered_education_total,
                'age': filtered_age_total,
                'occupation': filtered_occupation_total
            }
        }
    
    def render_metrics(self, filtered_data, selected_year, show_comparison, comparison_year):
        """Render key metrics row"""
        totals = filtered_data['totals']
        year_data = filtered_data['year_data']
        
        # Calculate percentages
        male_count = year_data['gender'].get('male', 0) if year_data['gender'] is not None else 0
        female_count = year_data['gender'].get('female', 0) if year_data['gender'] is not None else 0
        college_count = year_data['education'].get('college_graduate', 0) if year_data['education'] is not None else 0
        married_count = year_data['civil_status'].get('married', 0) if year_data['civil_status'] is not None else 0
        
        # Apply filter ratio
        if any([st.session_state.education_filter, st.session_state.age_filter, st.session_state.occupation_filter]):
            original_total = year_data['countries'][self.processor.get_country_columns()].sum() if year_data['countries'] is not None else 1
            if original_total > 0:
                filter_ratio = totals['migrants'] / original_total
                male_count = int(male_count * filter_ratio)
                female_count = int(female_count * filter_ratio)
                college_count = int(college_count * filter_ratio)
                married_count = int(married_count * filter_ratio)
        
        # Calculate percentages
        male_pct = (male_count / totals['migrants'] * 100) if totals['migrants'] > 0 else 0
        female_pct = (female_count / totals['migrants'] * 100) if totals['migrants'] > 0 else 0
        college_pct = (college_count / totals['migrants'] * 100) if totals['migrants'] > 0 else 0
        married_pct = (married_count / totals['migrants'] * 100) if totals['migrants'] > 0 else 0
        
        # Show filter status
        active_filters = []
        if st.session_state.education_filter:
            active_filters.append(f"Education: {len(st.session_state.education_filter)} cats")
        if st.session_state.age_filter:
            active_filters.append(f"Age: {len(st.session_state.age_filter)} groups")
        if st.session_state.occupation_filter:
            active_filters.append(f"Occupation: {len(st.session_state.occupation_filter)} types")
        
        if active_filters:
            st.markdown(f"""
                <div style='background: rgba(251, 191, 36, 0.1); border: 1px solid #fbbf24; border-radius: 8px; padding: 0.8rem; margin-bottom: 1rem;'>
                    <p style='margin: 0; color: #fbbf24; font-size: 0.9rem;'>
                        <strong>🔍 Active Filters:</strong> {' • '.join(active_filters)} 
                        <span style='color: #94a3b8;'>(Showing filtered data only)</span>
                    </p>
                </div>
            """, unsafe_allow_html=True)
        
        # Metrics
        # st.markdown("<div class='stats-row'>", unsafe_allow_html=True)
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            delta_total = None
            if show_comparison and comparison_year:
                comp_data = self.calculate_filtered_data(comparison_year, self.filter_manager.get_filters())
                comp_total = comp_data['totals']['migrants']
                delta_val = totals['migrants'] - comp_total
                delta_pct = (delta_val / comp_total * 100) if comp_total > 0 else 0
                delta_total = f"{delta_pct:+.1f}%"
            st.markdown(f"""
            <div style='text-align: center; padding: 1rem;'>
                <p style='color: #94a3b8; font-size: 0.9rem; margin: 0; text-transform: uppercase;'>Total OFWs</p>
                <p style='color: #00d4ff; font-size: 2rem; font-weight: 700; margin: 0.5rem 0;'>{totals['migrants']:,.0f}</p>
                {f"<p style='color: #4ade80; margin: 0;'>{delta_total}</p>" if delta_total else ""}
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style='text-align: center; padding: 1rem;'>
                <p style='color: #94a3b8; font-size: 0.9rem; margin: 0; text-transform: uppercase;'>Male %</p>
                <p style='color: #60a5fa; font-size: 2rem; font-weight: 700; margin: 0.5rem 0;'>{male_pct:.1f}%</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div style='text-align: center; padding: 1rem;'>
                <p style='color: #94a3b8; font-size: 0.9rem; margin: 0; text-transform: uppercase;'>Female %</p>
                <p style='color: #f472b6; font-size: 2rem; font-weight: 700; margin: 0.5rem 0;'>{female_pct:.1f}%</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div style='text-align: center; padding: 1rem;'>
                <p style='color: #94a3b8; font-size: 0.9rem; margin: 0; text-transform: uppercase;'>College Grad</p>
                <p style='color: #fbbf24; font-size: 2rem; font-weight: 700; margin: 0.5rem 0;'>{college_pct:.1f}%</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col5:
            st.markdown(f"""
            <div style='text-align: center; padding: 1rem;'>
                <p style='color: #94a3b8; font-size: 0.9rem; margin: 0; text-transform: uppercase;'>Married</p>
                <p style='color: #4ade80; font-size: 2rem; font-weight: 700; margin: 0.5rem 0;'>{married_pct:.1f}%</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col6:
            if year_data['countries'] is not None:
                top_dest = self.processor.country_mapping.get(
                    year_data['countries'][self.processor.get_country_columns()].idxmax(), 'N/A'
                )
            st.markdown(f"""
                <div style='text-align: center; padding: 1rem;'>
                <p style='color: #94a3b8; font-size: 0.9rem; margin: 0; text-transform: uppercase;'>Top Destination</p>
                <p style='color: #a78bfa; font-size: 1.5rem; font-weight: 700; margin: 0.5rem 0;'>{top_dest}</p>
                </div>
            """, unsafe_allow_html=True)
        
        
        return {
            'totals': totals,
            'percentages': {
                'male': male_pct,
                'female': female_pct,
                'college': college_pct,
                'married': married_pct
            },
            'top_destination': top_dest if year_data['countries'] is not None else 'N/A'
        }
    
    def render_global_overview(self, filtered_data, selected_year, filters):
        """Render global overview section"""
        st.markdown("## 🌍 Global Distribution")
        st.markdown(
            """
            <div style='background: rgba(96,165,250,0.08); border: 1px solid #1e3a8a; padding: 0.75rem 1rem; border-radius: 8px; font-size: 0.85rem; line-height: 1.4; margin-bottom: 1rem;'>
                This interactive map visualizes the global distribution of Filipino migrant workers across destination countries. 
                Darker colors indicate higher concentrations of OFWs. The data adjusts based on any active filters (education, age, occupation).
            </div>
            """,
            unsafe_allow_html=True
        )
        
        year_data = filtered_data['year_data']
        totals = filtered_data['totals']
        
        if year_data['countries'] is not None:
            map_data = []
            for country in self.processor.get_country_columns():
                migrants = year_data['countries'].get(country, 0)
                
                # Apply filter ratio to country data
                if any([st.session_state.education_filter, st.session_state.age_filter, st.session_state.occupation_filter]):
                    original_total = year_data['countries'][self.processor.get_country_columns()].sum()
                    if original_total > 0:
                        filter_ratio = totals['migrants'] / original_total
                        migrants = int(migrants * filter_ratio)
                
                if migrants > 0 and country in self.processor.country_mapping:
                    map_data.append({
                        'country': self.processor.country_mapping[country],
                        'migrants': migrants,
                        'percentage': (migrants / totals['migrants'] * 100) if totals['migrants'] > 0 else 0
                    })
            
            if map_data:
                map_df = pd.DataFrame(map_data)
                fig_map = self.viz.create_world_map(
                    map_df=map_df,
                    selected_year=selected_year,
                    total_migrants=totals['migrants'],
                    colorscale=filters['map_colorscale']
                )
                # Adding text labels on top of the choropleth
                fig_map.add_trace(go.Scattergeo(
                    locationmode='country names',
                    locations=map_df['country'],
                    text=map_df['migrants'].apply(lambda x: f"{x:,.0f}"),
                    mode='text',
                    textfont=dict(color='white', size=10),
                    showlegend=False
                ))
                st.plotly_chart(fig_map, use_container_width=True)
    
    def render_trends_and_destinations(self, filtered_data, selected_year, filters):
        """Render trends and destinations in two columns"""
        col_left, col_right = st.columns([3, 2])
        
        with col_left:
            # MIGRATION TRENDS
            st.markdown("## 📈 Migration Trends")
            st.markdown(
            """
            <div style='background: rgba(96,165,250,0.08); border: 1px solid #1e3a8a; padding: 0.75rem 1rem; border-radius: 8px; font-size: 0.85rem; line-height: 1.4; margin-bottom: 1rem;'>
                Track the total number of Filipino migrant workers over time. Tooltip shows year-on-year change. Marker color encodes year.
            </div>
            """,
            unsafe_allow_html=True
            )

            years = sorted(self.data['education']['year'].unique())
            trend_rows = []
            for year in years:
                year_filtered = self.calculate_filtered_data(year, filters)
                total = year_filtered['totals']['migrants']
                trend_rows.append({'Year': year, 'Total': total})
            if trend_rows:
                trend_df = pd.DataFrame(trend_rows)
                trend_df['Prev'] = trend_df['Total'].shift(1)
                trend_df['AbsChange'] = trend_df['Total'] - trend_df['Prev']
                trend_df['PctChange'] = (trend_df['AbsChange'] / trend_df['Prev'] * 100).round(2)

            # Build color list per year using selected colorscale
            import plotly.express as px
            scale_map = {
                "Viridis": px.colors.sequential.Viridis,
                "Plasma": px.colors.sequential.Plasma,
                "Turbo": px.colors.sequential.Turbo,
                "Blues": px.colors.sequential.Blues,
                "Reds": px.colors.sequential.Reds,
                "Greens": px.colors.sequential.Greens,
                "YlOrRd": px.colors.sequential.YlOrRd,
                "RdYlBu": px.colors.diverging.RdYlBu
            }
            base_scale = scale_map.get(filters['map_colorscale'], px.colors.sequential.Viridis)
            if len(years) == 1:
                marker_colors = [base_scale[0]]
            else:
                # Evenly sample scale
                marker_colors = [
                base_scale[int(i * (len(base_scale) - 1) / (len(years) - 1))]
                for i in range(len(years))
                ]

            # Custom data for hover
            customdata = trend_df[['Prev', 'AbsChange', 'PctChange']].to_numpy()

            fig_trend = go.Figure()
            fig_trend.add_trace(
                go.Scatter(
                x=trend_df['Year'],
                y=trend_df['Total'],
                mode='lines+markers',
                line=dict(color='#00d4ff', width=3),
                marker=dict(
                    size=11,
                    color=marker_colors,
                    line=dict(color="#ffffff", width=0.5)
                ),
                customdata=customdata,
                hovertemplate=(
                    "<b>Year %{x}</b><br>"
                    "Total OFWs: <span style='color:#00d4ff'><b>%{y:,.0f}</b></span><br>"
                    "%{customdata[0]:,.0f}<span style='color:#94a3b8'> prev total</span><br>"
                    "<span style='color:#94a3b8'>Change:</span> "
                    "<b>%{customdata[1]:+,.0f}</b> "
                    "(<b>%{customdata[2]:+,.2f}%</b>)<br>"
                    "<extra></extra>"
                )
                )
            )
            # Replace NaN hover for first year
            fig_trend.for_each_trace(
                lambda t: t.update(
                hovertemplate=t.hovertemplate.replace(
                    "nan prev total", "Baseline year"
                ).replace(
                    "Change: <b>+nan</b> (<b>+nan%</b>)",
                    "Change: <b>N/A</b>"
                )
                )
            )
            fig_trend.update_layout(
                **self.viz.dark_template,
                height=filters['chart_height'],
                margin=dict(l=20, r=20, t=30, b=20),
                xaxis_title='Year',
                yaxis_title='Number of Migrants',
                hovermode='x',
                showlegend=False
            )
            st.plotly_chart(fig_trend, use_container_width=True)
        
        with col_right:
            # TOP DESTINATIONS
            st.markdown("## 🏆 Top Destinations")
            
            st.markdown(
                f"""
                <div style='background: rgba(96,165,250,0.08); border: 1px solid #1e3a8a; padding: 0.75rem 1rem; border-radius: 8px; font-size: 0.85rem; line-height: 1.4; margin-bottom: 1rem;'>
                    Top {filters['top_n_countries']} destination countries ranked by number of OFWs. The count reflects filtered data if any demographic filters are active.
                </div>
                """,
                unsafe_allow_html=True
            )
            
            year_data = filtered_data['year_data']
            totals = filtered_data['totals']
            
            if year_data['countries'] is not None:
                country_data = []
                for country in self.processor.get_country_columns():
                    migrants = year_data['countries'].get(country, 0)
                    
                    # Apply filter ratio
                    if any([st.session_state.education_filter, st.session_state.age_filter, st.session_state.occupation_filter]):
                        original_total = year_data['countries'][self.processor.get_country_columns()].sum()
                        if original_total > 0:
                            filter_ratio = totals['migrants'] / original_total
                            migrants = int(migrants * filter_ratio)
                    
                    if migrants > 0:
                        country_name = self.processor.country_mapping.get(country, country.replace('_', ' ').title())
                        country_data.append({
                            'Country': country_name,
                            'Migrants': migrants,
                            'Percentage': (migrants / totals['migrants'] * 100) if totals['migrants'] > 0 else 0
                        })
                
                top_df = pd.DataFrame(country_data).nlargest(filters['top_n_countries'], 'Migrants').sort_values('Migrants', ascending=True)
                
                fig_top = px.bar(
                    top_df,
                    x='Migrants',
                    y='Country',
                    orientation='h',
                    title=f'<b>Top {filters["top_n_countries"]} Destinations</b>',
                    color='Migrants',
                    color_continuous_scale=filters['map_colorscale'],
                    text='Migrants'
                )
                fig_top.update_traces(
                    texttemplate='%{text:,.0f}',
                    textposition='outside',
                    marker=dict(
                        line=dict(color='#1e3a8a', width=1)
                    )
                )
                fig_top.update_layout(
                    **self.viz.dark_template,
                    height=filters['chart_height'],
                    showlegend=False
                )
                st.plotly_chart(fig_top, use_container_width=True)
    
    def render_demographics(self, filtered_data):
        """Render demographic overview"""
        st.markdown("## 👥 Demographics Overview")
        
        st.markdown(
                    """
                    <div style='background: rgba(96,165,250,0.08); border: 1px solid #1e3a8a; padding: 0.75rem 1rem; border-radius: 8px; font-size: 0.85rem; line-height: 1.4; margin-bottom: 1rem;'>
                        Explore the demographic characteristics of Filipino migrant workers. Use the filters in the sidebar to focus on specific education levels, age groups, or occupations.
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        
        year_data = filtered_data['year_data']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # EDUCATION
            st.markdown("### 🎓 Education Levels")
            
            if year_data['education'] is not None:
                educ_data = []
                for name, key in self.processor.education_mapping.items():
                    if st.session_state.education_filter and name not in st.session_state.education_filter:
                        continue
                    if key in year_data['education']:
                        count = year_data['education'][key]
                        if count > 0:
                            educ_data.append({'Category': name, 'Count': count})
                
                if educ_data:
                    educ_df = pd.DataFrame(educ_data).sort_values('Count', ascending=False)
                    color_map = {
                        'College Graduate': '#00d4ff',
                        'High School': '#4ade80',
                        'Post Graduate': '#fbbf24',
                        'Vocational': '#a78bfa',
                        'Elementary': '#f472b6'
                    }
                    fig_educ = px.bar(
                        educ_df,
                        x='Category',
                        y='Count',
                        title='<b>Education Distribution</b>',
                        color='Category',
                        color_discrete_map=color_map
                    )
                    fig_educ.update_layout(
                        **self.viz.dark_template,
                        height=320,
                        showlegend=False
                    )
                    st.plotly_chart(fig_educ, use_container_width=True)
        with col2:
            # AGE DISTRIBUTION
            st.markdown("### 📊 Age Distribution")
            
            if year_data['age'] is not None:
                age_data = []
                for age_group in self.processor.all_age_options:
                    if st.session_state.age_filter and age_group not in st.session_state.age_filter:
                        continue
                    if age_group in year_data['age']:
                        count = year_data['age'][age_group]
                        if count > 0:
                            age_data.append({'Age': age_group, 'Count': count})
                
                if age_data:
                    age_df = pd.DataFrame(age_data)
                    # Create color map for age groups
                    color_map = {
                        '15 - 19': '#a78bfa',
                        '20 - 24': '#00d4ff',
                        '25 - 29': '#4ade80',
                        '30 - 34': '#fbbf24',
                        '35 - 39': '#f472b6',
                        '40 - 44': '#fb923c',
                        '45 - 49': '#60a5fa',
                        '50 - 54': '#34d399',
                        '55 - 59': '#fde047',
                        '60 - 64': '#c084fc'
                    }
                    fig_age = px.bar(
                        age_df,
                        x='Age',
                        y='Count',
                        title='<b>Age Distribution</b>',
                        color='Age',
                        color_discrete_map=color_map
                    )
                    fig_age.update_layout(
                        **self.viz.dark_template,
                        height=320,
                        showlegend=False
                    )
                    st.plotly_chart(fig_age, use_container_width=True)
        
        with col3:
            # OCCUPATION
            st.markdown("### 💼 Occupations")
            
            if year_data['occupation'] is not None:
                occu_data = []
                for display_name, column_name in self.processor.occupation_mapping.items():
                    if st.session_state.occupation_filter and display_name not in st.session_state.occupation_filter:
                        continue
                    if column_name in year_data['occupation']:
                        count = year_data['occupation'][column_name]
                        if count > 0:
                            occu_data.append({'Occupation': display_name, 'Count': count})
                
                if occu_data:
                    occu_df = pd.DataFrame(occu_data)
                    color_map = {
                        'Administrative Workers': '#00d4ff',
                        'Clerical Workers': '#4ade80',
                        'Laborers & Operators': '#fbbf24',
                        'Housewives': '#f472b6',
                        'Armed Forces': '#a78bfa',
                        'Minors (Below 7)': '#fb923c',
                        'No Occupation': '#60a5fa',
                        'Out of School Youth': '#34d399',
                        'Professionals & Technical': '#fde047',
                        'Refugees': '#c084fc',
                        'Retirees': '#e879f9',
                        'Sales Workers': '#22d3ee',
                        'Service Workers': '#a3e635',
                        'Students': '#fca5a5',
                        'Workers & Fishermen': '#86efac'
                    }
                    fig_occu = px.bar(
                        occu_df,
                        x='Occupation',
                        y='Count',
                        title='<b>Occupation Distribution</b>',
                        color='Occupation',
                        color_discrete_map=color_map
                    )
                    fig_occu.update_layout(
                        **self.viz.dark_template,
                        height=320,
                        showlegend=False
                    )
                    st.plotly_chart(fig_occu, use_container_width=True)
    
    def render_additional_charts(self, filtered_data, selected_year):
        """Render additional charts and visualizations"""
        st.markdown("## 📊 Additional Insights")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # REGIONAL DISTRIBUTION
            st.markdown("### 🗺️ Origin Regions")
            
            st.markdown(
                """
                <div style='background: rgba(96,165,250,0.08); border: 1px solid #1e3a8a; padding: 0.75rem 1rem; border-radius: 8px; font-size: 0.85rem; line-height: 1.4;'>
                    This chart shows the distribution of Overseas Filipino Workers by their Philippine region of origin for the selected year.
                    Apply filters (education, age, occupation) to see how the regional proportions adjust relative to the filtered total.
                </div>
                """,
                unsafe_allow_html=True
            )
            
            year_data = filtered_data['year_data']
            totals = filtered_data['totals']
            
            if year_data['regions'] is not None:
                region_data = []
                for region in self.processor.get_region_columns():
                    migrants = year_data['regions'].get(region, 0)
                    
                    # Apply filter ratio
                    if any([st.session_state.education_filter, st.session_state.age_filter, st.session_state.occupation_filter]):
                        original_total = year_data['countries'][self.processor.get_country_columns()].sum() if year_data['countries'] is not None else 1
                        if original_total > 0:
                            filter_ratio = totals['migrants'] / original_total
                            migrants = int(migrants * filter_ratio)
                    
                    if migrants > 0:
                        region_data.append({
                            'Region': self.processor.region_mapping.get(region, region),
                            'Migrants': migrants
                        })
                
                if region_data:
                    region_df = pd.DataFrame(region_data)
                    
                    # Create a choropleth map of the Philippines regions
                    # Map region codes to proper names for geojson matching
                    region_geojson_mapping = {
                        'NCR': 'National Capital Region',
                        'CAR': 'Cordillera Administrative Region',
                        'Region I': 'Ilocos Region',
                        'Region II': 'Cagayan Valley',
                        'Region III': 'Central Luzon',
                        'Region IV-A': 'CALABARZON',
                        'Region IV-B': 'MIMAROPA',
                        'Region V': 'Bicol Region',
                        'Region VI': 'Western Visayas',
                        'Region VII': 'Central Visayas',
                        'Region VIII': 'Eastern Visayas',
                        'Region IX': 'Zamboanga Peninsula',
                        'Region X': 'Northern Mindanao',
                        'Region XI': 'Davao Region',
                        'Region XII': 'SOCCSKSARGEN',
                        'Region XIII': 'Caraga',
                        'ARMM': 'Bangsamoro Autonomous Region in Muslim Mindanao'
                    }
                    
                    region_df['region_name'] = region_df['Region'].map(region_geojson_mapping)
                    
                    # Create Philippines map using scatter geo (simple approach)
                    # Note: For a full choropleth, you'd need Philippines GeoJSON
                    fig_regions = px.choropleth(
                        region_df,
                        locations='Region',
                        locationmode='geojson-id',
                        color='Migrants',
                        hover_name='Region',
                        hover_data={'Region': False, 'Migrants': ':,.0f'},
                        color_continuous_scale='Viridis',
                        title='<b>Regional Distribution Map</b>',
                        labels={'Migrants': 'Number of OFWs'}
                    )
                    
                    # Fallback to bar chart if map doesn't render properly
                    # Since we may not have the geojson file, use horizontal bar as backup
                    region_df_sorted = region_df.sort_values('Migrants', ascending=True)
                    
                    fig_regions = px.bar(
                        region_df_sorted,
                        x='Migrants',
                        y='Region',
                        orientation='h',
                        title='<b>Regional Distribution</b>',
                        color='Migrants',
                        color_continuous_scale='Viridis'
                    )
                    
                    fig_regions.update_layout(
                        **self.viz.dark_template,
                        height=400,
                        showlegend=False
                    )
                    st.plotly_chart(fig_regions, use_container_width=True)
        
        with col2:
            # CIVIL STATUS
            st.markdown("### 👩‍❤️‍👨 Civil Status")

            st.markdown(
                """
                <div style='background: rgba(96,165,250,0.08); border: 1px solid #1e3a8a; padding: 0.75rem 1rem; border-radius: 8px; font-size: 0.85rem; line-height: 1.4;'>
                    This chart displays the marital status breakdown of OFWs for the selected year.
                    Filters applied will proportionally adjust the counts shown here.
                </div>
                """,
                unsafe_allow_html=True
            )
            
            if year_data['civil_status'] is not None:
                civil_status = {
                    'Single': 'single',
                    'Married': 'married',
                    'Widowed': 'widower',
                    'Separated': 'separated',
                    'Divorced': 'divorced'
                }
                
                civ_data = []
                for name, key in civil_status.items():
                    if key in year_data['civil_status']:
                        count = year_data['civil_status'][key]
                        
                        # Apply filter ratio
                        if any([st.session_state.education_filter, st.session_state.age_filter, st.session_state.occupation_filter]):
                            original_total = year_data['countries'][self.processor.get_country_columns()].sum() if year_data['countries'] is not None else 1
                            if original_total > 0:
                                filter_ratio = totals['migrants'] / original_total
                                count = int(count * filter_ratio)
                        
                        if count > 0:
                            civ_data.append({'Status': name, 'Count': count})
                
                if civ_data:
                    civ_df = pd.DataFrame(civ_data)
                    
                    # Create bar chart with custom colors per status
                    color_map = {
                        'Single': '#00d4ff',
                        'Married': '#4ade80',
                        'Widowed': '#fbbf24',
                        'Separated': '#f472b6',
                        'Divorced': '#a78bfa'
                    }
                    
                    fig_civ = px.bar(
                        civ_df,
                        x='Status',
                        y='Count',
                        title='<b>Civil Status Distribution</b>',
                        color='Status',
                        color_discrete_map=color_map
                    )
                    
                    fig_civ.update_layout(
                        **self.viz.dark_template,
                        height=400,
                        showlegend=False
                    )
                    
                    st.plotly_chart(fig_civ, use_container_width=True)
    
    def run(self):
        """Main method to run the dashboard"""
        # Header
        st.markdown("<h1>🇵🇭 FILIPINO MIGRANT ANALYTICS</h1>", unsafe_allow_html=True)
        st.markdown("<p class='subtitle'>Comprehensive Analysis of Overseas Filipino Workers • 2000-2025</p>", unsafe_allow_html=True)
        
        # Sidebar controls
        selected_year, show_comparison, comparison_year = self.filter_manager.render_sidebar_controls()
        filters = self.filter_manager.get_filters()
        
        # st.markdown("---")
        
        # Calculate filtered data
        filtered_data = self.calculate_filtered_data(selected_year, filters)
        
        # Render metrics
        metrics_data = self.render_metrics(filtered_data, selected_year, show_comparison, comparison_year)
        
        # Narrative insight
        filter_text = f" (filtered)" if any([st.session_state.education_filter, st.session_state.age_filter, st.session_state.occupation_filter]) else ""
        
        st.markdown(f"""
            <div style='background: rgba(0, 212, 255, 0.05); border-left: 4px solid #00d4ff; padding: 1.5rem; margin: 1.5rem 0; border-radius: 8px;'>
                <p style='margin: 0; color: #e4e6eb; line-height: 1.6;'>
                    <strong style='color: #00d4ff; font-size: 1.1rem;'>📊 Key Insights for {selected_year}{filter_text}:</strong><br/>
                    {'Based on the selected filters, there are' if filter_text else f'In {selected_year}, the Philippines had'} 
                    <strong style='color: #00d4ff;'>{filtered_data['totals']['migrants']:,.0f}</strong> overseas workers{' matching the criteria' if filter_text else ''}. 
                    The gender distribution shows <strong>{metrics_data['percentages']['female']:.1f}% female</strong> and <strong>{metrics_data['percentages']['male']:.1f}% male</strong> workers.
                    About <strong style='color: #00d4ff;'>{metrics_data['percentages']['college']:.1f}%</strong> {'of these OFWs are' if filter_text else 'of OFWs are'} college graduates.
                    The top destination remains <strong>{metrics_data['top_destination']}</strong>.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # Render all visualizations
        self.render_global_overview(filtered_data, selected_year, filters)
        self.render_trends_and_destinations(filtered_data, selected_year, filters)
        self.render_demographics(filtered_data)
        self.render_additional_charts(filtered_data, selected_year)
        
        # Footer
        # st.markdown("---")
        st.markdown("""
            <div style='text-align: center; padding: 2rem 0; color: #64748b;'>
                <div style='font-size: 0.9rem;'>
                    <strong style='color: #00d4ff;'>Filipino Migrant Analytics Dashboard</strong> • 
                    Tracking OFW Trends 2000-2025
                </div>
                <div style='font-size: 0.8rem; margin-top: 0.5rem;'>
                    Powered by Streamlit & Plotly
                </div>
            </div>
        """, unsafe_allow_html=True)

# Run the dashboard
if __name__ == "__main__":
    dashboard = Dashboard()
    dashboard.run()