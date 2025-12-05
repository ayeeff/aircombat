import pandas as pd
import glob
import os
import re

def merge_csvs():
    # Find all CSV files in the current directory
    all_files = glob.glob("*.csv")
    
    # Regex to match filenames that are exactly 2 or 3 letters long (e.g., aus.csv, uk.csv)
    # This filters out 'products.csv', 'calcs.csv', and the output file itself.
    country_pattern = re.compile(r'^[a-zA-Z]{2,3}\.csv$')
    
    dataframes = []
    
    print("Found the following country files to merge:")
    
    for filename in all_files:
        if country_pattern.match(filename):
            print(f"- Processing {filename}...")
            
            try:
                # Read the CSV
                df = pd.read_csv(filename)
                
                # Extract filename without extension (e.g., 'aus')
                country_name = os.path.splitext(filename)[0]
                
                # Add the new column based on filename
                df['country'] = country_name
                
                dataframes.append(df)
            except Exception as e:
                print(f"Error processing {filename}: {e}")

    if dataframes:
        # Merge all dataframes
        merged_df = pd.concat(dataframes, ignore_index=True)
        
        # Save to a single CSV
        output_filename = "global_merged.csv"
        merged_df.to_csv(output_filename, index=False)
        print(f"Successfully merged {len(dataframes)} files into {output_filename}")
        
        # Optional: Save as feather format since your repo uses it
        # merged_df.to_feather("global_merged.feather") 
    else:
        print("No matching country CSV files found.")

if __name__ == "__main__":
    merge_csvs()
