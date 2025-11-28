import streamlit as st


def show_members_page():
    # Page configuration with better spacing
    st.set_page_config(layout="wide", page_title="Team Members")

    # Custom CSS for enhanced styling
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        margin-bottom: 2rem;
        color: white;
    }
    
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
    
    .search-box {
        background: white;
        padding: 1rem;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin-bottom: 2rem;
    }
    
  
    

    
    </style>
    """, unsafe_allow_html=True)

    # Page header with gradient
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


show_members_page()
