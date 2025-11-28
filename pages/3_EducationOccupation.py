# pages/3_EducationOccupation.py
import streamlit as st
from educ_occ_heatmap import (
    get_heatmaps,
    available_years,
    load_data,
    melt_education,
    melt_occupation,
    estimate_joint
)

st.set_page_config(page_title="Education & Occupation", layout="wide")

# === Keep title exactly as requested ===
st.title("Filipino Emigrants' Proportional Distribution by Educational Attainment * Occupation")
st.markdown("""This dashboard shows proportional estimates of how Filipino emigrants distribute
across Educational Attainment and Occupation for the selected year.
These insights help the Commission on Filipinos Overseas (CFO) understand patterns
in skill mobility, employment alignment, and migrant vulnerabilities.""")

# --- load years safely ---
try:
    years = available_years()
    if not years:
        st.error("No valid years found in data/merged_data.csv")
        st.stop()
    min_year = min(years)
    max_year = max(years)
except Exception as e:
    st.error(f"Error reading data: {e}")
    st.stop()

# Year slider constrained to available years
year = st.slider("Select Year", min_value=int(min_year), max_value=int(max_year), value=int(max_year))

# Fetch heatmaps (these are Bokeh figures returned from your working module)
top_plot, bottom_plot, top_joint_hm, bottom_joint_hm = get_heatmaps(year)


# If both are None -> likely no data for selected year
if top_plot is None and bottom_plot is None:
    st.warning(f"No data available for year {year}.")
    st.stop()

# === Compute total emigrants for the selected year (for narrative context) ===
df = load_data()
df_year = df[df["year"] == int(year)]
if df_year.empty:
    total_emigrants_year = 0
else:
    # sum all numeric columns except 'year' to produce an aggregated count for the year
    numeric = df_year.select_dtypes(include="number").drop(columns=["year"], errors="ignore")
    total_emigrants_year = int(numeric.sum(axis=1).sum())

st.info(f"**Total emigrants in {year}: {total_emigrants_year:,} (aggregated PSA counts)**")

# === Prepare joint DataFrames (re-use your module's melt & estimate functions) ===
# Melt the year-specific data
educ_df = melt_education(df_year)
occ_df = melt_occupation(df_year)

# Defensive: if either melted df is empty, we won't try to compute narratives
if educ_df.empty or occ_df.empty:
    st.warning("Melted education or occupation data are empty for this year; narratives are unavailable.")
    # Still show whatever plots exist (if any)
else:
    # compute totals and determine top/bottom 10 educational attainment categories
    educ_totals = educ_df.groupby("Educational_Attainment", as_index=False)["Education_Count"].sum()
    educ_totals = educ_totals.sort_values("Education_Count", ascending=False)

    top10 = educ_totals.head(10)["Educational_Attainment"].tolist()
    bottom10 = educ_totals.tail(10)["Educational_Attainment"].tolist()

    # create joint frames for narrative extraction (same method you used to build the heatmaps)
    top_joint = estimate_joint(educ_df[educ_df["Educational_Attainment"].isin(top10)].reset_index(drop=True), occ_df)
    bottom_joint = estimate_joint(educ_df[educ_df["Educational_Attainment"].isin(bottom10)].reset_index(drop=True), occ_df)

    # helper to pick the strongest cell and format explanation
    def get_strongest(joint_df):
        if joint_df is None or joint_df.empty:
            return None
        row = joint_df.loc[joint_df["Percent"].idxmax()]
        educ = row["Educational_Attainment"]
        occ = row["Occupation"]
        pct = float(row["Percent"])
        return educ, occ, pct

    def pct_explain(pct, total_emigrants):
        """Return a one-line explanation: pct is percent of all emigrants, and approximate count."""
        if total_emigrants and pct > 0:
            approx_count = int(round((pct / 100.0) * total_emigrants))
            return f"{pct:.2f}% of all emigrants (~{approx_count:,} persons)"
        else:
            return f"{pct:.2f}% of all emigrants"

# --- TOP 10 section (layout unchanged) ---
st.subheader("Top 10 Educational Attainment * Occupation")
if top_plot is not None:
    st.bokeh_chart(top_plot, use_container_width=True)
else:
    st.info("Top 10 heatmap not available for this year.")

# Narrative for top
if not educ_df.empty and not occ_df.empty:
    strongest = get_strongest(top_joint)
    if strongest:
        educ, occ, pct = strongest
        st.markdown(
            f"### 📘 Key Insight — Top Group ({year})\n\n"
            f"The strongest proportional Education × Occupation combination among the **Top 10 education levels** is:\n\n"
            f"**➡ {educ.replace('_',' ').title()} → {occ.replace('_',' ').title()}**  \n"
            f"**➡ {pct_explain(pct, total_emigrants_year)}**\n\n"
            "**Interpretation:** this cell indicates the relative share (proportional estimate) of the entire emigrant population\n"
            f"belonging to the selected year that falls into this education × occupation pairing. Higher percentages (darker cells) show\n"
            "stronger concentration for that education group into the indicated occupation."
        )
    else:
        st.info("No dominant cell found for Top 10 (possible zero totals).")

st.write("---")

# --- BOTTOM 10 section ---
st.subheader("Bottom 10 Educational Attainment * Occupation")
if bottom_plot is not None:
    st.bokeh_chart(bottom_plot, use_container_width=True)
else:
    st.info("Bottom 10 heatmap not available for this year.")

# Narrative for bottom
if not educ_df.empty and not occ_df.empty:
    strongest_b = get_strongest(bottom_joint)
    if strongest_b:
        educ_b, occ_b, pct_b = strongest_b
        st.markdown(
            f"### 📙 Key Insight — Bottom Group ({year})\n\n"
            f"The strongest proportional Education × Occupation combination among the **Bottom 10 education levels** is:\n\n"
            f"**➡ {educ_b.replace('_',' ').title()} → {occ_b.replace('_',' ').title()}**  \n"
            f"**➡ {pct_explain(pct_b, total_emigrants_year)}**\n\n"
            "**Interpretation:** Although these education levels are smaller contributors to total emigrants,\n"
            "the heatmap reveals which occupation pathways are relatively more represented within these groups."
        )
    else:
        st.info("No dominant cell found for Bottom 10 (possible zero totals).")

st.markdown("---")

# --- CFO Policy Interpretation (kept and slightly contextualized) ---
st.subheader("🏛 Policy Interpretation for CFO")
st.write(
    f"These Education × Occupation proportional patterns (for {year}) provide CFO with quick signals:\n\n"
    "- **Monitoring Skill Flow:** If highly educated groups concentrate in certain occupations (e.g., nurses, IT), CFO can anticipate domestic skill gaps.\n\n"
    "- **Identifying Underemployment Abroad:** A notable share of high-education migrants in lower-skilled occupations can imply credential recognition issues.\n\n"
    "- **Targeted Support:** The bottom-10 heatmap helps identify vulnerable groups (minors, out-of-school youth, or 'no reported education') for targeted interventions.\n\n"
    "- **Program & Policy Use:** Use the per-year proportional heatmaps together with total emigrant counts (shown above) to size interventions — for example, a 5% cell in a year of 200k emigrants (~10k people) is operationally meaningful.\n\n"
    "The visualizations and narratives update automatically when you change the year, enabling evidence-based policy discussions."
)
