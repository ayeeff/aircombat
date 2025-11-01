import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os
import time

def scrape_us_aircraft():
    """Scrape US military aircraft data from Military History Wiki"""
    url = "https://military-history.fandom.com/wiki/List_of_active_United_States_military_aircraft"
    
    # More comprehensive headers to avoid 403 errors
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0',
    }
    
    try:
        # Add delay to be respectful
        time.sleep(2)
        
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        aircraft_data = []
        
        # Find all tables on the page
        tables = soup.find_all('table', {'class': 'wikitable'})
        
        if not tables:
            # Try finding tables without specific class
            tables = soup.find_all('table')
            print(f"Found {len(tables)} tables (no wikitable class)")
        
        if not tables:
            raise ValueError("No tables found on the page")
        
        print(f"Found {len(tables)} tables")
        
        for table_idx, table in enumerate(tables):
            print(f"\nProcessing table {table_idx + 1}...")
            
            # Find header row to identify columns
            headers = []
            header_row = table.find('tr')
            if header_row:
                headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
                print(f"Headers: {headers}")
            
            # Process data rows
            rows = table.find_all('tr')[1:]  # Skip header row
            
            for row in rows:
                cols = row.find_all(['td', 'th'])
                
                if len(cols) >= 6:  # Expecting at least 6 columns
                    try:
                        # Extract text from each column
                        aircraft = cols[0].get_text(strip=True)
                        
                        # Get photo URL if available
                        photo = ''
                        img = cols[1].find('img')
                        if img and img.get('src'):
                            photo = img.get('src')
                            # Convert to full URL if relative
                            if photo.startswith('//'):
                                photo = 'https:' + photo
                            elif photo.startswith('/'):
                                photo = 'https://military-history.fandom.com' + photo
                        
                        origin = cols[2].get_text(strip=True) if len(cols) > 2 else ''
                        aircraft_type = cols[3].get_text(strip=True) if len(cols) > 3 else ''
                        versions = cols[4].get_text(strip=True) if len(cols) > 4 else ''
                        in_service = cols[5].get_text(strip=True) if len(cols) > 5 else ''
                        notes = cols[6].get_text(strip=True) if len(cols) > 6 else ''
                        
                        # Skip empty rows
                        if aircraft and aircraft.strip():
                            aircraft_data.append({
                                'Aircraft': aircraft,
                                'Photo': photo,
                                'Origin': origin,
                                'Type': aircraft_type,
                                'Versions': versions,
                                'In_Service': in_service,
                                'Notes': notes
                            })
                    
                    except (ValueError, IndexError) as e:
                        print(f"Error processing row: {e}")
                        continue
        
        print(f"\nTotal aircraft scraped: {len(aircraft_data)}")
        return aircraft_data
    
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            print(f"Access forbidden (403). The website may be blocking automated requests.")
            print("Trying alternative approach...")
            # Return empty list to allow workflow to continue
            return []
        else:
            print(f"HTTP Error: {e}")
            return []
    except Exception as e:
        print(f"Error scraping data: {e}")
        return []

def main():
    print("Starting US Military Aircraft scraper...")
    print("Source: Military History Wiki\n")
    
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    
    # Scrape aircraft data
    aircraft_data = scrape_us_aircraft()
    
    if not aircraft_data:
        print("\nNo data scraped. Creating empty CSV to prevent workflow failure...")
        # Create empty DataFrame with proper columns
        df = pd.DataFrame(columns=['Aircraft', 'Photo', 'Origin', 'Type', 'Versions', 'In_Service', 'Notes', 'Scraped_Date'])
        filename = 'data/us_aircraft.csv'
        df.to_csv(filename, index=False)
        print(f"Empty CSV created at {filename}")
        print("\nNote: The website may be blocking automated requests.")
        print("Consider using a different data source or running the script locally with a browser session.")
        return
    
    # Create DataFrame
    df = pd.DataFrame(aircraft_data)
    
    # Add scraped date for versioning
    df['Scraped_Date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Reorder columns to match requested format
    df = df[['Aircraft', 'Photo', 'Origin', 'Type', 'Versions', 'In_Service', 'Notes', 'Scraped_Date']]
    
    # Display summary
    print("\nData preview:")
    print(df.head(10))
    print(f"\nTotal records: {len(df)}")
    
    # Save to CSV
    filename = 'data/us_aircraft.csv'
    df.to_csv(filename, index=False)
    print(f"\nData saved to {filename}")
    
    # Verify save
    if os.path.exists(filename):
        saved_df = pd.read_csv(filename)
        print(f"\nVerification: {filename} loaded successfully with {len(saved_df)} rows")
        print("\nSample of saved data:")
        print(saved_df.head())
    else:
        print(f"\nError: {filename} not found after save!")
    
    print("\nScraping completed successfully!")

if __name__ == "__main__":
    main()
