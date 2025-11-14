import os
import matplotlib.pyplot as plt
import math
import pandas as pd
import seaborn as sns
from loguru import logger

logger.info('Import ok')

input_folder = 'raw_data'
output_folder = 'python_results/excel_clean_up/'
plotting_folder = 'python_results/plotting'

if not os.path.exists(output_folder):
    os.mkdir(output_folder)

if not os.path.exists(plotting_folder):
    os.mkdir(plotting_folder)

# List all Excel files in the folder (assuming only one Excel file)
input_files = [f for f in os.listdir(input_folder) if f.endswith('.xlsx')]

input_file = input_files[0]  # Get the only Excel file name
file_path = os.path.join(input_folder, input_file)  # Construct the full path

# Load all sheets from the selected Excel file into a dictionary of DataFrames because I put each experiment on a different sheet 
sheets_dict = pd.read_excel(file_path, sheet_name=None)

# Add a column to each dataframe that indicates the sheet name/ replicate
for sheet_name, df in sheets_dict.items():
    df['Sheet'] = sheet_name 

logger.info('Sheet added as a column')

# Merge it into a new dataframe 
merged_df = pd.concat(sheets_dict.values(), ignore_index=True)

# Define file name
output_file = 'merged_data.xlsx'

# Combine the folder and file name to create the full path
output_path = os.path.join(output_folder, output_file)

# Save the DataFrame to the specified path
merged_df.to_excel(output_path, index=False)

logger.info('Excel merged and imported successfully')




# -------------- Make a heatmap --------------
# Using merged_df as input dataframe
# Step 1: Average replicates
merged_avg = merged_df.groupby(
    ["Peptide ", "Concentration (nM)", "Media "], as_index=False
)["intensity"].mean()

# Step 2: Get unique peptides
peptides = merged_avg["Peptide "].unique()

# Step 3: Create subplots (each row = peptide, 2 heatmaps side by side)
fig, axes = plt.subplots(len(peptides), 2, figsize=(12, 3 * len(peptides)), sharey=True)

# Ensure axes is always a 2D array
if len(peptides) == 1:
    axes = [axes]

for i, pep in enumerate(peptides):
    for j, media in enumerate(["normal", "lipodepleted"]):
        ax = axes[i][j]

        # Filter data for peptide + media
        data = merged_avg[(merged_avg["Peptide "] == pep) & (merged_avg["Media "] == media)]

        if data.empty:
            ax.set_visible(False)
            continue

        # Pivot to make heatmap
        pivot = data.pivot_table(
            index="Concentration (nM)", columns="Peptide ", values="intensity"
        )

        # Plot heatmap
        sns.heatmap(pivot, ax=ax, cmap="viridis", cbar=True)
        ax.set_title(f"{pep} - {media}")
        ax.set_ylabel("Concentration (nM)")
        ax.set_xlabel("Peptide ")

plt.tight_layout()
plt.show()

# -------------- Make a barplot --------------

# Step 1: Average replicates
merged_avg = merged_df.groupby(
    ["Peptide ", "Concentration (nM)", "Media "], as_index=False
)["intensity"].mean()

# Step 2: Get unique peptides
peptides = merged_avg["Peptide "].unique()

# Step 3: Create subplots in 2x2 grid (adjust automatically if more peptides)
rows = math.ceil(len(peptides) / 2)
fig, axes = plt.subplots(rows, 2, figsize=(12, 4 * rows), sharex=True)
axes = axes.flatten()

for i, pep in enumerate(peptides):
    ax = axes[i]
    data = merged_avg[merged_avg["Peptide "] == pep]

    sns.barplot(
        data=data,
        x="Concentration (nM)",
        y="intensity",
        hue="Media ",
        ax=ax,
        errorbar="sd"
    )

    ax.set_title(f"{pep}")
    ax.set_ylabel("Average Intensity")
    ax.set_xlabel("Concentration (nM)")

# Hide any unused subplots
for j in range(len(peptides), len(axes)):
    fig.delaxes(axes[j])

plt.tight_layout()
plt.savefig(os.path.join(plotting_folder, "2583_LPDvsnorm_HTS_barplot.png"), dpi=300)
plt.show()
plt.close()


# -------------- Make a boxplot --------------
# Step 1: Get unique peptides
peptides = merged_df["Peptide "].unique()

# Step 2: Create subplots in 2x2 grid
rows = math.ceil(len(peptides) / 2)
fig, axes = plt.subplots(rows, 2, figsize=(12, 4 * rows), sharex=True)
axes = axes.flatten()

for i, pep in enumerate(peptides):
    ax = axes[i]
    data = merged_df[merged_df["Peptide "] == pep]

    sns.boxplot(
        data=data,
        x="Concentration (nM)",
        y="intensity",
        hue="Media ",
        hue_order=["lipodepleted", "normal"],  # set order explicitly
        ax=ax,
        palette="Set2"
    )

    ax.set_title(f"{pep}")
    ax.set_ylabel("Intensity")
    ax.set_xlabel("Concentration (nM)")

# Hide any unused subplots
for j in range(len(peptides), len(axes)):
    fig.delaxes(axes[j])

plt.tight_layout()
plt.savefig(os.path.join(plotting_folder, "2583_LPDvsnorm_HTS_boxplot.png"), dpi=300)
plt.show()
plt.close()
