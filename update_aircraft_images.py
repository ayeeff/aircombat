#!/usr/bin/env python3
"""
Aircraft Image Updater - DuckDuckGo Edition
Scans CSV files in data directory and updates Photo URLs with hotlink-friendly alternatives
Uses DuckDuckGo HTML scraping (100% free, no API keys needed)
"""

import os
import csv
import time
import requests
import json
import re
from pathlib import Path
from urllib.parse import urlparse, quote

# Sites known to allow hotlinking
HOTLINK_FRIENDLY_DOMAINS = [
    'imgur.com',
    'i.imgur.com',
    'flickr.com',
    'live.staticflickr.com',
    'farm1.staticflickr.com',
    'farm2.staticflickr.com',
    'farm3.staticflickr.com',
    'farm4.staticflickr.com',
    'farm5.staticflickr.com',
    'farm6.staticflickr.com',
    'farm7.staticflickr.com',
    'farm8.staticflickr.com',
    'farm9.staticflickr.com',
    'pbs.twimg.com',
    'i.redd.it',
    'preview.redd.it',
    # Unsplash
    'unsplash.com',
    'images.unsplash.com',
    'source.unsplash.com',
    # Pexels
    'pexels.com',
    'images.pexels.com',
    # Pixabay
    'pixabay.com',
    'cdn.pixabay.com',
]

def is_wikimedia_url(url):
    """Check if URL is from Wikimedia"""
    return 'wikimedia.org' in url or 'wikipedia.org' in url

def is_hotlink_friendly(url):
    """Check if URL is from a hotlink-friendly domain"""
    if not url:
        return False
    domain = urlparse(url).netloc.lower()
    return any(friendly in domain for friendly in HOTLINK_FRIENDLY_DOMAINS)

def test_image_url(url, timeout=5):
    """Test if an image URL is accessible"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.head(url, timeout=timeout, allow_redirects=True, headers=headers)
        # Check if it's actually an image
        content_type = response.headers.get('content-type', '').lower()
        return response.status_code == 200 and 'image' in content_type
    except:
        return False

def search_duckduckgo_images(query, max_results=20):
    """
    Search DuckDuckGo for images using their API
    Returns list of image URLs
    """
    try:
        # DuckDuckGo uses a token-based system
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
        }
        
        # Step 1: Get the vqd token
        params = {'q': query}
        response = requests.get('https://duckduckgo.com/', params=params, headers=headers, timeout=10)
        
        # Extract vqd token from response
        vqd_match = re.search(r'vqd=["\'](\d+-\d+(?:-\d+)?)["\']', response.text)
        if not vqd_match:
            print(f"    ⚠ Could not extract vqd token")
            return []
        
        vqd = vqd_match.group(1)
        
        # Step 2: Query the image search API
        params = {
            'l': 'us-en',
            'o': 'json',
            'q': query,
            'vqd': vqd,
            'f': ',,,',
            'p': '1',
            'v7exp': 'a',
        }
        
        response = requests.get(
            'https://duckduckgo.com/i.js',
            params=params,
            headers=headers,
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"    ⚠ API returned status {response.status_code}")
            return []
        
        data = response.json()
        results = data.get('results', [])
        
        # Extract image URLs
        image_urls = []
        for result in results[:max_results]:
            image_url = result.get('image')
            if image_url:
                image_urls.append(image_url)
        
        return image_urls
        
    except requests.exceptions.RequestException as e:
        print(f"    ❌ Request failed: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"    ❌ Failed to parse JSON: {e}")
        return []
    except Exception as e:
        print(f"    ❌ Unexpected error: {e}")
        return []

def search_aircraft_image_duckduckgo(aircraft_name, origin):
    """
    Search for aircraft images using DuckDuckGo
    Returns a hotlink-friendly image URL or None
    """
    # Construct search query
    query = f"{aircraft_name} {origin} aircraft photo"
    
    print(f"  🔍 Searching DuckDuckGo for: {query}")
    
    # Get image results
    image_urls = search_duckduckgo_images(query)
    
    if not image_urls:
        print(f"    ⚠ No images found")
        return None
    
    print(f"    📸 Found {len(image_urls)} images")
    
    # Filter for hotlink-friendly sources
    for idx, url in enumerate(image_urls, 1):
        if is_hotlink_friendly(url):
            domain = urlparse(url).netloc
            print(f"    [{idx}/{len(image_urls)}] Testing {domain}: {url[:60]}...")
            
            if test_image_url(url):
                print(f"    ✅ Valid image found!")
                return url
            else:
                print(f"    ⚠ URL not accessible, trying next...")
        else:
            domain = urlparse(url).netloc
            print(f"    [{idx}/{len(image_urls)}] Skipping non-hotlink domain: {domain}")
    
    print(f"    ❌ No hotlink-friendly images found")
    return None

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
                print(f"\n⚠️  Reached limit of {limit} updates, stopping...")
                rows.append(row)
                continue
            
            # Check if current photo needs updating
            if current_photo and is_wikimedia_url(current_photo):
                print(f"\n[Row {idx}] {aircraft} ({origin})")
                print(f"  Current: {current_photo[:80]}...")
                
                # Search for alternative
                new_url = search_aircraft_image_duckduckgo(aircraft, origin)
                
                if new_url and is_hotlink_friendly(new_url):
                    print(f"  ✅ Found alternative: {new_url[:80]}...")
                    if not dry_run:
                        row['Photo'] = new_url
                    updates += 1
                    processed += 1
                else:
                    print(f"  ❌ No suitable alternative found")
                    skipped += 1
                
                # Rate limiting to be respectful
                time.sleep(2)  # 2 seconds between requests
                
            elif current_photo and not is_hotlink_friendly(current_photo) and not is_wikimedia_url(current_photo):
                domain = urlparse(current_photo).netloc
                print(f"\n[Row {idx}] {aircraft}: Non-hotlink-friendly domain: {domain}")
                errors += 1
            
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
        
        print(f"\n  💾 Backup saved: {backup_path}")
        print(f"  ✅ Updated {updates} images in {csv_path.name}")
    
    return updates, skipped, errors

def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Update aircraft images using DuckDuckGo')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Report changes without modifying files')
    parser.add_argument('--data-dir', default='data',
                       help='Directory containing CSV files (default: data)')
    parser.add_argument('--limit', type=int, default=None,
                       help='Limit number of images to update per CSV (for testing)')
    parser.add_argument('--test', action='store_true',
                       help='Test DuckDuckGo search and exit')
    args = parser.parse_args()
    
    # Test search if requested
    if args.test:
        print("🔍 Testing DuckDuckGo image search...")
        result = search_aircraft_image_duckduckgo("F-35", "United States")
        if result:
            print(f"✅ Test successful! Found: {result}")
            return 0
        else:
            print("❌ Test failed - no results returned")
            return 1
    
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
    print(f"🖼️  Aircraft Image Updater - DuckDuckGo Edition")
    print(f"{'='*70}")
    print(f"Found {len(csv_files)} CSV files")
    print(f"Mode: {'DRY RUN (no changes will be saved)' if args.dry_run else 'LIVE UPDATE'}")
    if args.limit:
        print(f"Limit: {args.limit} updates per file")
    print(f"Source: DuckDuckGo (100% free, no API key needed) 🦆")
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
    print(f"  Files processed:     {len(csv_files)}")
    print(f"  ✅ Images updated:   {total_updates}")
    print(f"  ⚠️  Images skipped:   {total_skipped}")
    print(f"  ❌ Errors:           {total_errors}")
    
    if args.dry_run:
        print(f"\n  💡 This was a dry run - no files were modified")
        print(f"  💡 Run without --dry-run to apply changes")
    
    if args.limit:
        print(f"\n  💡 Limit was set to {args.limit} updates per file")
        print(f"  💡 Remove --limit to process all rows")
    
    print(f"{'='*70}")
    
    return 0

if __name__ == '__main__':
    exit(main())
