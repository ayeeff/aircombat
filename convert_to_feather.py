#!/usr/bin/env python3
"""
Weekly job: Convert every CSV in /data/ to .feather (Arrow IPC)
Keeps the same filename, just changes extension: data.csv → data.feather
"""

import pathlib
import pandas as pd

DATA_DIR = pathlib.Path("data")

def main():
    if not DATA_DIR.exists():
        print(f"Error: {DATA_DIR} directory not found!")
        return

    csv_files = list(DATA_DIR.rglob("*.csv"))
    if not csv_files:
        print("No CSV files found in /data/")
        return

    print(f"Found {len(csv_files)} CSV file(s). Converting to .feather...")

    for csv_path in csv_files:
        feather_path = csv_path.with_suffix(".feather")

        # Skip if already up-to-date and feather is newer
        if feather_path.exists() and feather_path.stat().st_mtime > csv_path.stat().st_mtime:
            print(f"Skipping (already up-to-date): {feather_path.name}")
            continue

        try:
            df = pd.read_csv(csv_path)
            df.to_feather(feather_path)
            print(f"Converted: {csv_path.name} → {feather_path.name} ({feather_path.stat().st_size / 1024:.1f} KB)")
        except Exception as e:
            print(f"Failed on {csv_path.name}: {e}")

    print("All done! Your HTML dashboards will now load instantly.")

if __name__ == "__main__":
    main()
