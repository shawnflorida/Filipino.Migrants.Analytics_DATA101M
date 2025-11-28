import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# ---------- Page config ----------
st.set_page_config(
    page_title="Migration Pattern Analysis",
    page_icon="🇵🇭",
    layout="wide",
    initial_sidebar_state="expanded",
)

EXPLANATIONS = {
    1995: "The Migrant Workers and Overseas Filipinos Act (RA 8042) changed how the Philippines manages and protects OFWs. This helped shape deployment patterns in this period.",
    1997: "The Asian Financial Crisis affected many Asian economies. Some Filipinos looked for work abroad as local opportunities became less stable.",
    2008: "The Global Financial Crisis shook job markets worldwide. Demand shifted, but many Filipinos still relied on overseas work for income.",
}
DEFAULT_EXPLANATION = (
    "Migration in this year reflects ongoing economic gaps between the Philippines and destination "
    "countries, plus established labor corridors for Filipino workers."
)

# ---------- Data loader ----------
class DataLoader:
    @staticmethod
    @st.cache_data
    def load_all_data():
        try:
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            base_path = os.path.join(project_root, "data", "raph", "clean_migration_origin_destination.csv")
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
            'albania': 'Albania',
            'andorra': 'Andorra',
            'angola': 'Angola',
            'anguilla': 'Anguilla',
            'antigua_and_barbuda': 'Antigua And Barbuda',
            'argentina': 'Argentina',
            'armenia': 'Armenia',
            'aruba': 'Aruba',
            'australia': 'Australia',
            'austria': 'Austria',
            'bahamas': 'Bahamas',
            'bahrain': 'Bahrain',
            'bangladesh': 'Bangladesh',
            'barbados': 'Barbados',
            'belgium': 'Belgium',
            'bermuda': 'Bermuda',
            'bolivia': 'Bolivia',
            'bosnia_and_herzegovina': 'Bosnia And Herzegovina',
            'brazil': 'Brazil',
            'british_virgin_islands': 'British Virgin Islands',
            'brunei_darussalam': 'Brunei Darussalam',
            'bulgaria': 'Bulgaria',
            'cameroon': 'Cameroon',
            'canada': 'Canada',
            'cayman_islands': 'Cayman Islands',
            'channel_island': 'Channel Island',
            'chile': 'Chile',
            'china_p_r_o_c': 'China (P.R.O.C.)',
            'cocos_keeling_island': 'Cocos (Keeling) Island',
            'colombia': 'Colombia',
            'costa_rica': 'Costa Rica',
            'croatia': 'Croatia',
            'cyprus': 'Cyprus',
            'czech_republic': 'Czech Republic',
            'democratic_kampuchea': 'Democratic Kampuchea',
            'democratic_republic_of_the_congo_zaire': 'Democratic Republic Of The Congo (Zaire)',
            'denmark': 'Denmark',
            'dominican_republic': 'Dominican Republic',
            'ecuador': 'Ecuador',
            'egypt': 'Egypt',
            'estonia': 'Estonia',
            'ethiopia': 'Ethiopia',
            'falkland_islands_malvinas': 'Falkland Islands (Malvinas)',
            'faroe_islands': 'Faroe Islands',
            'fiji': 'Fiji',
            'finland': 'Finland',
            'france': 'France',
            'french_polynesia': 'French Polynesia',
            'gabon': 'Gabon',
            'georgia': 'Georgia',
            'germany': 'Germany',
            'ghana': 'Ghana',
            'gibraltar': 'Gibraltar',
            'greece': 'Greece',
            'greenland': 'Greenland',
            'hongkong': 'Hong Kong',
            'hungary': 'Hungary',
            'iceland': 'Iceland',
            'india': 'India',
            'indonesia': 'Indonesia',
            'iran': 'Iran',
            'iraq': 'Iraq',
            'ireland': 'Ireland',
            'isle_of_man': 'Isle Of Man',
            'israel': 'Israel',
            'italy': 'Italy',
            'japan': 'Japan',
            'jordan': 'Jordan',
            'kazakhstan': 'Kazakhstan',
            'kenya': 'Kenya',
            'kiribati': 'Kiribati',
            'kuwait': 'Kuwait',
            'latvia': 'Latvia',
            'lebanon': 'Lebanon',
            'leichtenstein': 'Leichtenstein',
            'lesotho': 'Lesotho',
            'liberia': 'Liberia',
            'libya': 'Libya',
            'lithuania': 'Lithuania',
            'luxembourg': 'Luxembourg',
            'macau': 'Macau',
            'macedonia': 'Macedonia',
            'malaysia': 'Malaysia',
            'maldives': 'Maldives',
            'malta': 'Malta',
            'marshall_islands': 'Marshall Islands',
            'mauritius': 'Mauritius',
            'mexico': 'Mexico',
            'midway_island': 'Midway Island',
            'moldova': 'Moldova',
            'monaco': 'Monaco',
            'morocco': 'Morocco',
            'mozambique': 'Mozambique',
            'myanmar_burma': 'Myanmar (Burma)',
            'namibia': 'Namibia',
            'nepal': 'Nepal',
            'netherlands': 'Netherlands',
            'netherlands_antilles': 'Netherlands Antilles',
            'new_caledonia': 'New Caledonia',
            'new_zealand': 'New Zealand',
            'nigeria': 'Nigeria',
            'norway': 'Norway',
            'oman': 'Oman',
            'pacific_islands': 'Pacific Islands',
            'pakistan': 'Pakistan',
            'palau': 'Palau',
            'panama': 'Panama',
            'papua_new_guinea': 'Papua New Guinea',
            'peru': 'Peru',
            'poland': 'Poland',
            'portugal': 'Portugal',
            'puerto_rico': 'Puerto Rico',
            'qatar': 'Qatar',
            'reunion': 'Reunion',
            'romania': 'Romania',
            'russian_federation_ussr': 'Russian Federation / Ussr',
            'saint_lucia': 'Saint Lucia',
            'san_marino': 'San Marino',
            'saudi_arabia': 'Saudi Arabia',
            'senegal': 'Senegal',
            'seychelles': 'Seychelles',
            'singapore': 'Singapore',
            'sint_maarten': 'Sint Maarten',
            'slovak_republic': 'Slovak Republic',
            'slovenia': 'Slovenia',
            'solomon_islands': 'Solomon Islands',
            'south_africa': 'South Africa',
            'south_korea': 'South Korea',
            'spain': 'Spain',
            'sri_lanka': 'Sri Lanka',
            'sudan': 'Sudan',
            'sweden': 'Sweden',
            'switzerland': 'Switzerland',
            'syria': 'Syria',
            'taiwan_roc': 'Taiwan',
            'thailand': 'Thailand',
            'trinidad_and_tobago': 'Trinidad And Tobago',
            'tunisia': 'Tunisia',
            'turkey': 'Turkey',
            'turks_and_caicos_islands': 'Turks And Caicos Islands',
            'uganda': 'Uganda',
            'ukraine': 'Ukraine',
            'united_arab_emirates': 'United Arab Emirates',
            'united_kingdom': 'United Kingdom',
            'united_republic_of_tanzania': 'United Republic Of Tanzania',
            'united_states_of_america': 'United States Of America',
            'uruguay': 'Uruguay',
            'uzbekistan': 'Uzbekistan',
            'vanuatu': 'Vanuatu',
            'venezuela': 'Venezuela',
            'vietnam': 'Vietnam',
            'wake_island': 'Wake Island',
            'yemen': 'Yemen',
            'yugoslavia_serbia_montenegro': 'Yugoslavia (Serbia & Montenegro)',
            'zambia': 'Zambia',
        }

    def prepare_main_df(self):
        df = self.data["main"].copy()
        df["origin_region"] = df["origin_region"].astype(str).str.strip()
        df["destination_country"] = df["destination_country"].astype(str).str.strip()

        df["destination_country"] = df["destination_country"].replace({
            "PHILIPPINES": "Philippines",
            "REPUBLIC OF THE PHILIPPINES": "Philippines",
        })

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

# ---------- Load data ----------
data_dict = DataLoader.load_all_data()
processor = DataProcessor(data_dict)
df = processor.prepare_main_df()

# ---------- Sidebar ----------
st.sidebar.header("Filters")

years = sorted(df["year"].unique())
selected_year = st.sidebar.slider(
    "Year",
    min_value=int(min(years)),
    max_value=int(max(years)),
    value=int(max(years)),
    step=1,
)

origin_options = ["All regions"] + sorted(df["origin_region"].unique())
selected_origin = st.sidebar.selectbox("Origin Region", origin_options)

dest_options = ["All countries"] + sorted(df["destination_pretty"].unique())
selected_dest = st.sidebar.selectbox("Destination Country", dest_options)

# ---------- Cumulative total migrants up to selected year ----------
df_year_totals = (
    df.groupby("year", as_index=False)["migrants"]
    .sum()
    .sort_values("year")
)
df_year_totals["cumulative_migrants"] = df_year_totals["migrants"].cumsum()
cum_total_row = df_year_totals[df_year_totals["year"] == selected_year]
cum_total_migrants = int(cum_total_row["cumulative_migrants"].iloc[0]) if not cum_total_row.empty else 0

# --- Sidebar KPI: total migrant population up to selected year ---
st.sidebar.markdown("---")
st.sidebar.markdown("**Total Migrant Population (up to selected year)**")
st.sidebar.markdown(f"## {cum_total_migrants:,}")  # bigger than ###

st.sidebar.caption(
    f"Population total as of **{selected_year}** based on all recorded "
    f"origin regions and destination countries."
)

# ---------- Filtered data for map ----------
year_mask = df["year"] == selected_year
df_year = df[year_mask].copy()

if selected_origin != "All regions":
    df_year = df_year[df_year["origin_region"] == selected_origin]

if selected_dest != "All countries":
    df_year = df_year[df_year["destination_pretty"] == selected_dest]

# ---------- Totals and insight text ----------
summary_mask = df["year"] == selected_year
if selected_origin != "All regions":
    summary_mask &= df["origin_region"] == selected_origin
if selected_dest != "All countries":
    summary_mask &= df["destination_pretty"] == selected_dest

df_summary = df[summary_mask]
total_migrants = int(df_summary["migrants"].sum()) if not df_summary.empty else 0
dest_label = selected_dest if selected_dest != "All countries" else "All Countries"
origin_label = selected_origin if selected_origin != "All regions" else "All Regions"

base_text = EXPLANATIONS.get(selected_year, DEFAULT_EXPLANATION)

if total_migrants == 0:
    zero_note = (
        f" This dataset records no documented migrants to **{dest_label}** in **{selected_year}** "
        f"under the current filters. This may reflect limited labor demand, absence of formal "
        f"deployment channels, or gaps in available statistics rather than the absolute absence "
        f"of any Filipino migrants."
    )
else:
    zero_note = ""

insight_text = (
    f"{base_text} "
    f"In your filtered data, there are **{total_migrants:,}** migrants "
    f"moving from **{origin_label}** to **{dest_label}** in **{selected_year}**."
    f"{zero_note}"
)


# ---------- Aggregated data for map ----------
all_countries = (
    df_year.groupby("destination_pretty", as_index=False)["migrants"]
    .sum()
    .rename(columns={"destination_pretty": "Destination", "migrants": "Migrants"})
)
all_countries = all_countries[all_countries["Migrants"] > 0].sort_values("Migrants", ascending=False)

top_n = 10
top_df = all_countries.head(top_n)

# ---------- Base world map ----------
fig = px.choropleth(
    all_countries,
    locations="Destination",
    locationmode="country names",
    color="Migrants",
    color_continuous_scale="Viridis",
    labels={"Migrants": "Migrants"},
)
fig.update_geos(
    projection_type="natural earth",
    showcoastlines=True,
    coastlinecolor="#1f2937",
    showland=True,
    landcolor="#020617",
    showcountries=True,
    countrycolor="#1f2937",
)
fig.update_layout(
    paper_bgcolor="#020617",
    plot_bgcolor="#020617",
    font=dict(color="#e5e7eb"),
    margin=dict(l=0, r=0, t=0, b=0),
    coloraxis_colorbar=dict(title="Migrants", tickfont=dict(color="#e5e7eb")),
)

# ---------- Labels on top 10 ----------
fig.add_trace(
    go.Scattergeo(
        locationmode="country names",
        locations=top_df["Destination"],
        text=top_df.apply(
            lambda r: f"{r['Destination']}<br>{int(r['Migrants']):,}", axis=1
        ),
        mode="text",
        textfont=dict(color="white", size=10),
        showlegend=False,
        hoverinfo="none",
    )
)

# ---------- Orange lines from Philippines to top 10 ----------
ph_lat, ph_lon = 12.8797, 121.7740  # Philippines centroid

line_lats = []
line_lons = []

for _, row in top_df.iterrows():
    dest = row["Destination"]
    try:
        tmp = px.scatter_geo(
            pd.DataFrame({"country": [dest]}),
            locations="country",
            locationmode="country names",
        )
        d_lon = float(tmp.data[0]["lon"][0])
        d_lat = float(tmp.data[0]["lat"][0])
    except Exception:
        continue

    line_lats.extend([ph_lat, d_lat, None])
    line_lons.extend([ph_lon, d_lon, None])

if line_lats:
    fig.add_trace(
        go.Scattergeo(
            lon=line_lons,
            lat=line_lats,
            mode="lines",
            line=dict(color="#f97316", width=4),
            opacity=0.9,
            showlegend=False,
            hoverinfo="skip",
        )
    )
# ---------- Layout ----------
title_col, year_col = st.columns([3, 1])

with title_col:
    st.title("✈️ Migration Pattern Analysis")
    st.subheader(
        "Tracing where Filipinos move across the globe, one year and destination at a time."
    )

with year_col:
    st.markdown("<br>", unsafe_allow_html=True)  # small vertical spacer
    st.markdown(f" 🗓️ Selected year")
    st.markdown(f"# {selected_year}")

st.plotly_chart(fig, use_container_width=True)

# Yearly insight card
with st.container():
    st.markdown("### 📊 Yearly Phenomenon Insight")
    st.markdown(
        f"""
<small>{insight_text}</small>
""",
        unsafe_allow_html=True,
    )

# ---------- Top destinations panel ----------
if selected_dest == "All countries":
    top5 = all_countries.head(5).copy()
    if not top5.empty:
        st.markdown("### 🏆 Top Destination Countries")
        col1, col2, col3, col4, col5 = st.columns(5)

        cols = [col1, col2, col3, col4, col5]
        for col, (_, row) in zip(cols, top5.iterrows()):
            with col:
                st.markdown(
                    f"**{row['Destination']}**  \n"
                    f"{int(row['Migrants']):,} migrants",
                )

color_max = all_countries["Migrants"].max() if not all_countries.empty else 0

fig = px.choropleth(
    all_countries,
    locations="Destination",
    locationmode="country names",
    color="Migrants",
    color_continuous_scale="Viridis",
    range_color=(0, color_max),
    labels={"Migrants": "Migrants"},
)

# share of migrants going to selected_dest (if not 'All countries')
dest_share_text = ""

if selected_dest != "All countries" and total_migrants > 0:
    prev_year = selected_year - 1
    if prev_year in years:
        prev_mask = (df["year"] == prev_year)

        if selected_origin != "All regions":
            prev_mask &= df["origin_region"] == selected_origin
        if selected_dest != "All countries":
            prev_mask &= df["destination_pretty"] == selected_dest

        prev_total = int(df.loc[prev_mask, "migrants"].sum())

        if prev_total > 0:
            change_pct = (total_migrants - prev_total) / prev_total * 100
            direction = "increased" if change_pct >= 0 else "decreased"
            dest_share_text = (
                f" This destination’s migrants **{direction} by {abs(change_pct):.1f}%** "
                f"compared with **{prev_year}** under the same filters."
            )


st.markdown(
    f"There are **{total_migrants:,}** people coming from **{origin_label}** "
    f"to **{dest_label}** in year **{selected_year}**.{dest_share_text}"
)
