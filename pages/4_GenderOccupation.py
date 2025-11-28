import streamlit as st
import pandas as pd
import altair as alt
import numpy as np


# Page meta + styling

st.set_page_config(page_title="Gender & Occupation", layout="wide")
st.title("Gender & Occupation — Distribution & Trends")
st.markdown(
    "This page shows occupation counts and gender splits using data from CFO."
)


# Load data

@st.cache_data
def load_data():
    base = "data"
    occu = pd.read_csv(f"{base}/occu_pivot.csv")
    sex = pd.read_csv(f"{base}/sex_pivot.csv")
    # Clean occupation column names: replace underscores and fix casing
    occu_cols = list(occu.columns)
    # create mapping for nicer labels
    col_map = {}
    for c in occu.columns:
        if c == "year":
            col_map[c] = c
        else:
            nicer = c.replace("_", " ").replace("&", "and")
            nicer = " ".join([w.capitalize() for w in nicer.split()])
            col_map[c] = nicer
    occu = occu.rename(columns=col_map)

    # Normalize sex column names to 'Male' and 'Female' if possible
    sex_cols = {c.lower(): c for c in sex.columns}
    if "male" in sex_cols and "female" in sex_cols:
        sex = sex.rename(columns={sex_cols["male"]: "Male", sex_cols["female"]: "Female"})
    else:
        # If exactly "Male" and "Female" already present, keep them.
        pass

    return occu, sex

occu_df, sex_df = load_data()


# Sidebar filters & controls

st.sidebar.header("Filters & Options")

years = sorted(occu_df["year"].unique())
if len(years) == 0:
    st.error("No years found in occupation dataset.")
    st.stop()

selected_year = st.sidebar.selectbox("Select year", options=years, index=len(years) - 1)

# Get a list of occupation columns (all except 'year')
occu_columns = [c for c in occu_df.columns if c != "year"]
default_top_n = 12
top_n = st.sidebar.slider("Number of occupations to display", min_value=6, max_value=30, value=default_top_n)

occupation_multiselect = st.sidebar.multiselect(
    "Filter occupations (optional - if empty uses top N by total)",
    options=sorted(occu_columns),
    default=[]
)

show_estimate_note = st.sidebar.checkbox("Show approximation note (gender split estimate)", value=True)
normalize_option = st.sidebar.radio("Show counts or percentages:", ("Counts", "Percent of total (selected year)"))

st.sidebar.markdown("---")
st.sidebar.write("Design note: Mirrored bar chart is an *estimated* gender split derived by applying the overall male/female shares for the selected year to each occupation.")


# Prepare data for the selected year

row = occu_df[occu_df["year"] == selected_year]
if row.shape[0] == 0:
    st.error(f"No occupation data available for year {selected_year}")
    st.stop()

# transpose to have occupation names and counts
occ_year = row.drop(columns="year").T.reset_index()
occ_year.columns = ["Occupation", "Count"]
# sort by Count descending
occ_year = occ_year.sort_values("Count", ascending=False)

# apply occupation filter or top-N
if occupation_multiselect:
    display_df = occ_year[occ_year["Occupation"].isin(occupation_multiselect)].copy()
else:
    display_df = occ_year.head(top_n).copy()


# Estimate gender split per occupation (approximation)

sex_row = sex_df[sex_df["year"] == selected_year]
if sex_row.shape[0] == 0:
    st.warning(f"Gender totals not available for {selected_year}. Using overall proportions from latest year.")
    sex_row = sex_df.iloc[[-1]]

# Make sure Male and Female exist and are numeric
if "Male" not in sex_row.columns or "Female" not in sex_row.columns:
    st.error("Sex totals table must contain 'Male' and 'Female' columns (case-insensitive).")
    st.stop()

male_total = int(sex_row["Male"].values[0])
female_total = int(sex_row["Female"].values[0])
total_people = male_total + female_total
male_share = male_total / total_people if total_people else 0.5
female_share = female_total / total_people if total_people else 0.5

# Create estimated male/female counts per occupation
est = display_df.copy()
est["Male"] = (est["Count"] * male_share).round().astype(int)
est["Female"] = (est["Count"] * female_share).round().astype(int)

# If user asked percentages, compute percent-of-total per occupation
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


# Mirrored bar chart

st.subheader("👥 Gender Distribution by Occupation — Mirrored View")

st.markdown(
    "Female bars (purple) appear on the **left**, and Male bars (teal) appear on the **right**. "
    "Axis labels show positive values only for easier reading."
)

# Prepare mirrored data
mirror_df = est.copy()
mirror_df["Female_mirror"] = -mirror_df[value_col_f]   # internal negative — left side
mirror_df["Male_mirror"] = mirror_df[value_col]        # positive — right side

# Convert occupation list to ordered categorical for correct sorting (descending by count)
sorted_occ = mirror_df.sort_values("Count", ascending=True)["Occupation"].tolist()
mirror_df["Occupation"] = pd.Categorical(mirror_df["Occupation"], categories=sorted_occ, ordered=True)

# Axis max for both sides (use absolute max of actual value columns)
# handle pct vs counts smoothly by filling zeros if needed
left_max = int(mirror_df[value_col_f].abs().max()) if mirror_df[value_col_f].abs().max() is not None else 0
right_max = int(mirror_df[value_col].abs().max()) if mirror_df[value_col].abs().max() is not None else 0
max_val = max(left_max, right_max, 1)

# Force positive labels on x-axis using labelExpr
x_axis = alt.Axis(
    title=x_title,
    labelExpr="abs(datum.value)"
)

x_scale = alt.Scale(domain=[-max_val, max_val])

# Female bar layer (left)
female_bar = (
    alt.Chart(mirror_df)
    .mark_bar(size=18)
    .encode(
        x=alt.X("Female_mirror:Q", title=x_title, scale=x_scale, axis=x_axis, stack=None),
        y=alt.Y("Occupation:N", sort=sorted_occ, title=None),
        color=alt.value("#B266FF"),
        tooltip=[
            alt.Tooltip("Occupation:N"),
            alt.Tooltip(value_col_f + ":Q", title="Female", format=","),
        ],
    )
)

# Male bar layer (right)
male_bar = (
    alt.Chart(mirror_df)
    .mark_bar(size=18)
    .encode(
        x=alt.X("Male_mirror:Q", title=x_title, scale=x_scale, axis=x_axis, stack=None),
        y=alt.Y("Occupation:N", sort=sorted_occ, title=None),
        color=alt.value("#2AA198"),
        tooltip=[
            alt.Tooltip("Occupation:N"),
            alt.Tooltip(value_col + ":Q", title="Male", format=","),
        ],
    )
)

# Female text labels (positive values only)
female_text = (
    alt.Chart(mirror_df)
    .mark_text(align="right", dx=-5, color="gray")
    .encode(
        x=alt.X("Female_mirror:Q", stack=None),
        y=alt.Y("Occupation:N", sort=sorted_occ),
        text=alt.Text(value_col_f + ":Q", format=","),
    )
)

# Male text labels
male_text = (
    alt.Chart(mirror_df)
    .mark_text(align="left", dx=5, color="gray")
    .encode(
        x=alt.X("Male_mirror:Q", stack=None),
        y=alt.Y("Occupation:N", sort=sorted_occ),
        text=alt.Text(value_col + ":Q", format=","),
    )
)

# Center vertical zero line
center_rule = (
    alt.Chart(pd.DataFrame({"x": [0]}))
    .mark_rule(color="gray", strokeWidth=1)
    .encode(x="x:Q")
)

# Combine all layers
mirrored_chart = (female_bar + male_bar + female_text + male_text + center_rule).properties(
    height=40 * len(sorted_occ), width=900
)

st.altair_chart(mirrored_chart, use_container_width=True)

if show_estimate_note:
    st.info(
        "ℹ️ **Estimation note:** Because no occupation×gender dataset exists, "
        "we split each occupation by the overall Male/Female share for the selected year. "
        "This is an approximation."
    )

st.info(
    
    "This mirrored bar chart shows the estimated male and female distribution across occupations. "
    "Female counts extend to the left and male counts to the right. The x-axis displays only positive values for easier interpretation."
)


# Two-column detailed section:
# left = Occupation trends (small multiples)
# right = Gender trend & Top occupations

st.markdown("---")
col1, col2 = st.columns((2, 1))

with col1:
    st.subheader("Occupation Trends (Selected occupations)")
    # prepare time-series for selected occupations (all years)
    occu_ts = occu_df[["year"] + occu_columns].melt(id_vars="year", var_name="Occupation", value_name="Count")
    # Make labels tidy (matching the renaming earlier)
    occu_ts["Occupation"] = occu_ts["Occupation"].astype(str)
    # If user selected particular occupations, filter; else use top N occupations overall
    if occupation_multiselect:
        ts_filter = occupation_multiselect
    else:
        ts_filter = occ_year.head(top_n)["Occupation"].tolist()

    ts_plot = occu_ts[occu_ts["Occupation"].isin(ts_filter)]

    line = alt.Chart(ts_plot).mark_line(point=True).encode(
        x=alt.X("year:O", title="Year"),
        y=alt.Y("Count:Q", title="Count"),
        color=alt.Color("Occupation:N", legend=alt.Legend(columns=2)),
        tooltip=["year", "Occupation", "Count"]
    ).properties(height=420)

    st.altair_chart(line, use_container_width=True)

    st.info(
        
        "This line chart presents occupation trends over time. Each line represents one of the selected occupations, "
        "showing how counts change year-by-year."
    )

with col2:
    st.subheader("Gender Trend & Top Occupations")
    # Gender overall trend chart
    # Ensure gender columns are 'Male' and 'Female' for melt
    gender_long = sex_df.melt(id_vars="year", var_name="Gender", value_name="Count")
    gender_chart = alt.Chart(gender_long).mark_area(opacity=0.6).encode(
        x=alt.X("year:O", title="Year"),
        y=alt.Y("Count:Q", title="Count"),
        color=alt.Color("Gender:N", scale=alt.Scale(domain=["Male", "Female"], range=["#2AA198", "#B266FF"]))
    ).properties(height=220)
    st.altair_chart(gender_chart, use_container_width=True)

    st.info(
     
        "The gender trend chart illustrates the overall male and female population across years, showing shifts in gender composition."
    )

    st.write("Top occupations (selected year)")
    top_show_df = est[["Occupation", "Count"]].sort_values("Count", ascending=False).head(top_n)
    # Simple bar chart
    top_chart = alt.Chart(top_show_df).mark_bar().encode(
        x=alt.X("Count:Q", title="Count"),
        y=alt.Y("Occupation:N", sort='-x'),
        tooltip=["Occupation", "Count"],
        color=alt.value("#4C72B0")
    ).properties(height=240)
    st.altair_chart(top_chart, use_container_width=True)

    st.info(
        
        "This bar chart ranks the top occupations in the selected year based on total count. Higher bars indicate greater representation."
    )


# Show data and download

st.markdown("---")
st.subheader("Data & Export")

with st.expander("Show occupation totals (selected year)"):
    st.dataframe(occ_year.style.format({"Count": "{:,}"}))

with st.expander("Show estimated gender-by-occupation (for selected year)"):
    display_est = est[["Occupation", "Count", "Male", "Female"]].copy()
    display_est = display_est.rename(columns={"Count": "Total"})
    st.dataframe(display_est.style.format({"Total": "{:,}", "Male": "{:,}", "Female": "{:,}"}))

# Provide CSV download link for the estimated breakdown
csv = display_est.to_csv(index=False)
st.download_button("Download estimated occupation × gender CSV", data=csv, file_name=f"estimated_occu_gender_{selected_year}.csv", mime="text/csv")
