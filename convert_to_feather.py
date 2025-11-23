#!/usr/bin/env python3
"""
Weekly CSV → Feather converter
Forces Uncompressed Feather format for browser/JS compatibility.
"""

import pathlib
import pandas as pd
import os

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

        # --- TIMESTAMP CHECK REMOVED TO FORCE UPDATE ---
        # We are disabling this check to ensure all files are re-saved 
        # as 'uncompressed' to fix the browser error.
        # if feather_path.exists() and feather_path.stat().st_mtime >= csv_path.stat().st_mtime:
        #     continue

        try:
            df = pd.read_csv(csv_path)
            
            # CRITICAL FIX: compression='uncompressed'
            # The JavaScript Apache Arrow reader cannot handle LZ4 (default) compression.
            df.to_feather(feather_path, compression='uncompressed')
            
            print(f"Converted: {csv_path.name} → {feather_path.name}")
            converted += 1
        except Exception as e:
            print(f"ERROR on {csv_path.name}: {e}")

    print(f"Done! {converted} file(s) converted/updated.")

if __name__ == "__main__":
    main()
