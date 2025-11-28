# educ_occ_heatmap.py
import math
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# ------------------------
# Load dataset
# ------------------------


def load_data(path="data/merged_data.csv"):
    df = pd.read_csv(path)
    if "year" in df.columns:
        df["year"] = pd.to_numeric(
            df["year"], errors="coerce").fillna(0).astype(int)
    else:
        raise ValueError("merged_data.csv is missing required column 'year'")
    # replace other missing with 0 (aggregated counts)
    df = df.fillna(0)
    return df

# ------------------------
# Available years
# ------------------------


def available_years(data_path="data/merged_data.csv"):
    df = load_data(data_path)
    years = sorted(df["year"].unique().tolist())
    return [y for y in years if y != 0]


# ------------------------
# Column lists (update if your column names differ)
# ------------------------
EDUCATION_COLS = [
    "college_graduate", "college_level",
    "elementary_graduate", "elementary_level",
    "high_school_graduate", "high_school_level",
    "no_formal_education", "non-formal_education",
    "not_reported_/_no_response", "not_of_schooling_age",
    "post_graduate", "post_graduate_level",
    "vocational_graduate", "vocational_level"
]

OCCUPATION_COLS = [
    "administrative_workers", "clerical_workers",
    "equipment_operators,_&_laborers", "housewives",
    "members_of_the_armed_forces", "minors_(below_7_years_old)",
    "no_occupation_reported", "out_of_school_youth",
    "prof'l,_tech'l,_&_related_workers", "refugees",
    "retirees", "sales_workers", "service_workers",
    "students", "workers_&_fishermen"
]

# ------------------------
# Melt helpers
# ------------------------


def melt_education(df_year):
    available = [c for c in EDUCATION_COLS if c in df_year.columns]
    if not available:
        return pd.DataFrame(columns=["year", "Educational_Attainment", "Education_Count"])
    return df_year.melt(
        id_vars="year",
        value_vars=available,
        var_name="Educational_Attainment",
        value_name="Education_Count"
    )


def melt_occupation(df_year):
    available = [c for c in OCCUPATION_COLS if c in df_year.columns]
    if not available:
        return pd.DataFrame(columns=["year", "Occupation", "Occupation_Count"])
    return df_year.melt(
        id_vars="year",
        value_vars=available,
        var_name="Occupation",
        value_name="Occupation_Count"
    )

# ------------------------
# Joint proportional distribution (Option C)
# ------------------------


def estimate_joint(educ_df, occ_df):
    # if either empty -> None
    if educ_df is None or occ_df is None or educ_df.empty or occ_df.empty:
        return None

    total_educ = educ_df["Education_Count"].sum()
    total_occ = occ_df["Occupation_Count"].sum()
    if total_educ == 0 or total_occ == 0:
        return None

    # cross join (proportional estimate)
    ed = educ_df.copy()
    oc = occ_df.copy()
    ed["key"] = 1
    oc["key"] = 1
    joint = ed.merge(oc, on=["year", "key"]).drop(columns=["key"])

    joint["educ_prop"] = joint["Education_Count"] / total_educ
    joint["occ_prop"] = joint["Occupation_Count"] / total_occ
    joint["Percent"] = (joint["educ_prop"] * joint["occ_prop"]) * 100.0
    joint["Percent"] = joint["Percent"].fillna(0.0)

    joint = joint[[
        "year", "Educational_Attainment", "Education_Count",
        "Occupation", "Occupation_Count", "Percent"
    ]]

    return joint

# ------------------------
# Build a single heatmap (Matplotlib/Seaborn figure)
# ------------------------


def build_heatmap(joint_df, title, x_order=None, y_order=None):
    if joint_df is None or joint_df.empty:
        return None

    # x categories (occupations) - alphabetical or provided order
    if x_order is None:
        x_cats = sorted(joint_df["Occupation"].unique())
    else:
        x_cats = [x for x in x_order if x in joint_df["Occupation"].unique()]

    # y categories (education) - preserve provided order or reverse alphabetical
    if y_order is None:
        y_cats = sorted(
            joint_df["Educational_Attainment"].unique(), reverse=True)
    else:
        y_cats = [
            y for y in y_order if y in joint_df["Educational_Attainment"].unique()]

    # Create pivot table for heatmap
    pivot_data = joint_df.pivot_table(
        index="Educational_Attainment",
        columns="Occupation",
        values="Percent",
        aggfunc='first'
    ).reindex(index=y_cats, columns=x_cats)

    # Create figure
    fig, ax = plt.subplots(
        figsize=(max(12, len(x_cats) * 0.8), max(8, len(y_cats) * 0.6)))

    # Create heatmap
    sns.heatmap(
        pivot_data,
        annot=True,
        fmt=".2f",
        cmap="viridis_r",  # reversed viridis
        center=None,
        square=False,
        ax=ax,
        cbar_kws={'label': 'Percentage (%)', 'format': '%.1f%%'}
    )

    # Customize appearance
    ax.set_title(title, fontsize=16, pad=20)
    ax.set_xlabel("Occupation", fontsize=12)
    ax.set_ylabel("Educational Attainment", fontsize=12)

    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)

    plt.tight_layout()

    return fig

# ------------------------
# Public: compute top/bottom heatmaps
# ------------------------


def get_heatmaps(year, data_path="data/merged_data.csv"):
    df = load_data(data_path)
    df_year = df[df["year"] == int(year)]
    if df_year.empty:
        return None, None, None, None

    educ_df = melt_education(df_year)
    occ_df = melt_occupation(df_year)
    if educ_df.empty or occ_df.empty:
        return None, None, None, None

    # totals to rank educational attainment
    educ_totals = educ_df.groupby("Educational_Attainment", as_index=False)[
        "Education_Count"].sum()
    educ_totals = educ_totals.sort_values("Education_Count", ascending=False)

    top10_educ = educ_totals.head(10)["Educational_Attainment"].tolist()
    bottom10_educ = educ_totals.tail(10)["Educational_Attainment"].tolist()

    educ_top_df = educ_df[educ_df["Educational_Attainment"].isin(
        top10_educ)].reset_index(drop=True)
    educ_bottom_df = educ_df[educ_df["Educational_Attainment"].isin(
        bottom10_educ)].reset_index(drop=True)

    occ_alphabetical = sorted(occ_df["Occupation"].unique().tolist())

    top_joint = estimate_joint(educ_top_df, occ_df)
    bottom_joint = estimate_joint(educ_bottom_df, occ_df)

    top_plot = build_heatmap(top_joint, "Top 10 Educational Attainment × Occupations (Proportional %)",
                             x_order=occ_alphabetical, y_order=top10_educ)
    bottom_plot = build_heatmap(bottom_joint, "Bottom 10 Educational Attainment × Occupations (Proportional %)",
                                x_order=occ_alphabetical, y_order=bottom10_educ)

    # Return (top_plot, bottom_plot, top_joint, bottom_joint)
    return top_plot, bottom_plot, top_joint, bottom_joint

# ------------------------
# Helper: best pairing for narratives
# ------------------------


def extract_insight(joint_df):
    if joint_df is None or joint_df.empty:
        return None, None, None
    idx = joint_df["Percent"].idxmax()
    row = joint_df.loc[idx]
    return row["Educational_Attainment"], row["Occupation"], float(row["Percent"])

# ------------------------
# Display helper
# ------------------------


def show_heatmaps(year, data_path="data/merged_data.csv"):
    """Convenience function to display both heatmaps for a given year"""
    top_plot, bottom_plot, top_joint, bottom_joint = get_heatmaps(
        year, data_path)

    if top_plot is not None:
        plt.figure(top_plot.number)
        plt.show()

    if bottom_plot is not None:
        plt.figure(bottom_plot.number)
        plt.show()

    return top_joint, bottom_joint

# ------------------------
# Save helper
# ------------------------


def save_heatmaps(year, save_dir=".", data_path="data/merged_data.csv"):
    """Save both heatmaps as PNG files"""
    top_plot, bottom_plot, top_joint, bottom_joint = get_heatmaps(
        year, data_path)

    if top_plot is not None:
        top_plot.savefig(f"{save_dir}/top_education_occupation_{year}.png",
                         dpi=300, bbox_inches='tight', facecolor='white')
        plt.close(top_plot)

    if bottom_plot is not None:
        bottom_plot.savefig(f"{save_dir}/bottom_education_occupation_{year}.png",
                            dpi=300, bbox_inches='tight', facecolor='white')
        plt.close(bottom_plot)

    return top_joint, bottom_joint
