#!/usr/bin/env python3
"""
Aircraft Image Updater - Wikimedia Commons Edition
Scans CSV files in data directory and updates Photo URLs with hotlink-friendly alternatives
Uses Wikimedia Commons API (100% free, automation-friendly)
"""
import os
import csv
import time
import requests
import json
import re
from pathlib import Path
from urllib.parse import urlparse, quote, unquote

def is_wikimedia_url(url):
    """Check if URL is from Wikimedia"""
    return 'wikimedia.org' in url or 'wikipedia.org' in url

def extract_filename_from_wikimedia_url(url):
    """Extract the filename from a Wikimedia URL"""
    if not url:
        return None
   
    # Handle different Wikimedia URL formats
    # Format 1: https://upload.wikimedia.org/wikipedia/commons/4/43/Filename.jpg
    match = re.search(r'/wikipedia/commons/(?:\w+/)+([^/]+)$', url)
    if match:
        return unquote(match.group(1))
   
    # Format 2: https://en.wikipedia.org/wiki/File:Filename.jpg
    match = re.search(r'/wiki/File:(.+)$', url)
    if match:
        return unquote(match.group(1))
   
    # Format 3: Direct filename in URL
    match = re.search(r'/([^/]+\.(jpg|jpeg|png|gif|svg))(\?.*)?$', url, re.IGNORECASE)
    if match:
        return unquote(match.group(1))
   
    return None

def generate_filename_variations(filename):
    """Generate possible filename variations for fallback searches"""
    if not filename:
        return []
   
    variations = [filename]
   
    # Remove common suffixes and try variations
    base_name = filename
   
    # List of countries/air forces to remove from filenames
    air_force_patterns = [
        r'\s+Turkish\s+Air\s+Force',
        r'\s+USAF',
        r'\s+US\s+Air\s+Force',
        r'\s+Royal\s+Air\s+Force',
        r'\s+RAF',
        r'\s+Israeli\s+Air\s+Force',
        r'\s+Indian\s+Air\s+Force',
        r'\s+Pakistan\s+Air\s+Force',
        r'\s+Russian\s+Air\s+Force',
        r'\s+Chinese\s+Air\s+Force',
        r'\s+PLAAF',
        r'\s+RAAF',
        r'\s+Australian\s+Air\s+Force',
        r'\s+Canadian\s+Air\s+Force',
        r'\s+RCAF',
        r'\s+German\s+Air\s+Force',
        r'\s+Luftwaffe',
        r'\s+French\s+Air\s+Force',
        r'\s+Spanish\s+Air\s+Force',
        r'\s+Italian\s+Air\s+Force',
        r'\s+Japanese\s+Air\s+Force',
        r'\s+JASDF',
        r'\s+Korean\s+Air\s+Force',
        r'\s+ROKAF',
        r'\s+Saudi\s+Air\s+Force',
        r'\s+RSAF',
        r'\s+Swedish\s+Air\s+Force',
        r'\s+Thai\s+Air\s+Force',
        r'\s+RTAF',
        r'_Turkish_Air_Force',
        r'_USAF',
        r'_US_Air_Force',
        r'_Royal_Air_Force',
        r'_RAF',
        r'_Israeli_Air_Force',
        r'_Indian_Air_Force',
        r'_Pakistan_Air_Force',
        r'_Russian_Air_Force',
        r'_Chinese_Air_Force',
        r'_PLAAF',
        r'_RAAF',
        r'_Australian_Air_Force',
        r'_Canadian_Air_Force',
        r'_RCAF',
        r'_German_Air_Force',
        r'_Luftwaffe',
        r'_French_Air_Force',
        r'_Spanish_Air_Force',
        r'_Italian_Air_Force',
        r'_Japanese_Air_Force',
        r'_JASDF',
        r'_Korean_Air_Force',
        r'_ROKAF',
        r'_Saudi_Air_Force',
        r'_RSAF',
        r'_Swedish_Air_Force',
        r'_Thai_Air_Force',
        r'_RTAF',
    ]
   
    # Try removing air force names
    for pattern in air_force_patterns:
        cleaned = re.sub(pattern, '', base_name, flags=re.IGNORECASE)
        # Clean up any double spaces or underscores
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        cleaned = re.sub(r'_+', '_', cleaned).strip('_')
        if cleaned != base_name and cleaned not in variations and cleaned:
            variations.append(cleaned)
   
    # Try without year/date patterns like (2020), _2020, -2020
    for pattern in [r'\s*\(\d{4}\)', r'_\d{4}', r'-\d{4}']:
        cleaned = re.sub(pattern, '', base_name)
        if cleaned != base_name and cleaned not in variations:
            variations.append(cleaned)
   
    # Try without "(cropped)" suffix
    if '(cropped)' in base_name or '_(cropped)' in base_name:
        cleaned = base_name.replace('(cropped)', '').replace('_(cropped)', '')
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        if cleaned not in variations:
            variations.append(cleaned)
   
    # Try without trailing numbers like _1, _2, _3
    cleaned = re.sub(r'_\d+(\.\w+)', r'\1', base_name)
    if cleaned != base_name and cleaned not in variations:
        variations.append(cleaned)
   
    # Try replacing underscores with spaces and vice versa
    if '_' in base_name:
        spaced = base_name.replace('_', ' ')
        if spaced not in variations:
            variations.append(spaced)
   
    if ' ' in base_name:
        underscored = base_name.replace(' ', '_')
        if underscored not in variations:
            variations.append(underscored)
   
    # Try combinations: remove air force AND year
    for af_pattern in air_force_patterns[:10]: # Just try first 10 to avoid too many variations
        for year_pattern in [r'\s*\(\d{4}\)', r'_\d{4}', r'-\d{4}']:
            cleaned = re.sub(af_pattern, '', base_name, flags=re.IGNORECASE)
            cleaned = re.sub(year_pattern, '', cleaned)
            cleaned = re.sub(r'\s+', ' ', cleaned).strip()
            cleaned = re.sub(r'_+', '_', cleaned).strip('_')
            if cleaned and cleaned not in variations and len(cleaned) > 5:
                variations.append(cleaned)
   
    return variations

def get_wikimedia_direct_url(filename, preferred_width=1280):
    """
    Get direct URL for a Wikimedia Commons file using the API
    Returns a direct hotlink-friendly URL
    """
    if not filename:
        return None
   
    try:
        # Use Wikimedia Commons API
        api_url = "https://commons.wikimedia.org/w/api.php"
       
        params = {
            'action': 'query',
            'titles': f'File:{filename}',
            'prop': 'imageinfo',
            'iiprop': 'url|size',
            'iiurlwidth': preferred_width,
            'format': 'json',
        }
       
        headers = {
            'User-Agent': 'AircraftImageUpdater/1.0 (Educational; GitHub Actions)'
        }
       
        response = requests.get(api_url, params=params, headers=headers, timeout=10)
       
        if response.status_code != 200:
            print(f" ⚠ API returned status {response.status_code}")
            return None
       
        data = response.json()
       
        # Extract the image URL from the response
        pages = data.get('query', {}).get('pages', {})
       
        for page_id, page_data in pages.items():
            if page_id == '-1':
                # File not found
                return None
           
            imageinfo = page_data.get('imageinfo', [])
            if imageinfo:
                # Try to get the thumbnailed URL (which is direct and hotlink-friendly)
                thumb_url = imageinfo[0].get('thumburl')
                if thumb_url:
                    return thumb_url
               
                # Fallback to original URL
                url = imageinfo[0].get('url')
                return url
       
        return None
       
    except requests.exceptions.RequestException as e:
        print(f" ❌ Request failed: {e}")
        return None
    except Exception as e:
        print(f" ❌ Unexpected error: {e}")
        return None

def get_wikimedia_direct_url_with_fallback(filename, preferred_width=1280):
    """
    Try to get direct URL with filename variations as fallback
    """
    if not filename:
        return None
   
    # Try original filename first
    result = get_wikimedia_direct_url(filename, preferred_width)
    if result:
        return result
   
    # Try variations
    variations = generate_filename_variations(filename)
   
    if len(variations) > 1:
        print(f" 🔄 Trying {len(variations)-1} filename variation(s)...")
   
    for idx, variation in enumerate(variations[1:], 1): # Skip first one (already tried)
        print(f" [{idx}] Trying: {variation[:60]}...")
        result = get_wikimedia_direct_url(variation, preferred_width)
        if result:
            print(f" ✅ Found with variation!")
            return result
   
    return None

def convert_wikimedia_url(current_url):
    """
    Convert a Wikimedia URL to a direct hotlink-friendly URL
    Returns None if file not found
    """
    if not current_url or not is_wikimedia_url(current_url):
        return None
   
    print(f" 🔍 Converting Wikimedia URL...")
   
    # Extract filename
    filename = extract_filename_from_wikimedia_url(current_url)
   
    if not filename:
        print(f" ⚠ Could not extract filename from URL")
        return None
   
    print(f" 📄 Extracted filename: {filename}")
   
    # Get direct URL from Commons API (with fallback variations)
    direct_url = get_wikimedia_direct_url_with_fallback(filename)
   
    if direct_url:
        print(f" ✅ Found direct URL")
        return direct_url
    else:
        print(f" ⚠ Could not find file on Wikimedia Commons (tried variations)")
        return None

def find_image_by_aircraft(aircraft, origin='', preferred_width=1280):
    """
    Search for an image on Wikimedia Commons using the aircraft name
    Returns the first suitable direct URL found
    """
    if not aircraft:
        return None

    search_query = f'"{aircraft}"'
    if origin:
        search_query += f' {origin}'

    try:
        api_url = "https://commons.wikimedia.org/w/api.php"
       
        params = {
            'action': 'query',
            'list': 'search',
            'srsearch': search_query,
            'srnamespace': 6,
            'format': 'json',
            'srprop': 'size',
            'srlimit': 5,
        }
       
        headers = {
            'User-Agent': 'AircraftImageUpdater/1.0 (Educational; GitHub Actions)'
        }
       
        response = requests.get(api_url, params=params, headers=headers, timeout=10)
       
        if response.status_code != 200:
            print(f" ⚠ Search API returned status {response.status_code}")
            return None
       
        data = response.json()
       
        search_results = data.get('query', {}).get('search', [])
       
        print(f" 🔍 Found {len(search_results)} search results for '{aircraft}'")
       
        for idx, result in enumerate(search_results, 1):
            if result.get('ns') != 6:
                continue
           
            title = result['title']
            filename = title[5:]  # Remove 'File:'
           
            # Skip if too small (e.g., icons)
            if result.get('size', 0) < 50000:
                print(f" [{idx}] Skipping small image: {filename[:40]}...")
                continue
           
            print(f" [{idx}] Trying search result: {filename[:60]}...")
            direct_url = get_wikimedia_direct_url(filename, preferred_width)
            if direct_url:
                print(f" ✅ Found via search!")
                return direct_url
           
        print(f" ⚠ No suitable image found in search results")
        return None
       
    except requests.exceptions.RequestException as e:
        print(f" ❌ Search request failed: {e}")
        return None
    except Exception as e:
        print(f" ❌ Unexpected search error: {e}")
        return None

def test_image_url(url, timeout=5):
    """Test if an image URL is accessible"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.head(url, timeout=timeout, allow_redirects=True, headers=headers)
        content_type = response.headers.get('content-type', '').lower()
        return response.status_code == 200 and 'image' in content_type
    except:
        return False

def update_csv_images(csv_path, dry_run=False, limit=None):
    """
    Update image URLs in a CSV file
   
    Args:
        csv_path: Path to CSV file
        dry_run: If True, only report changes without modifying file
        limit: Maximum number of rows to process (for testing)
    """
    print(f"\n{'='*70}")
    print(f"Processing: {csv_path}")
    print(f"{'='*70}")
   
    rows = []
    updates = 0
    skipped = 0
    errors = 0
    processed = 0
   
    # Read CSV
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
       
        for idx, row in enumerate(reader, start=1):
            aircraft = row.get('Aircraft', '')
            origin = row.get('Origin', '')
            current_photo = row.get('Photo', '')
           
            # Check limit
            if limit and processed >= limit:
                print(f"\n⚠️ Reached limit of {limit} updates, stopping...")
                rows.append(row)
                continue
           
            # Only process if there's a photo URL from Wikimedia
            if current_photo and is_wikimedia_url(current_photo):
                print(f"\n[Row {idx}] {aircraft} ({origin})")
                print(f" Current: {current_photo[:80]}...")
               
                # First, check if current URL is still accessible
                if test_image_url(current_photo):
                    print(f" ℹ️ Current URL is accessible, skipping.")
                    skipped += 1
                else:
                    print(f" ❌ Current URL is dead, attempting to replace...")
                   
                    # Try to convert/fix the existing URL
                    new_url = convert_wikimedia_url(current_photo)
                    found = False
                    if new_url:
                        if test_image_url(new_url):
                            print(f" ✅ Fixed via conversion: {new_url[:80]}...")
                            if not dry_run:
                                row['Photo'] = new_url
                            updates += 1
                            found = True
                            processed += 1
                        else:
                            print(f" ⚠ Converted URL not accessible.")
                    if not found:
                        # Fallback to search
                        print(f" 🔍 Searching for replacement image...")
                        search_url = find_image_by_aircraft(aircraft, origin)
                        if search_url and test_image_url(search_url):
                            print(f" ✅ Found via search: {search_url[:80]}...")
                            if not dry_run:
                                row['Photo'] = search_url
                            updates += 1
                            processed += 1
                        else:
                            print(f" ❌ No replacement found, keeping original (dead).")
                            skipped += 1
               
                # Rate limiting to be respectful
                time.sleep(1)  # 1 second between requests
           
            rows.append(row)
   
    # Write back if not dry run and updates were made
    if not dry_run and updates > 0:
        backup_path = csv_path.with_suffix('.csv.backup')
        # Create backup
        with open(backup_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            # Write original rows from backup
            with open(csv_path, 'r', encoding='utf-8') as orig:
                reader = csv.DictReader(orig)
                writer.writerows(reader)
       
        # Write updated data
        with open(csv_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
       
        print(f"\n 💾 Backup saved: {backup_path}")
        print(f" ✅ Updated {updates} images in {csv_path.name}")
   
    return updates, skipped, errors

def main():
    """Main execution function"""
    import argparse
   
    parser = argparse.ArgumentParser(description='Update aircraft images using Wikimedia Commons API')
    parser.add_argument('--dry-run', action='store_true',
                       help='Report changes without modifying files')
    parser.add_argument('--data-dir', default='data',
                       help='Directory containing CSV files (default: data)')
    parser.add_argument('--limit', type=int, default=None,
                       help='Limit number of images to update per CSV (for testing)')
    parser.add_argument('--test', action='store_true',
                       help='Test Wikimedia API and exit')
    args = parser.parse_args()
   
    # Test API if requested
    if args.test:
        print("🔍 Testing Wikimedia Commons API...")
        print("\nTest 1: Regular file")
        test_url = "https://upload.wikimedia.org/wikipedia/commons/4/43/First_F-35_headed_for_USAF_service.jpg"
        filename = extract_filename_from_wikimedia_url(test_url)
        if filename:
            print(f"✓ Extracted filename: {filename}")
            result = get_wikimedia_direct_url_with_fallback(filename)
            if result:
                print(f"✅ Test 1 successful! Got URL: {result[:80]}...")
            else:
                print("❌ Test 1 failed")
       
        print("\nTest 2: File with year suffix (should try variations)")
        test_url2 = "https://upload.wikimedia.org/wikipedia/commons/9/9e/Boeing_E-7_Wedgetail_RAAF_(2020).jpg"
        filename2 = extract_filename_from_wikimedia_url(test_url2)
        if filename2:
            print(f"✓ Extracted filename: {filename2}")
            result2 = get_wikimedia_direct_url_with_fallback(filename2)
            if result2:
                print(f"✅ Test 2 successful! Got URL: {result2[:80]}...")
            else:
                print("❌ Test 2 failed (will keep original URL)")
       
        print("\nTest 3: Search fallback")
        search_result = find_image_by_aircraft("Chengdu J-20", "China")
        if search_result:
            print(f"✅ Test 3 successful! Search URL: {search_result[:80]}...")
        else:
            print("❌ Test 3 failed")
       
        return 0
   
    data_dir = Path(args.data_dir)
   
    if not data_dir.exists():
        print(f"❌ Error: Directory '{data_dir}' not found")
        return 1
   
    # Find all CSV files
    csv_files = list(data_dir.glob('*.csv'))
   
    if not csv_files:
        print(f"❌ No CSV files found in '{data_dir}'")
        return 1
   
    print(f"{'='*70}")
    print(f"🖼️ Aircraft Image Updater - Wikimedia Commons Edition")
    print(f"{'='*70}")
    print(f"Found {len(csv_files)} CSV files")
    print(f"Mode: {'DRY RUN (no changes will be saved)' if args.dry_run else 'LIVE UPDATE'}")
    if args.limit:
        print(f"Limit: {args.limit} updates per file")
    print(f"Source: Wikimedia Commons API (100% free, automation-friendly)")
    print(f"{'='*70}\n")
   
    total_updates = 0
    total_skipped = 0
    total_errors = 0
   
    # Process each CSV
    for csv_path in sorted(csv_files):
        updates, skipped, errors = update_csv_images(csv_path, dry_run=args.dry_run, limit=args.limit)
        total_updates += updates
        total_skipped += skipped
        total_errors += errors
   
    # Summary
    print(f"\n{'='*70}")
    print(f"📊 SUMMARY")
    print(f"{'='*70}")
    print(f" Files processed: {len(csv_files)}")
    print(f" ✅ Images updated: {total_updates}")
    print(f" ⚠️ Images skipped: {total_skipped}")
    print(f" ❌ Errors: {total_errors}")
   
    if args.dry_run:
        print(f"\n 💡 This was a dry run - no files were modified")
        print(f" 💡 Run without --dry-run to apply changes")
   
    if args.limit:
        print(f"\n 💡 Limit was set to {args.limit} updates per file")
        print(f" 💡 Remove --limit to process all rows")
   
    print(f"{'='*70}")
   
    return 0

if __name__ == '__main__':
    exit(main())
