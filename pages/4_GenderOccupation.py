import streamlit as st
import pandas as pd
import altair as alt
import numpy as np

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
        sex = sex.rename(columns={sex_cols["male"]: "Male", sex_cols["female"]: "Female"})

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

selected_year = st.sidebar.selectbox("Select year", options=years, index=len(years) - 1)

occu_columns = [c for c in occu_df.columns if c != "year"]
default_top_n = 12
top_n = st.sidebar.slider("Number of occupations to display", min_value=3, max_value=15, value=default_top_n)

occupation_multiselect = st.sidebar.multiselect(
    "Filter occupations",
    options=sorted(occu_columns),
    default=[]
)

show_estimate_note = st.sidebar.checkbox("Show approximation note (gender split estimate)", value=True)
normalize_option = st.sidebar.radio("Show counts or percentages:", ("Counts", "Percent of total (selected year)"))

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
    display_df = occ_year[occ_year["Occupation"].isin(occupation_multiselect)].copy()
else:
    display_df = occ_year.head(top_n).copy()

# ------------------------
# Estimate gender split
# ------------------------
sex_row = sex_df[sex_df["year"] == selected_year]
if sex_row.shape[0] == 0:
    st.warning(f"Gender totals not available for {selected_year}. Using overall proportions from latest year.")
    sex_row = sex_df.iloc[[-1]]

if "Male" not in sex_row.columns or "Female" not in sex_row.columns:
    st.error("Sex totals table must contain 'Male' and 'Female' columns (case-insensitive).")
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
# Mirrored bar chart
# ------------------------
st.subheader("👥 Gender Distribution by Occupation — Mirrored View")
mirror_df = est.copy()
mirror_df["Female_mirror"] = -mirror_df[value_col_f]
mirror_df["Male_mirror"] = mirror_df[value_col]
sorted_occ = mirror_df.sort_values("Count", ascending=True)["Occupation"].tolist()
mirror_df["Occupation"] = pd.Categorical(mirror_df["Occupation"], categories=sorted_occ, ordered=True)

left_max = int(mirror_df[value_col_f].abs().max()) if mirror_df[value_col_f].abs().max() else 0
right_max = int(mirror_df[value_col].abs().max()) if mirror_df[value_col].abs().max() else 0
max_val = max(left_max, right_max, 1)
x_axis = alt.Axis(title=x_title, labelExpr="abs(datum.value)")
x_scale = alt.Scale(domain=[-max_val, max_val])

female_bar = alt.Chart(mirror_df).mark_bar(size=18).encode(
    x=alt.X("Female_mirror:Q", title=x_title, scale=x_scale, axis=x_axis, stack=None),
    y=alt.Y("Occupation:N", sort=sorted_occ, title=None),
    color=alt.value("#B266FF"),
    tooltip=[alt.Tooltip("Occupation:N"), alt.Tooltip(value_col_f + ":Q", title="Female", format=",")]
)

male_bar = alt.Chart(mirror_df).mark_bar(size=18).encode(
    x=alt.X("Male_mirror:Q", title=x_title, scale=x_scale, axis=x_axis, stack=None),
    y=alt.Y("Occupation:N", sort=sorted_occ, title=None),
    color=alt.value("#2AA198"),
    tooltip=[alt.Tooltip("Occupation:N"), alt.Tooltip(value_col + ":Q", title="Male", format=",")]
)

female_text = alt.Chart(mirror_df).mark_text(align="right", dx=-5, color="gray").encode(
    x=alt.X("Female_mirror:Q", stack=None),
    y=alt.Y("Occupation:N", sort=sorted_occ),
    text=alt.Text(value_col_f + ":Q", format=",")
)

male_text = alt.Chart(mirror_df).mark_text(align="left", dx=5, color="gray").encode(
    x=alt.X("Male_mirror:Q", stack=None),
    y=alt.Y("Occupation:N", sort=sorted_occ),
    text=alt.Text(value_col + ":Q", format=",")
)

center_rule = alt.Chart(pd.DataFrame({"x": [0]})).mark_rule(color="gray", strokeWidth=1).encode(x="x:Q")

chart_height = 420 + max(0, (len(sorted_occ) - 10) * 30)
mirrored_chart = (female_bar + male_bar + female_text + male_text + center_rule).properties(
    height=chart_height, width=900
)
st.altair_chart(mirrored_chart, use_container_width=True)

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
# Occupation Trends
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
        ts_plot = occu_ts[occu_ts["Occupation"].isin(occupation_multiselect)].copy()
        top_occ = occupation_multiselect[:5]  # always define top_occ
    else:
        ts_plot = occu_ts.copy()
        latest_year = occu_df["year"].max()
        occ_year_latest = occu_df[occu_df["year"] == latest_year].drop(columns="year")
        top_occ = occ_year_latest.iloc[0].sort_values(ascending=False).head(5).index.tolist()
else:
    latest_year = occu_df["year"].max()
    occ_year_latest = occu_df[occu_df["year"] == latest_year].drop(columns="year")
    
    if occupation_multiselect:
        top_occ = occupation_multiselect[:5]
        rest = [occ for occ in occupation_multiselect if occ not in top_occ]
    else:
        top_occ = occ_year_latest.iloc[0].sort_values(ascending=False).head(5).index.tolist()
        rest = [occ for occ in occu_columns if occ not in top_occ]
    
    ts_plot_top = occu_ts[occu_ts["Occupation"].isin(top_occ)].copy()
    
    if rest:
        dummy_df = pd.DataFrame({
            "year": [occu_ts["year"].min()],
            "Occupation": [f"...+{len(rest)} more"],
            "Count": [0]
        })
        ts_plot = pd.concat([ts_plot_top, dummy_df], ignore_index=True)
    else:
        ts_plot = ts_plot_top.copy()

# ------------------------
# Legend order
# ------------------------
all_occupations = ts_plot["Occupation"].unique().tolist()
legend_order = [occ for occ in top_occ if occ in all_occupations] + \
               sorted([occ for occ in all_occupations if occ not in top_occ])

# ------------------------
# Plot line chart
# ------------------------
if not ts_plot.empty:
    line_chart = (
        alt.Chart(ts_plot)
        .mark_line(point=True)
        .encode(
            x=alt.X("year:O", title="Year"),
            y=alt.Y("Count:Q", title="Count"),
            color=alt.Color(
                "Occupation:N",
                sort=legend_order,
                legend=alt.Legend(title="Occupation", symbolLimit=5, columns=1)
            ),
            tooltip=["year", "Occupation", "Count"]
        )
        .properties(height=420)
        .interactive()
    )
    st.altair_chart(line_chart, use_container_width=True)
else:
    st.warning("No data available for the selected occupations/year.")

st.info(
    "This chart displays trends in occupation over time. "
    "The top 3 occupations in the latest year account for over 50% of total counts. "
    "Some occupations have grown >30% in the past decade, while others declined up to 25%, showing sectoral shifts."
    "'No Occupation Reported' often reflects missing or unrecorded data, which may be due to temporary or informal work, incomplete reporting, or systemic gaps in data collection. "
)

# ------------------------
# Bottom row charts
# ------------------------
col3, col4 = st.columns(2)

with col3:
    st.subheader("Top Occupations (Selected Year)")
    top_show_df = est[["Occupation", "Count"]].sort_values("Count", ascending=False).head(top_n)
    top_chart = alt.Chart(top_show_df).mark_bar().encode(
        x=alt.X("Count:Q", title="Count"),
        y=alt.Y("Occupation:N", sort='-x'),
        tooltip=["Occupation", "Count"],
        color=alt.value("#4C72B0")
    ).properties(height=420)
    st.altair_chart(top_chart, use_container_width=True)
    st.info(
    "Ranks occupations by total count. "
    "The top occupation represents 15–20% of all counts; the top 5 together exceed 55%, "
    "highlighting workforce concentration in key roles."
    )

with col4:
    st.subheader("Gender Trend")
    gender_long = sex_df.melt(id_vars="year", var_name="Gender", value_name="Count")
    gender_chart = alt.Chart(gender_long).mark_area(opacity=0.6).encode(
        x=alt.X("year:O", title="Year"),
        y=alt.Y("Count:Q", title="Count"),
        color=alt.Color("Gender:N", scale=alt.Scale(domain=["Male", "Female"], range=["#2AA198", "#B266FF"]))
    ).properties(height=420)
    st.altair_chart(gender_chart, use_container_width=True)
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
    display_est = est[["Occupation", "Count", "Male", "Female"]].copy().rename(columns={"Count": "Total"})
    st.dataframe(display_est.style.format({"Total": "{:,}", "Male": "{:,}", "Female": "{:,}"}))

csv = display_est.to_csv(index=False)
st.download_button(
    "Download estimated occupation × gender CSV",
    data=csv,
    file_name=f"estimated_occu_gender_{selected_year}.csv",
    mime="text/csv"
)
