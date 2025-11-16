from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from loguru import logger

logger.info("Imports OK")

# --------------------
# Folders & file setup
# --------------------
BASE_DIR = Path("python_results")
INPUT_FOLDER = BASE_DIR
OUTPUT_FOLDER = BASE_DIR / "excel_clean_up"
PLOT_FOLDER = BASE_DIR / "plotting"

for folder in (OUTPUT_FOLDER, PLOT_FOLDER):
    folder.mkdir(parents=True, exist_ok=True)

# --------------------
# Load & merge CSVs
# --------------------
csv_files = sorted(INPUT_FOLDER.glob("*.csv"))

if not csv_files:
    raise FileNotFoundError(f"No CSV files found in {INPUT_FOLDER.resolve()}")

logger.info(f"Found {len(csv_files)} CSV file(s).")

df_list = []
for file in csv_files:
    logger.info(f"Loading: {file.name}")
    df_list.append(pd.read_csv(file))

merged_df = pd.concat(df_list, ignore_index=True)

# Save merged raw data (no filtering)
output_path = OUTPUT_FOLDER / "merged_data.csv"
merged_df.to_csv(output_path, index=False)
logger.info(f"Merged CSV saved to: {output_path.resolve()}")

# --------------------
# Add REP based on WELL_ID
# --------------------
rep_map = {
    "A": "rep1", "D": "rep1",
    "B": "rep2", "E": "rep2",
    "C": "rep3", "F": "rep3",
}

merged_df["REP"] = merged_df["WELL_ID"].str[0].map(rep_map)

# --------------------
# Parse GATING from FILE_NAME
# --------------------
merged_df["GATING"] = (
    merged_df["FILE_NAME"]
    .str.split("_").str[-1]      # last chunk
    .str.split(".").str[0]       # drop extension
)

# Rename "values" gate so it's clearer later
merged_df["GATING"] = merged_df["GATING"].replace("values", "unstained_correction")

# Keep only SSC singlets
ssc_singlets_df = merged_df[merged_df["GATING"] == "SSC singlets"].copy()
logger.info(f"SSC singlets rows: {len(ssc_singlets_df):,}")

# --------------------
# Robust fluorescence stats (ignore <= 0)
# --------------------
def compute_fluo_stats(
    df: pd.DataFrame,
    value_col: str = "DATA_POINT",
    group_cols=("PEPTIDE", "TREATMENT", "MEDIA", "REP"),
) -> pd.DataFrame:
    """
    Compute robust fluorescence stats per group, ignoring non-positive values.

    Returns one row per group with:
        - event_count (all events, before filtering)
        - mean, median (positive values only)
        - gmean (geometric mean of positive values)
        - p75, p95 (positive values)
        - top25_mean (mean of brightest 25% positive values)
        - cv (std/mean on positive values)
        - skew (skewness on positive values)
    """

    def _positive(x: pd.Series) -> pd.Series:
        return x[x > 0]

    def _gmean(x: pd.Series) -> float:
        x = _positive(x)
        if len(x) == 0:
            return np.nan
        return float(np.exp(np.log(x).mean()))

    def _cv(x: pd.Series) -> float:
        x = _positive(x)
        if len(x) == 0:
            return np.nan
        m = x.mean()
        return float(x.std(ddof=1) / m) if m != 0 else np.nan

    def _skew(x: pd.Series) -> float:
        x = _positive(x)
        return float(x.skew()) if len(x) > 0 else np.nan

    def _p75(x: pd.Series) -> float:
        x = _positive(x)
        return float(x.quantile(0.75)) if len(x) > 0 else np.nan

    def _p95(x: pd.Series) -> float:
        x = _positive(x)
        return float(x.quantile(0.95)) if len(x) > 0 else np.nan

    def _top25_mean(x: pd.Series) -> float:
        x = _positive(x)
        if len(x) == 0:
            return np.nan
        q75 = x.quantile(0.75)
        return float(x[x >= q75].mean())

    stats_df = (
        df
        .groupby(list(group_cols))
        .agg(
            event_count=(value_col, "size"),                       # all events
            mean=(value_col, lambda x: _positive(x).mean()),
            median=(value_col, lambda x: _positive(x).median()),
            gmean=(value_col, _gmean),
            p75=(value_col, _p75),
            p95=(value_col, _p95),
            top25_mean=(value_col, _top25_mean),
            cv=(value_col, _cv),
            skew=(value_col, _skew),
        )
        .reset_index()
    )

    return stats_df


stats_df = compute_fluo_stats(
    ssc_singlets_df,
    value_col="DATA_POINT",
    group_cols=("PEPTIDE", "TREATMENT", "MEDIA", "REP"),
)

# Save stats to CSV too (optional but handy)
stats_out = OUTPUT_FOLDER / "ssc_stats_by_condition.csv"
stats_df.to_csv(stats_out, index=False)
logger.info(f"Per-condition stats saved to: {stats_out.resolve()}")

# --------------------
# Reshape for plotting
# --------------------
# --- melt & filter once ---
plot_df = stats_df.melt(
    id_vars=["PEPTIDE", "TREATMENT", "MEDIA", "REP"],
    var_name="parameter",
    value_name="value",
)

keep = ["mean", "median", "gmean", "p75", "p95", "top25_mean", "cv", "skew"]
plot_df = plot_df[plot_df["parameter"].isin(keep)]

# only normal media
plot_df_normal = plot_df[plot_df["MEDIA"] == "normal"].copy()

# peptide groups
group1 = ["CROT", "LDL"]
group2 = ["GR30", "GP30", "LL37"]

def plot_peptide_group(plot_df_normal, peptides, fig_title):
    sub_df = plot_df_normal[plot_df_normal["PEPTIDE"].isin(peptides)].copy()
    if sub_df.empty:
        print(f"No data for peptides {peptides}")
        return

    metrics = keep
    n_metrics = len(metrics)
    n_cols = 4
    n_rows = math.ceil(n_metrics / n_cols)

    fig, axes = plt.subplots(
        n_rows, n_cols,
        figsize=(18, 6),
        squeeze=False
    )

    sns.set(style="whitegrid")

    peptide_order = peptides
    treatment_order = sorted(sub_df["TREATMENT"].unique())

    for i, metric in enumerate(metrics):
        r = i // n_cols
        c = i % n_cols
        ax = axes[r, c]

        mdf = sub_df[sub_df["parameter"] == metric]

        sns.barplot(
            data=mdf,
            x="PEPTIDE",
            y="value",
            hue="TREATMENT",
            order=peptide_order,
            hue_order=treatment_order,
            ax=ax,
        )

        ax.set_title(metric)
        ax.set_xlabel("PEPTIDE")
        ax.set_ylabel("value")
        ax.set_xticklabels(peptide_order, rotation=45, ha="right")

        if i == 0:
            ax.legend(title="TREATMENT")
        else:
            ax.legend().remove()

    # hide any unused axes
    for j in range(n_metrics, n_rows * n_cols):
        r = j // n_cols
        c = j % n_cols
        axes[r, c].set_visible(False)

    fig.suptitle(fig_title, y=1.02, fontsize=14)
    fig.tight_layout()

    # ----------------------------
    # SAVE FIGURE TO PLOT FOLDER
    # ----------------------------
    save_path = PLOT_FOLDER / f"{fig_title.replace(' ', '_')}.png"
    fig.savefig(save_path, dpi=300, bbox_inches="tight")
    logger.info(f"Saved figure: {save_path}")

    
# Figure 1: CROT + LDL
plot_peptide_group(plot_df_normal, group1, "CROT + LDL")

# Figure 2: GR30 + GP30 + LL37
plot_peptide_group(plot_df_normal, group2, "GR30 + GP30 + LL37")


