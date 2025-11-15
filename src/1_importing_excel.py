import os
import matplotlib.pyplot as plt
import math
import pandas as pd
import seaborn as sns
from loguru import logger
from pathlib import Path
import numpy as np

logger.info('Import ok')


# Folders
BASE_DIR = Path("python_results")
INPUT_FOLDER = BASE_DIR
OUTPUT_FOLDER = BASE_DIR / "excel_clean_up"
PLOT_FOLDER = BASE_DIR / "plotting"

# Ensure output folders exist
for folder in (OUTPUT_FOLDER, PLOT_FOLDER):
    folder.mkdir(parents=True, exist_ok=True)

# Find CSV files
csv_files = sorted(INPUT_FOLDER.glob("*.csv"))

if not csv_files:
    raise FileNotFoundError(
        f"No CSV files found in {INPUT_FOLDER.resolve()}"
    )

logger.info(f"Found {len(csv_files)} CSV file(s).")

# Load & merge each CSV
df_list = []
for file in csv_files:
    logger.info(f"Loading: {file.name}")
    df_list.append(pd.read_csv(file))

merged_df = pd.concat(df_list, ignore_index=True)

# Output
output_path = OUTPUT_FOLDER / "merged_data.csv"
merged_df.to_csv(output_path, index=False)

logger.info(f"Merged CSV saved to: {output_path.resolve()}")

#add the rep based on the well ID 
# Dictionary for mapping well letters to replicate
rep_map = {
    "A": "rep1", "D": "rep1",
    "B": "rep2", "E": "rep2",
    "C": "rep3", "F": "rep3"
}

# Create the new 'rep' column
merged_df["REP"] = merged_df["WELL_ID"].str[0].map(rep_map)

#make two separate dataframes - one with ssc singlets, the other with only positive uptake 

#first, make a new column that specifies which GATING done in flowjo and change the name so i know what it is later 
merged_df['GATING'] = merged_df['FILE_NAME'].str.split('_').str[-1].str.split('.').str[-2]
merged_df["GATING"] = merged_df["GATING"].replace("values", "unstained_correction")

ssc_singlets_df = merged_df[merged_df["GATING"] == "SSC singlets"].copy()

# grab parameters of interest 
# p75 → 75th percentile
# p95 → 95th percentile
# top25_mean → mean of brightest 25% of cells
# gmean → geometric mean (best for fluorescence)
# cv → coefficient of variation
# skew → skewness (bright tail detection)

stats_df = ssc_singlets_df.groupby(
    ["PEPTIDE", "TREATMENT", "MEDIA", "REP"]
).agg(
    mean=("DATA_POINT", "mean"),
    median=("DATA_POINT", "median"),
    gmean=("DATA_POINT", lambda x: np.exp(np.log(x).mean())),
    p75=("DATA_POINT", lambda x: x.quantile(0.75)),
    p95=("DATA_POINT", lambda x: x.quantile(0.95)),
    top25_mean=("DATA_POINT", lambda x: x[x >= x.quantile(0.75)].mean()),
    cv=("DATA_POINT", lambda x: x.std() / x.mean()),
    skew=("DATA_POINT", "skew")
)








# # -------------- Make a heatmap --------------
# # Using merged_df as input dataframe
# # Step 1: Average replicates
# merged_avg = merged_df.groupby(
#     ["Peptide ", "Concentration (nM)", "Media "], as_index=False
# )["intensity"].mean()

# # Step 2: Get unique peptides
# peptides = merged_avg["Peptide "].unique()

# # Step 3: Create subplots (each row = peptide, 2 heatmaps side by side)
# fig, axes = plt.subplots(len(peptides), 2, figsize=(12, 3 * len(peptides)), sharey=True)

# # Ensure axes is always a 2D array
# if len(peptides) == 1:
#     axes = [axes]

# for i, pep in enumerate(peptides):
#     for j, media in enumerate(["normal", "lipodepleted"]):
#         ax = axes[i][j]

#         # Filter data for peptide + media
#         data = merged_avg[(merged_avg["Peptide "] == pep) & (merged_avg["Media "] == media)]

#         if data.empty:
#             ax.set_visible(False)
#             continue

#         # Pivot to make heatmap
#         pivot = data.pivot_table(
#             index="Concentration (nM)", columns="Peptide ", values="intensity"
#         )

#         # Plot heatmap
#         sns.heatmap(pivot, ax=ax, cmap="viridis", cbar=True)
#         ax.set_title(f"{pep} - {media}")
#         ax.set_ylabel("Concentration (nM)")
#         ax.set_xlabel("Peptide ")

# plt.tight_layout()
# plt.show()

# # -------------- Make a barplot --------------

# # Step 1: Average replicates
# merged_avg = merged_df.groupby(
#     ["Peptide ", "Concentration (nM)", "Media "], as_index=False
# )["intensity"].mean()

# # Step 2: Get unique peptides
# peptides = merged_avg["Peptide "].unique()

# # Step 3: Create subplots in 2x2 grid (adjust automatically if more peptides)
# rows = math.ceil(len(peptides) / 2)
# fig, axes = plt.subplots(rows, 2, figsize=(12, 4 * rows), sharex=True)
# axes = axes.flatten()

# for i, pep in enumerate(peptides):
#     ax = axes[i]
#     data = merged_avg[merged_avg["Peptide "] == pep]

#     sns.barplot(
#         data=data,
#         x="Concentration (nM)",
#         y="intensity",
#         hue="Media ",
#         ax=ax,
#         errorbar="sd"
#     )

#     ax.set_title(f"{pep}")
#     ax.set_ylabel("Average Intensity")
#     ax.set_xlabel("Concentration (nM)")

# # Hide any unused subplots
# for j in range(len(peptides), len(axes)):
#     fig.delaxes(axes[j])

# plt.tight_layout()
# plt.savefig(os.path.join(plotting_folder, "2583_LPDvsnorm_HTS_barplot.png"), dpi=300)
# plt.show()
# plt.close()


# # -------------- Make a boxplot --------------
# # Step 1: Get unique peptides
# peptides = merged_df["Peptide "].unique()

# # Step 2: Create subplots in 2x2 grid
# rows = math.ceil(len(peptides) / 2)
# fig, axes = plt.subplots(rows, 2, figsize=(12, 4 * rows), sharex=True)
# axes = axes.flatten()

# for i, pep in enumerate(peptides):
#     ax = axes[i]
#     data = merged_df[merged_df["Peptide "] == pep]

#     sns.boxplot(
#         data=data,
#         x="Concentration (nM)",
#         y="intensity",
#         hue="Media ",
#         hue_order=["lipodepleted", "normal"],  # set order explicitly
#         ax=ax,
#         palette="Set2"
#     )

#     ax.set_title(f"{pep}")
#     ax.set_ylabel("Intensity")
#     ax.set_xlabel("Concentration (nM)")

# # Hide any unused subplots
# for j in range(len(peptides), len(axes)):
#     fig.delaxes(axes[j])

# plt.tight_layout()
# plt.savefig(os.path.join(plotting_folder, "2583_LPDvsnorm_HTS_boxplot.png"), dpi=300)
# plt.show()
# plt.close()
