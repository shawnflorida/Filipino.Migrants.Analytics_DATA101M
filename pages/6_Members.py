import streamlit as st


def show_members_page():
    st.title("👥 Project Team Members")
    st.subheader("Group 3")

    st.markdown("---")

    # Team members data
    members = [
        {
            "name": "RAPHAEL MATTHEW AZUCENA",
            "contributions": ["Supplementary Dataset and Policies"]
        },
        {
            "name": "JOSEBELLE DELGADO",
            "contributions": ["EducationOccupation.py", "Data Visualization"]
        },
        {
            "name": "SHAWN MICHAEL MANA-AY",
            "contributions": ["Main Dashboard", "Data Visualization"]
        },
        {
            "name": "RAPHEL ANGELO MERCADO",
            "contributions": ["MigrationData.py"]
        },
        {
            "name": "AARON PAGAYUNAN",
            "contributions": ["GenderOccupation.py Pages"]
        }
    ]

    # Display members in a nice layout
    cols = st.columns(2)

    for i, member in enumerate(members):
        with cols[i % 2]:
            with st.container():
                st.markdown(f"### {member['name']}")
                st.markdown("**Contributions:**")
                for contribution in member['contributions']:
                    st.markdown(f"• {contribution}")
                st.markdown("---")


show_members_page()
