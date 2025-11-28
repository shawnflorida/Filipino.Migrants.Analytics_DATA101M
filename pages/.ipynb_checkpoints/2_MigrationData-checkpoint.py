import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os

# ---------- Page config ----------
st.set_page_config(
    page_title="Migration Pattern Analysis",
    page_icon="🇵🇭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Dark mode CSS (same as dashboard) ----------
st.markdown(
    """
    <style>
    /* Backgrounds */
    .stApp {
        background-color: #111827;
        color: #e5e7eb;
    }
    section[data-testid="stSidebar"] {
        background-color: #020617;
        border-right: 1px solid #1f2937;
    }
    /* Titles */
    h1, h2, h3, h4 {
        color: #f9fafb;
    }
    /* Selectboxes, sliders, etc. */
    .stSelectbox, .stSlider {
        color: #e5e7eb;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Data loader ----------
class DataLoader:
    @staticmethod
    @st.cache_data
    def load_all_data():
        try:
            base_path = os.path.join("data", "raph", "clean_migration_origin_destination.csv")
            df = pd.read_csv(base_path)
            return {"main": df}
        except Exception as e:
            st.error(f"Error loading data: {e}")
            st.stop()

# ---------- Data processor ----------
class DataProcessor:
    def __init__(self, data_dict):
        self.data = data_dict
        self.country_mapping = {
            # … keep your full mapping …
        }

    def prepare_main_df(self):
        df = self.data["main"].copy()
        df["origin_region"] = df["origin_region"].astype(str).str.strip()
        df["destination_country"] = df["destination_country"].astype(str).str.strip()

        df["destination_clean"] = (
            df["destination_country"]
            .str.lower()
            .str.replace(r"[^a-z0-9]+", "_", regex=True)
            .str.strip("_")
        )
        df["destination_pretty"] = df["destination_clean"].map(self.country_mapping).fillna(
            df["destination_country"]
        )
        return df

# ---------- Load data & geojson ----------
data_dict = DataLoader.load_all_data()
processor = DataProcessor(data_dict)
df = processor.prepare_main_df()

with open("data/raph/countries (1).geojson", "r", encoding="utf-8") as f:
    world_geojson = json.load(f)

country_prop = "name"

# ---------- Sidebar: Filters card ----------
with st.sidebar:
    st.markdown("## Filters")
    years = sorted(df["year"].unique())
    selected_year = st.slider(
        "Year",
        min_value=int(min(years)),
        max_value=int(max(years)),
        value=int(max(years)),
        step=1,
    )

    origin_options = ["All regions"] + sorted(df["origin_region"].unique())
    selected_origin = st.selectbox("Origin Region", origin_options)

    dest_options = ["All countries"] + sorted(df["destination_pretty"].unique())
    selected_dest = st.selectbox("Destination Country", dest_options)

# ---------- Main layout ----------
st.markdown("Rough Idea of Migration Pattern")

st.markdown("Will edit the logic and creativity later")

# Filters -> dataframe
mask = df["year"] == selected_year
if selected_origin != "All regions":
    mask &= df["origin_region"] == selected_origin
if selected_dest != "All countries":
    mask &= df["destination_pretty"] == selected_dest

df_filtered = df[mask].copy()

map_df = (
    df_filtered.groupby("destination_pretty", as_index=False)["migrants"]
    .sum()
    .rename(columns={"destination_pretty": "Destination", "migrants": "Migrants"})
)

map_df["Destination"] = map_df["Destination"].astype(str).str.strip().str.title()
name_fixes = {
    "United States Of America": "United States of America",
    "Hongkong": "Hong Kong",
    "Taiwan": "Taiwan",
}
map_df["Destination"] = map_df["Destination"].replace(name_fixes)

# ---------- Choropleth (dark style) ----------
fig = px.choropleth(
    map_df,
    geojson=world_geojson,
    locations="Destination",
    featureidkey=f"properties.{country_prop}",
    color="Migrants",
    color_continuous_scale="Viridis",
    labels={"Migrants": "Migrants"},
)

fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(
    paper_bgcolor="#111827",
    plot_bgcolor="#111827",
    font=dict(color="#e5e7eb"),
    margin=dict(l=0, r=0, t=10, b=0),
    coloraxis_colorbar=dict(title="Migrants", tickfont=dict(color="#e5e7eb")),
)

st.plotly_chart(fig, use_container_width=True)

total_migrants = int(df_filtered["migrants"].sum())
dest_label = selected_dest if selected_dest != "All countries" else "All Countries"
origin_label = selected_origin if selected_origin != "All regions" else "All Regions"

st.markdown(
    f"There are **{total_migrants:,}** people coming from **{origin_label}** "
    f"to **{dest_label}** in year **{selected_year}**."
)


# PAGE BREAK DUMMY CODE AHEAD

import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os

# ---------- Page config ----------
st.set_page_config(
    page_title="Migration Pattern Analysis",
    page_icon="🇵🇭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Dark mode CSS (same palette as dashboard) ----------
st.markdown(
    """
    <style>
    .stApp { background-color: #111827; color: #e5e7eb; }
    section[data-testid="stSidebar"] { background-color: #020617; border-right: 1px solid #1f2937; }
    h1, h2, h3, h4 { color: #f9fafb; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Data loader ----------
class DataLoader:
    @staticmethod
    @st.cache_data
    def load_all_data():
        try:
            base_path = os.path.join("data", "raph", "clean_migration_origin_destination.csv")
            df = pd.read_csv(base_path)
            return {"main": df}
        except Exception as e:
            st.error(f"Error loading data: {e}")
            st.stop()

# ---------- Data processor ----------
class DataProcessor:
    def __init__(self, data_dict):
        self.data = data_dict
        self.country_mapping = {
            # keep your full mapping here (truncated for brevity)
            'united_states_of_america': 'United States Of America',
            'hongkong': 'Hong Kong',
            'taiwan_roc': 'Taiwan',
            # ... plus all other countries ...
        }

    def prepare_main_df(self):
        df = self.data["main"].copy()
        df["origin_region"] = df["origin_region"].astype(str).str.strip()
        df["destination_country"] = df["destination_country"].astype(str).str.strip()

        df["destination_clean"] = (
            df["destination_country"]
            .str.lower()
            .str.replace(r"[^a-z0-9]+", "_", regex=True)
            .str.strip("_")
        )
        df["destination_pretty"] = df["destination_clean"].map(self.country_mapping).fillna(
            df["destination_country"]
        )
        return df

# ---------- Load data & GeoJSON ----------
data_dict = DataLoader.load_all_data()
processor = DataProcessor(data_dict)
df = processor.prepare_main_df()

with open("data/raph/countries (1).geojson", "r", encoding="utf-8") as f:
    world_geojson = json.load(f)

country_prop = "name"  # e.g. {'name': 'Malaysia', ...}

# ---------- Sidebar: filters ----------
with st.sidebar:
    st.markdown("## Filters")

    years = sorted(df["year"].unique())
    selected_year = st.slider(
        "Year",
        min_value=int(min(years)),
        max_value=int(max(years)),
        value=int(max(years)),
        step=1,
    )

    origin_options = sorted(df["origin_region"].unique())
    selected_origin = st.selectbox("Origin Region (for arrow)", origin_options)

    dest_options = sorted(df["destination_pretty"].unique())
    selected_dest = st.selectbox("Destination Country (for arrow)", dest_options)

# ---------- 1) Choropleth data: year only ----------
base_mask = df["year"] == selected_year
df_base = df[base_mask].copy()

map_df = (
    df_base.groupby("destination_pretty", as_index=False)["migrants"]
    .sum()
    .rename(columns={"destination_pretty": "Destination", "migrants": "Migrants"})
)

map_df["Destination"] = map_df["Destination"].astype(str).str.strip().str.title()
name_fixes = {
    "United States Of America": "United States of America",
    "Hongkong": "Hong Kong",
    "Taiwan": "Taiwan",
}
map_df["Destination"] = map_df["Destination"].replace(name_fixes)

# ---------- 2) Arrow / highlight data: year + origin + dest ----------
arrow_mask = (
    (df["year"] == selected_year)
    & (df["origin_region"] == selected_origin)
    & (df["destination_pretty"] == selected_dest)
)
df_arrow = df[arrow_mask].copy()
arrow_migrants = int(df_arrow["migrants"].sum()) if not df_arrow.empty else 0

# ---------- Choropleth ----------
fig = px.choropleth(
    map_df,
    geojson=world_geojson,
    locations="Destination",
    featureidkey=f"properties.{country_prop}",
    color="Migrants",
    color_continuous_scale="Viridis",
    labels={"Migrants": "Migrants"},
)

fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(
    paper_bgcolor="#111827",
    plot_bgcolor="#111827",
    font=dict(color="#e5e7eb"),
    margin=dict(l=0, r=0, t=10, b=0),
    coloraxis_colorbar=dict(title="Migrants", tickfont=dict(color="#e5e7eb")),
)

# Optional: visually highlight selected destination country (outline)
if arrow_migrants > 0:
    dest_name = selected_dest.title()
    dest_name = name_fixes.get(dest_name, dest_name)

    # Add an extra trace with higher line width for the chosen country
    fig.add_choropleth(
        geojson=world_geojson,
        locations=[dest_name],
        featureidkey=f"properties.{country_prop}",
        z=[arrow_migrants],
        showscale=False,
        marker_line_width=2.5,
        marker_line_color="#facc15",  # yellow outline
        colorscale=[[0, "#facc15"], [1, "#facc15"]],
    )

# ---------- Layout ----------
st.markdown("## Migration Pattern Analysis")

st.plotly_chart(fig, use_container_width=True)

st.markdown(
    f"In **{selected_year}**, there are **{arrow_migrants:,}** migrants "
    f"from **{selected_origin}** going to **{selected_dest}**."
)

