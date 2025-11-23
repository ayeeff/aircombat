#!/usr/bin/env python3
"""
Weekly CSV → Feather converter
Only converts if CSV is newer than existing .feather (or .feather missing)
"""

import pathlib
import pandas as pd

DATA_DIR = pathlib.Path("data")

def main():
    if not DATA_DIR.exists():
        print(f"{DATA_DIR} directory not found!")
        return

    csv_files = list(DATA_DIR.rglob("*.csv"))
    print(f"Found {len(csv_files)} CSV file(s)")

    converted = 0
    for csv_path in csv_files:
        feather_path = csv_path.with_suffix(".feather")

        # Skip if feather exists and is newer or same age
        if feather_path.exists() and feather_path.stat().st_mtime >= csv_path.stat().st_mtime:
            continue

        try:
            df = pd.read_csv(csv_path)
            df.to_feather(feather_path)
            print(f"Converted: {csv_path.name} → {feather_path.name}")
            converted += 1
        except Exception as e:
            print(f"ERROR on {csv_path.name}: {e}")

    print(f"Done! {converted} file(s) converted/updated.")

if __name__ == "__main__":
    main()
