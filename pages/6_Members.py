import streamlit as st


def show_members_page():
    # Page configuration with better spacing
    st.set_page_config(layout="wide", page_title="Team Members")

    # Custom CSS for enhanced styling
    st.markdown("""
    <style>
    .member-card {
        background: white;
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid #e0e0e0;
        transition: all 0.3s ease;
        height: fit-content;
        margin-bottom: 1.5rem;
    }
    
    .member-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
    }
    
    .member-name {
        font-size: 1.1rem;
        font-weight: 600;
        color: #2d3748;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #f0f2f6;
    }
    
    .contributions-title {
        font-size: 0.9rem;
        font-weight: 500;
        color: #4a5568;
        margin-bottom: 0.8rem;
    }
    
    .chip {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        margin: 0.2rem 0.3rem;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
    }
    </style>
    """, unsafe_allow_html=True)

    # Page header
    st.markdown("""
        <h1 style="margin:0; font-size: 2.5rem;">👥 Project Team Members</h1>
        <p style="margin:0; opacity: 0.9; font-size: 1.1rem;">Group 3 • Final Project</p>
    """, unsafe_allow_html=True)

    # Team members data with icons and colors
    members = [
        {
            "name": "SHAWN MICHAEL MANA-AY",
            "contributions": ["Main Dashboard", "Data Visualization"],
            "icon": "🎯",
            "color": "#45B7D1"
        },
        {
            "name": "RAPHAEL MATTHEW AZUCENA",
            "contributions": ["Supplementary Dataset and Policies"],
            "icon": "📊",
            "color": "#FF6B6B"
        },
        {
            "name": "JOSEBELLE DELGADO",
            "contributions": ["EducationOccupation.py", "Data Visualization"],
            "icon": "📈",
            "color": "#4ECDC4"
        },
        {
            "name": "RAPHEL ANGELO MERCADO",
            "contributions": ["MigrationData.py"],
            "icon": "🌐",
            "color": "#96CEB4"
        },
        {
            "name": "AARON PAGAYUNAN",
            "contributions": ["GenderOccupation.py Pages"],
            "icon": "👨‍💼",
            "color": "#F67FD4"
        },
    ]

    # Search box with better styling
    st.markdown("---")

    query = ""

    # Responsive layout
    cols = st.columns(3)

    # Filter and display members
    filtered_members = [
        member for member in members
        if not query or
        query in member["name"].lower() or
        any(query in contri.lower() for contri in member["contributions"])
    ]

    if not filtered_members:
        st.warning("No team members found matching your search criteria.")
        return

    for i, member in enumerate(filtered_members):
        with cols[i % 3]:
            # Custom card with unique colors
            st.markdown(f"""
            <div class="member-card">
                <div class="member-name">
                    <span style="font-size: 1.3rem; margin-right: 0.5rem;">{member['icon']}</span>
                    {member["name"]}
                </div>
                <div class="contributions-title">Key Contributions:</div>
                <div>
                    {''.join(f'<span class="chip" style="background: {member["color"]};">• {c}</span>' for c in member["contributions"])}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Footer section
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9rem;">
        <p>Built with ❤️ using Streamlit • Group 3 Final Project</p>
    </div>
    """, unsafe_allow_html=True)


def show_readme_page():
    st.set_page_config(layout="wide", page_title="Project Documentation")

    st.markdown("""
    <style>
    .readme-section {
        # background: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.6);
        margin-bottom: 1rem;
        # border-left: 4px solid #667eea;
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("🇵🇭 Filipino Migrators Dashboard")

    st.markdown("""
    <div class="readme-section">
    <h2>📖 Project Overview</h2>
    <p>A <strong>Streamlit web application</strong> that visualizes <strong>Filipino migration patterns and trends</strong> across countries, age groups, education levels, occupations, gender, and civil status. Explore historical migration data and uncover insights about demographic shifts over time.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="readme-section">
    <h2>🚀 Features</h2>
    <ul>
    <li>Interactive <strong>migration visualizations</strong> by country, age, education, occupation, gender, and civil status</li>
    <li><strong>Year-wise trends</strong> and comparisons</li>
    <li><strong>Searchable and filterable dashboards</strong> for focused insights</li>
    <li><strong>Downloadable datasets</strong> for offline analysis</li>
    <li>Built using <strong>Python, Pandas, Streamlit, and Plotly/Matplotlib</strong></li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="readme-section">
    <h2>👨‍💻 Team Members – Group 3</h2>
    """, unsafe_allow_html=True)

    team_data = {
        "Name": [
            "Raphael Matthew Azucena",
            "Shawn Michael Mana-ay",
            "Aaron Pagayunan",
            "Josebelle Delgado",
            "Raphel Angelo Mercado"
        ],
        "Role / Contribution": [
            "Supplementary Data Development",
            "Data Processing & Lead Development",
            "Demographics Visualization Development",
            "Education and Occupation Visualization",
            "Choropleth for Migration Location"
        ]
    }

    st.table(team_data)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="readme-section">
    <h2>⚡ Getting Started</h2>
    <h3>Prerequisites</h3>
    <ul>
    <li>Python 3.7+</li>
    <li>pip (Python package manager)</li>
    </ul>
    
    <h3>Installation & Setup</h3>
    <ol>
    <li><strong>Clone the repository</strong>
    <pre><code>git clone https://github.com/shawnflorida/Filipino.Migrants.Analytics_DATA101M
    cd Filipino.Migrants.Analytics_DATA101M</code></pre>
    </li>
    <li><strong>Install dependencies</strong>
    <pre><code>pip install -r requirements.txt</code></pre>
    </li>
    <li><strong>Run the Streamlit app</strong>
    <pre><code>streamlit run Home.py</code></pre>
    </li>
    <li><strong>Open your browser</strong> at <code>http://localhost:8501</code> to explore the dashboard.</li>
    <li><strong>Open the website online</strong> at <a href="https://dataviz101m---final-project-k2vml2puzghqjcvnhgbmae.streamlit.app/">Streamlit App</a></li>
    </ol>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="readme-section">
    <h2>🛠 Technologies Used</h2>
    <ul>
    <li><strong>Python</strong> – Data processing & analysis</li>
    <li><strong>Pandas & NumPy</strong> – Data wrangling and manipulation</li>
    <li><strong>Streamlit</strong> – Dashboard development</li>
    <li><strong>Matplotlib & Plotly</strong> – Visualizations</li>
    <li><strong>Jupyter Notebook</strong> – Exploratory data analysis</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="readme-section">
    <h2>📄 License</h2>
    <p>This project is licensed under the MIT License - see the <a href="https://github.com/shawnflorida/DataViz101M---Final-Project/blob/main/LICENSE">LICENSE</a> file for details.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="readme-section">
    <h2>📞 Contact</h2>
    <ul>
    <li>shawn_mana-ay@dlsu.edu.ph</li>
    <li>raphael_matthew_azucena@dlsu.edu.ph</li>
    <li>josebelle_delgado@dlsu.edu.ph</li>
    <li>raphel_mercado@dlsu.edu.ph</li>
    <li>aaron_pagayunan@dlsu.edu.ph</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)


def main():
    # st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Team Members", "Project Documentation"])

    if page == "Team Members":
        show_members_page()
    else:
        show_readme_page()


if __name__ == "__main__":
    main()
