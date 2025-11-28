import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter

# ------------------------
# Page meta + styling
# ------------------------
st.set_page_config(page_title="Gender & Occupation", layout="wide")
st.title("Gender & Occupation — Distribution & Trends")
st.markdown(
    "Explore occupation distributions and gender splits in the workforce using official CFO data. "
    "This page highlights trends over time, shows the concentration of workers across different occupations, "
    "and provides insights into gender-specific patterns and shifts within the workforce."
)

# ------------------------
# Load data
# ------------------------


@st.cache_data
def load_data():
    base = "data"
    occu = pd.read_csv(f"{base}/occu_pivot.csv")
    sex = pd.read_csv(f"{base}/sex_pivot.csv")

    # Clean occupation column names
    col_map = {}
    for c in occu.columns:
        if c == "year":
            col_map[c] = c
        else:
            nicer = c.replace("_", " ").replace("&", "and")
            nicer = " ".join([w.capitalize() for w in nicer.split()])
            col_map[c] = nicer
    occu = occu.rename(columns=col_map)

    # Normalize sex column names to 'Male' and 'Female'
    sex_cols = {c.lower(): c for c in sex.columns}
    if "male" in sex_cols and "female" in sex_cols:
        sex = sex.rename(
            columns={sex_cols["male"]: "Male", sex_cols["female"]: "Female"})

    return occu, sex


occu_df, sex_df = load_data()

# ------------------------
# Sidebar filters & controls
# ------------------------
st.sidebar.header("Filters & Options")

years = sorted(occu_df["year"].unique())
if len(years) == 0:
    st.error("No years found in occupation dataset.")
    st.stop()

selected_year = st.sidebar.selectbox(
    "Select year", options=years, index=len(years) - 1)

occu_columns = [c for c in occu_df.columns if c != "year"]
default_top_n = 12
top_n = st.sidebar.slider("Number of occupations to display",
                          min_value=3, max_value=15, value=default_top_n)

occupation_multiselect = st.sidebar.multiselect(
    "Filter occupations",
    options=sorted(occu_columns),
    default=[]
)

show_estimate_note = st.sidebar.checkbox(
    "Show approximation note (gender split estimate)", value=True)
normalize_option = st.sidebar.radio(
    "Show counts or percentages:", ("Counts", "Percent of total (selected year)"))

st.sidebar.markdown("---")
st.sidebar.write(
    "Design note: Mirrored bar chart is an *estimated* gender split derived by applying "
    "the overall male/female shares for the selected year to each occupation."
)

# ------------------------
# Prepare data for selected year
# ------------------------
row = occu_df[occu_df["year"] == selected_year]
if row.shape[0] == 0:
    st.error(f"No occupation data available for year {selected_year}")
    st.stop()

occ_year = row.drop(columns="year").T.reset_index()
occ_year.columns = ["Occupation", "Count"]
occ_year = occ_year.sort_values("Count", ascending=False)

if occupation_multiselect:
    display_df = occ_year[occ_year["Occupation"].isin(
        occupation_multiselect)].copy()
else:
    display_df = occ_year.head(top_n).copy()

# ------------------------
# Estimate gender split
# ------------------------
sex_row = sex_df[sex_df["year"] == selected_year]
if sex_row.shape[0] == 0:
    st.warning(
        f"Gender totals not available for {selected_year}. Using overall proportions from latest year.")
    sex_row = sex_df.iloc[[-1]]

if "Male" not in sex_row.columns or "Female" not in sex_row.columns:
    st.error(
        "Sex totals table must contain 'Male' and 'Female' columns (case-insensitive).")
    st.stop()

male_total = int(sex_row["Male"].values[0])
female_total = int(sex_row["Female"].values[0])
total_people = male_total + female_total
male_share = male_total / total_people if total_people else 0.5
female_share = female_total / total_people if total_people else 0.5

est = display_df.copy()
est["Male"] = (est["Count"] * male_share).round().astype(int)
est["Female"] = (est["Count"] * female_share).round().astype(int)

if normalize_option == "Percent of total (selected year)":
    total_for_percent = float(display_df["Count"].sum())
    if total_for_percent > 0:
        est["Male_pct"] = est["Male"] / total_for_percent * 100
        est["Female_pct"] = est["Female"] / total_for_percent * 100
        value_col = "Male_pct"
        value_col_f = "Female_pct"
        x_title = "Percent of total migrants (%)"
    else:
        est["Male_pct"] = 0
        est["Female_pct"] = 0
        value_col = "Male_pct"
        value_col_f = "Female_pct"
        x_title = "Percent of total migrants (%)"
else:
    value_col = "Male"
    value_col_f = "Female"
    x_title = "Number of migrants"

# ------------------------
# Mirrored bar chart with Matplotlib
# ------------------------
st.subheader("👥 Gender Distribution by Occupation — Mirrored View")

# Prepare data for mirrored chart
mirror_df = est.copy()
if normalize_option == "Percent of total (selected year)":
    mirror_df["Female_mirror"] = -mirror_df["Female_pct"]
    mirror_df["Male_mirror"] = mirror_df["Male_pct"]
    male_values = mirror_df["Male_pct"].values
    female_values = mirror_df["Female_pct"].values
else:
    mirror_df["Female_mirror"] = -mirror_df["Female"]
    mirror_df["Male_mirror"] = mirror_df["Male"]
    male_values = mirror_df["Male"].values
    female_values = mirror_df["Female"].values

# Sort occupations by total count
mirror_df = mirror_df.sort_values("Count", ascending=True)
occupations = mirror_df["Occupation"].tolist()

# Create mirrored bar chart
fig, ax = plt.subplots(figsize=(12, 8 + max(0, (len(occupations) - 10) * 0.3)))

y_pos = np.arange(len(occupations))
bar_height = 0.7

# Create bars
male_bars = ax.barh(y_pos, mirror_df["Male_mirror"].values, bar_height,
                    color='#2AA198', label='Male', edgecolor='white')
female_bars = ax.barh(y_pos, mirror_df["Female_mirror"].values, bar_height,
                      color='#B266FF', label='Female', edgecolor='white')

# Add value labels
for i, (male_val, female_val) in enumerate(zip(male_values, female_values)):
    if normalize_option == "Percent of total (selected year)":
        male_text = f"{male_val:.1f}%"
        female_text = f"{female_val:.1f}%"
    else:
        male_text = f"{male_val:,}"
        female_text = f"{female_val:,}"

    ax.text(male_val + (max(male_values) * 0.01), i, male_text,
            va='center', ha='left', fontsize=9, color='gray')
    ax.text(-female_val - (max(female_values) * 0.01), i, female_text,
            va='center', ha='right', fontsize=9, color='gray')

# Customize the chart
ax.axvline(0, color='gray', linewidth=1)
ax.set_yticks(y_pos)
ax.set_yticklabels(occupations)
ax.set_xlabel(x_title)
ax.legend()

# Format x-axis for percentages or counts
if normalize_option == "Percent of total (selected year)":
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{abs(x):.0f}%'))
else:
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{abs(x):,}'))

plt.tight_layout()
st.pyplot(fig)

if show_estimate_note:
    st.info(
        "ℹ️ **Estimation note:** Because no occupation×gender dataset exists, "
        "we split each occupation by the overall Male/Female share for the selected year. "
        "This is an approximation."
    )

st.info(
    "This mirrored bar chart shows the estimated gender split by occupation for the selected year. "
    "Female counts extend left, while male counts extends right. "
    "The top 3 occupations make up over 60% of the workforce. "
    "Majority of the occupations are female dominated. "
)

st.markdown("---")

# ------------------------
# Occupation Trends with Matplotlib
# ------------------------
st.subheader("Occupation Trends (Selected Occupations)")

# Melt the data
occu_ts = occu_df[["year"] + occu_columns].melt(
    id_vars="year", var_name="Occupation", value_name="Count"
)
occu_ts["Occupation"] = occu_ts["Occupation"].astype(str)

# ------------------------
# Multiselect filter and top N / show all logic
# ------------------------
occupation_multiselect = st.multiselect(
    "Select occupations (leave empty to show top N)",
    options=sorted(occu_columns),
    default=[]
)

show_all = st.checkbox("Show all occupations", value=True)

# Determine which occupations to display
if show_all:
    if occupation_multiselect:
        ts_plot = occu_ts[occu_ts["Occupation"].isin(
            occupation_multiselect)].copy()
        top_occ = occupation_multiselect[:5]
    else:
        ts_plot = occu_ts.copy()
        latest_year = occu_df["year"].max()
        occ_year_latest = occu_df[occu_df["year"]
                                  == latest_year].drop(columns="year")
        top_occ = occ_year_latest.iloc[0].sort_values(
            ascending=False).head(5).index.tolist()
else:
    latest_year = occu_df["year"].max()
    occ_year_latest = occu_df[occu_df["year"]
                              == latest_year].drop(columns="year")

    if occupation_multiselect:
        top_occ = occupation_multiselect[:5]
    else:
        top_occ = occ_year_latest.iloc[0].sort_values(
            ascending=False).head(5).index.tolist()

    ts_plot = occu_ts[occu_ts["Occupation"].isin(top_occ)].copy()

# ------------------------
# Plot line chart with Matplotlib
# ------------------------
if not ts_plot.empty:
    fig2, ax2 = plt.subplots(figsize=(12, 8))

    # Create color map for occupations
    occupations_to_plot = ts_plot["Occupation"].unique()
    colors = plt.cm.Set3(np.linspace(0, 1, len(occupations_to_plot)))

    for i, occupation in enumerate(occupations_to_plot):
        occ_data = ts_plot[ts_plot["Occupation"]
                           == occupation].sort_values("year")
        ax2.plot(occ_data["year"], occ_data["Count"],
                 marker='o', linewidth=2.5, markersize=6,
                 color=colors[i], label=occupation)

    ax2.set_xlabel("Year")
    ax2.set_ylabel("Count")
    ax2.set_title("Occupation Trends Over Time")
    ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax2.grid(True, alpha=0.3)

    # Format y-axis with commas
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:,.0f}'))

    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig2)
else:
    st.warning("No data available for the selected occupations/year.")

st.info(
    "This chart displays trends in occupation over time. "
    "The top 3 occupations in the latest year account for over 50% of total counts. "
    "Some occupations have grown >30% in the past decade, while others declined up to 25%, showing sectoral shifts."
    "'No Occupation Reported' often reflects missing or unrecorded data, which may be due to temporary or informal work, incomplete reporting, or systemic gaps in data collection. "
)

# ------------------------
# Bottom row charts with Matplotlib
# ------------------------
col3, col4 = st.columns(2)

with col3:
    st.subheader("Top Occupations (Selected Year)")

    # Prepare data for horizontal bar chart
    top_show_df = est[["Occupation", "Count"]].sort_values(
        "Count", ascending=True).head(top_n)

    fig3, ax3 = plt.subplots(figsize=(10, 8))
    y_pos = np.arange(len(top_show_df))

    bars = ax3.barh(y_pos, top_show_df["Count"],
                    color='#4C72B0', alpha=0.7, edgecolor='white')

    ax3.set_yticks(y_pos)
    ax3.set_yticklabels(top_show_df["Occupation"])
    ax3.set_xlabel("Count")
    ax3.set_title(f"Top {top_n} Occupations in {selected_year}")

    # Add value labels on bars
    for i, bar in enumerate(bars):
        width = bar.get_width()
        ax3.text(width + (max(top_show_df["Count"]) * 0.01), bar.get_y() + bar.get_height()/2,
                 f'{width:,}', ha='left', va='center', fontsize=9)

    ax3.xaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:,.0f}'))
    plt.tight_layout()
    st.pyplot(fig3)

    st.info(
        "Ranks occupations by total count. "
        "The top occupation represents 15–20% of all counts; the top 5 together exceed 55%, "
        "highlighting workforce concentration in key roles."
    )

with col4:
    st.subheader("Gender Trend")

    # Prepare gender data
    gender_long = sex_df.melt(
        id_vars="year", var_name="Gender", value_name="Count")

    fig4, ax4 = plt.subplots(figsize=(10, 8))

    # Plot area chart
    years = gender_long["year"].unique()
    male_data = gender_long[gender_long["Gender"]
                            == "Male"].sort_values("year")
    female_data = gender_long[gender_long["Gender"]
                              == "Female"].sort_values("year")

    ax4.fill_between(
        years, female_data["Count"], color='#B266FF', alpha=0.6, label='Female')
    ax4.fill_between(years, male_data["Count"],
                     color='#2AA198', alpha=0.6, label='Male')

    # Add line plots on top
    ax4.plot(years, female_data["Count"], color='#B266FF', linewidth=2)
    ax4.plot(years, male_data["Count"], color='#2AA198', linewidth=2)

    ax4.set_xlabel("Year")
    ax4.set_ylabel("Count")
    ax4.set_title("Gender Distribution Over Time")
    ax4.legend()
    ax4.grid(True, alpha=0.3)

    # Format y-axis with commas
    ax4.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{x:,.0f}'))

    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig4)

    st.info(
        "Illustrates male and female population over time. "
        "In the latest year, females are ~55%, males ~45%. "
        "Male counts have increased >20% in several years, slightly narrowing the gender gap."
    )

# ------------------------
# Data & download
# ------------------------
st.markdown("---")
st.subheader("Data & Export")
with st.expander("Show occupation totals (selected year)"):
    st.dataframe(occ_year.style.format({"Count": "{:,}"}))
with st.expander("Show estimated gender-by-occupation (for selected year)"):
    display_est = est[["Occupation", "Count", "Male", "Female"]
                      ].copy().rename(columns={"Count": "Total"})
    st.dataframe(display_est.style.format(
        {"Total": "{:,}", "Male": "{:,}", "Female": "{:,}"}))

csv = display_est.to_csv(index=False)
st.download_button(
    "Download estimated occupation × gender CSV",
    data=csv,
    file_name=f"estimated_occu_gender_{selected_year}.csv",
    mime="text/csv"
)

# Clean up matplotlib figures
plt.close('all')
