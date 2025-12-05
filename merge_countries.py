import pandas as pd
import glob
import os
import re

def merge_csvs():
    # Define the data directory
    data_dir = 'data'
    
    # path to look for csvs (e.g., data/*.csv)
    search_path = os.path.join(data_dir, "*.csv")
    all_files = glob.glob(search_path)
    
    # Regex to match filenames that are exactly 2 or 3 letters long
    # We check os.path.basename to ignore the 'data/' folder prefix in the regex
    country_pattern = re.compile(r'^[a-zA-Z]{2,3}\.csv$')
    
    dataframes = []
    
    print(f"Scanning '{data_dir}' folder...")
    
    for filepath in all_files:
        filename = os.path.basename(filepath)
        
        if country_pattern.match(filename):
            print(f"- Processing {filename}...")
            
            try:
                # Read the CSV
                df = pd.read_csv(filepath)
                
                # Extract filename without extension for the column (e.g., 'aus')
                country_name = os.path.splitext(filename)[0]
                
                # Add the new column
                df['country'] = country_name
                
                dataframes.append(df)
            except Exception as e:
                print(f"Error processing {filename}: {e}")

    if dataframes:
        # Merge all dataframes
        merged_df = pd.concat(dataframes, ignore_index=True)
        
        # Save to data folder
        output_path = os.path.join(data_dir, "global_merged.csv")
        merged_df.to_csv(output_path, index=False)
        
        print(f"Successfully merged {len(dataframes)} files into {output_path}")
    else:
        print("No matching country CSV files found in /data/.")
        # Create an empty file or raise error to ensure git has something to touch? 
        # Better to just print error so user checks logs.

if __name__ == "__main__":
    merge_csvs()
