from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

# Configuration
DATA_PATH = Path("C:/Users/u244278/OneDrive - Baylor College of Medicine/Documents/BOEYNAEMS LAB 2025/flow_data_exported/2593_dynasore/2593_raw_data")
COLUMN = "YG582-A"
OUTPUT_DIR = Path("python_results")
MAP_FILE = Path("map_of_conditions.csv")

#you will also need to configure the metadata 

def read_fcs_csv(file_path: Path) -> pd.DataFrame:
    """Read FCS CSV file, skipping metadata headers."""
    return pd.read_csv(file_path, skiprows=142)


def extract_well_id(file_path: Path) -> str:
    """Extract WELL ID from FCS CSV file metadata."""
    with open(file_path) as f:
        for line in f:
            if line.strip().startswith("WELL ID"):
                return line.split(",")[1].strip()
    return None


def process_file(file_path: Path, map_df: pd.DataFrame, column: str) -> list[dict]:
    """Process a single FCS file and return list of data rows."""
    df = read_fcs_csv(file_path)
    well_id = extract_well_id(file_path)

    # Get metadata for this well
    well_info = map_df[map_df["WELL ID"] == well_id]

    if well_info.empty:
        return []

    metadata = {
        "WELL_ID": well_id,
        "TREATMENT": well_info["treatment"].values[0],
        "PEPTIDE": well_info["peptide"].values[0],
        "MEDIA": well_info["media"].values[0],
        "FILE_NAME": file_path.name,
    }

    # Create a row for each data point
    data = df[column]

    # Handle case with no data points
    if len(data) == 0:
        data = [np.nan]
    return [{**metadata, "DATA_POINT": value} for value in data]


def main():
    """Combine FCS data from multiple files with metadata mapping."""
    # Load mapping file
    map_df = pd.read_csv(f"{DATA_PATH}/{MAP_FILE}")

    # Process all CSV files
    csv_files = sorted(f for f in DATA_PATH.glob("*.csv") if f != DATA_PATH / MAP_FILE)
    rows = []

    for file_path in csv_files:
        try:
            file_rows = process_file(file_path, map_df, COLUMN)
            rows.extend(file_rows)
        except Exception as e:
            print(f"Error processing {file_path.name}: {e}")
            continue

    # Create DataFrame and save
    result_df = pd.DataFrame(rows)

    OUTPUT_DIR.mkdir(exist_ok=True)
    output_file = OUTPUT_DIR / f"{COLUMN}_combined.csv"
    result_df.to_csv(output_file, index=False)

    # Print summary
    print(f"\n{'=' * 50}")
    print(f"Combined data saved to: {output_file}")
    print(f"Total rows: {len(result_df):,}")
    print(f"Total files processed: {len(csv_files)}")


if __name__ == "__main__":
    main()