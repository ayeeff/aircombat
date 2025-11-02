#!/usr/bin/env python3
"""
Aircraft Image Updater - Wikimedia Commons Edition
Scans CSV files in data directory and converts Wikimedia URLs to direct image URLs
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
            print(f"    ⚠ API returned status {response.status_code}")
            return None
        
        data = response.json()
        
        # Extract the image URL from the response
        pages = data.get('query', {}).get('pages', {})
        
        for page_id, page_data in pages.items():
            if page_id == '-1':
                print(f"    ⚠ File not found on Wikimedia Commons")
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
        print(f"    ❌ Request failed: {e}")
        return None
    except Exception as e:
        print(f"    ❌ Unexpected error: {e}")
        return None

def convert_wikimedia_url(current_url):
    """
    Convert a Wikimedia URL to a direct hotlink-friendly URL
    """
    if not current_url or not is_wikimedia_url(current_url):
        return None
    
    print(f"  🔍 Converting Wikimedia URL...")
    
    # Extract filename
    filename = extract_filename_from_wikimedia_url(current_url)
    
    if not filename:
        print(f"    ⚠ Could not extract filename from URL")
        return None
    
    print(f"    📄 Extracted filename: {filename}")
    
    # Get direct URL from Commons API
    direct_url = get_wikimedia_direct_url(filename)
    
    if direct_url:
        print(f"    ✅ Found direct URL")
        return direct_url
    else:
        print(f"    ❌ Could not get direct URL")
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
                print(f"\n⚠️  Reached limit of {limit} updates, stopping...")
                rows.append(row)
                continue
            
            # Check if current photo needs updating
            if current_photo and is_wikimedia_url(current_photo):
                print(f"\n[Row {idx}] {aircraft} ({origin})")
                print(f"  Current: {current_photo[:80]}...")
                
                # Convert to direct URL
                new_url = convert_wikimedia_url(current_photo)
                
                if new_url and new_url != current_photo:
                    # Verify the new URL works
                    if test_image_url(new_url):
                        print(f"  ✅ Converted to: {new_url[:80]}...")
                        if not dry_run:
                            row['Photo'] = new_url
                        updates += 1
                        processed += 1
                    else:
                        print(f"  ⚠ New URL not accessible")
                        skipped += 1
                else:
                    if new_url == current_photo:
                        print(f"  ℹ️  Already using direct URL")
                    else:
                        print(f"  ❌ Could not convert URL")
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
        
        print(f"\n  💾 Backup saved: {backup_path}")
        print(f"  ✅ Updated {updates} images in {csv_path.name}")
    
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
        test_url = "https://upload.wikimedia.org/wikipedia/commons/4/43/First_F-35_headed_for_USAF_service.jpg"
        filename = extract_filename_from_wikimedia_url(test_url)
        if filename:
            print(f"✓ Extracted filename: {filename}")
            result = get_wikimedia_direct_url(filename)
            if result:
                print(f"✅ Test successful! Got URL: {result}")
                return 0
        print("❌ Test failed")
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
    print(f"🖼️  Aircraft Image Updater - Wikimedia Commons Edition")
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
