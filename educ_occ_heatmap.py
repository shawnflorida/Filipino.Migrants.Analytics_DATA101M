# educ_occ_heatmap.py
import math
import pandas as pd
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, LinearColorMapper, ColorBar, PrintfTickFormatter
from bokeh.transform import transform
from bokeh.palettes import Viridis256  # compatible with Bokeh 2.x / 3.x

# ------------------------
# Load dataset
# ------------------------
def load_data(path="data/merged_data.csv"):
    df = pd.read_csv(path)
    if "year" in df.columns:
        df["year"] = pd.to_numeric(df["year"], errors="coerce").fillna(0).astype(int)
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
# Palette helper
# ------------------------
def get_palette():
    # reverse Viridis so darker (blue/purple) = higher value
    return Viridis256[::-1]

# ------------------------
# Build a single heatmap (Bokeh figure)
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
        y_cats = sorted(joint_df["Educational_Attainment"].unique(), reverse=True)
    else:
        y_cats = [y for y in y_order if y in joint_df["Educational_Attainment"].unique()]

    palette = get_palette()
    low = float(joint_df["Percent"].min())
    high = float(joint_df["Percent"].max())
    if math.isclose(low, high):
        high = low + 1.0

    mapper = LinearColorMapper(palette=palette, low=low, high=high)

    src = joint_df.copy().reset_index(drop=True)
    # label text and dynamic color for readability
    src["label_text"] = src["Percent"].apply(lambda v: (f"{v:.1f}%" if v >= 1 else f"{v:.2f}%"))
    src["_norm"] = (src["Percent"] - low) / (high - low + 1e-9)
    src["label_color"] = src["_norm"].apply(lambda n: "white" if n > 0.5 else "black")

    source = ColumnDataSource(src)

    width = max(900, min(1600, 120 + 80 * len(x_cats)))
    height = max(420, 60 * len(y_cats))

    p = figure(
        x_range=x_cats,
        y_range=y_cats,
        width=width,
        height=height,
        title=title,
        toolbar_location="right",
        tools="hover,save,box_zoom,reset",
        tooltips=[
            ("Education", "@Educational_Attainment"),
            ("Occupation", "@Occupation"),
            ("Percent", "@Percent{0.2f}%")
        ]
    )

    p.rect(
        x="Occupation",
        y="Educational_Attainment",
        width=1,
        height=1,
        source=source,
        fill_color=transform("Percent", mapper),
        line_color="white"
    )

    p.text(
        x="Occupation",
        y="Educational_Attainment",
        text="label_text",
        source=source,
        text_align="center",
        text_baseline="middle",
        text_font_size="9pt",
        text_color="label_color"
    )

    color_bar = ColorBar(
        color_mapper=mapper,
        width=12,
        location=(0, 0),
        formatter=PrintfTickFormatter(format="%0.1f%%")
    )
    p.add_layout(color_bar, "right")

    # gentle tilt for occupancy labels
    p.xaxis.major_label_orientation = 0.9
    p.xaxis.major_label_text_font_size = "9pt"
    p.yaxis.major_label_text_font_size = "11pt"
    p.title.text_font_size = "15pt"

    return p

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
    educ_totals = educ_df.groupby("Educational_Attainment", as_index=False)["Education_Count"].sum()
    educ_totals = educ_totals.sort_values("Education_Count", ascending=False)

    top10_educ = educ_totals.head(10)["Educational_Attainment"].tolist()
    bottom10_educ = educ_totals.tail(10)["Educational_Attainment"].tolist()

    educ_top_df = educ_df[educ_df["Educational_Attainment"].isin(top10_educ)].reset_index(drop=True)
    educ_bottom_df = educ_df[educ_df["Educational_Attainment"].isin(bottom10_educ)].reset_index(drop=True)

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
