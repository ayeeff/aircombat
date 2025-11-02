#!/usr/bin/env python3
"""
Aircraft Image Updater - Wikimedia Commons Edition (Enhanced & Fixed)
Scans CSV files in data directory and updates Photo URLs with hotlink-friendly alternatives
Uses Wikimedia Commons API (100% free, automation-friendly)
Enhanced validation to catch dead links that return 200 OK
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
    for af_pattern in air_force_patterns[:10]:
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
            return None
       
        data = response.json()
       
        # Extract the image URL from the response
        pages = data.get('query', {}).get('pages', {})
       
        for page_id, page_data in pages.items():
            if page_id == '-1':
                return None
           
            imageinfo = page_data.get('imageinfo', [])
            if imageinfo:
                # Try to get the thumbnailed URL (direct and hotlink-friendly)
                thumb_url = imageinfo[0].get('thumburl')
                if thumb_url:
                    return thumb_url
               
                # Fallback to original URL
                url = imageinfo[0].get('url')
                return url
       
        return None
       
    except Exception:
        return None

def get_wikimedia_direct_url_with_fallback(filename, preferred_width=1280, verbose=True):
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
   
    if len(variations) > 1 and verbose:
        print(f" 🔄 Trying {len(variations)-1} filename variation(s)...")
   
    for idx, variation in enumerate(variations[1:], 1):
        if verbose:
            print(f" [{idx}] Trying: {variation[:60]}...")
        result = get_wikimedia_direct_url(variation, preferred_width)
        if result:
            if verbose:
                print(f" ✅ Found with variation!")
            return result
   
    return None

def convert_wikimedia_url(current_url, verbose=True):
    """
    Convert a Wikimedia URL to a direct hotlink-friendly URL
    Returns None if file not found
    """
    if not current_url or not is_wikimedia_url(current_url):
        return None
   
    if verbose:
        print(f" 🔍 Converting Wikimedia URL...")
   
    # Extract filename
    filename = extract_filename_from_wikimedia_url(current_url)
   
    if not filename:
        if verbose:
            print(f" ⚠ Could not extract filename from URL")
        return None
   
    if verbose:
        print(f" 📄 Extracted filename: {filename}")
   
    # Get direct URL from Commons API (with fallback variations)
    direct_url = get_wikimedia_direct_url_with_fallback(filename, verbose=verbose)
   
    if direct_url:
        if verbose:
            print(f" ✅ Found direct URL")
        return direct_url
    else:
        if verbose:
            print(f" ⚠ Could not find file on Wikimedia Commons (tried variations)")
        return None

def find_image_by_aircraft(aircraft, origin='', preferred_width=1280, verbose=True):
    """
    Search for an image on Wikimedia Commons using the aircraft name
    Returns the first suitable direct URL found
    """
    if not aircraft:
        return None

    # Generate possible search queries with progressive fallbacks
    queries = []
    
    # Clean up aircraft name for better searches
    clean_aircraft = aircraft
    
    # Remove common prefixes that might confuse search
    clean_aircraft = re.sub(r'^(C[CP]-|CE-)', '', clean_aircraft)
    
    # Extract base aircraft name (e.g., "F-16" from "F-16I Sufa")
    base_match = re.match(r'^([A-Z]+-?\d+[A-Z]*)', clean_aircraft)
    base_aircraft = base_match.group(1) if base_match else None
    
    # Strategy 1: Try exact name with origin
    if origin:
        queries.append(f'"{clean_aircraft}" {origin}')
    queries.append(f'"{clean_aircraft}"')
    
    # Strategy 2: Try without quotes for broader search
    if origin:
        queries.append(f'{clean_aircraft} {origin}')
    
    # Strategy 3: Try base aircraft model if we have one (e.g., "F-15" instead of "F-15SA Eagle II")
    if base_aircraft and base_aircraft != clean_aircraft:
        if origin:
            queries.append(f'"{base_aircraft}" {origin}')
        queries.append(f'"{base_aircraft}"')
    
    # Strategy 4: Try manufacturer + base model (e.g., "Boeing F-15")
    manufacturer_match = re.match(r'^([A-Za-z]+(?:\s+[A-Za-z]+)?)\s+([A-Z]+-?\d+)', clean_aircraft)
    if manufacturer_match:
        manufacturer = manufacturer_match.group(1)
        model = manufacturer_match.group(2)
        queries.append(f'{manufacturer} {model}')
    
    # Strategy 5: For very specific variants, try the generic version
    # E.g., "JF-17" instead of "JF-17B Thunder"
    generic_match = re.match(r'^([A-Z]+-?\d+)[A-Z]?\b', clean_aircraft)
    if generic_match:
        generic = generic_match.group(1)
        if generic != base_aircraft:
            queries.append(f'"{generic}"')

    try:
        api_url = "https://commons.wikimedia.org/w/api.php"
       
        for query_idx, query in enumerate(queries, 1):
            params = {
                'action': 'query',
                'list': 'search',
                'srsearch': query,
                'srnamespace': 6,
                'format': 'json',
                'srprop': 'size',
                'srlimit': 20,
            }
           
            headers = {
                'User-Agent': 'AircraftImageUpdater/1.0 (Educational; GitHub Actions)'
            }
           
            response = requests.get(api_url, params=params, headers=headers, timeout=10)
           
            if response.status_code != 200:
                continue
           
            data = response.json()
           
            search_results = data.get('query', {}).get('search', [])
           
            if verbose:
                print(f" 🔍 Found {len(search_results)} search results for '{query}' (strategy {query_idx}/{len(queries)})")
           
            for idx, result in enumerate(search_results, 1):
                if result.get('ns') != 6:
                    continue
               
                title = result['title']
                filename = title[5:]  # Remove 'File:'
               
                if verbose:
                    print(f" [{idx}] Trying search result: {filename[:60]}...")
                direct_url = get_wikimedia_direct_url(filename, preferred_width)
                if direct_url:
                    if verbose:
                        print(f" ✅ Found via search (strategy {query_idx})!")
                    return direct_url
            
            # If we found results but none worked, try next strategy
            # If no results at all, also try next strategy
           
        return None
       
    except Exception:
        return None

def test_image_url_enhanced(url, timeout=10):
    """
    Enhanced test for image URL accessibility
    Returns (is_accessible, reason) tuple
    """
    if not url:
        return False, "Empty URL"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # First try HEAD request
        response = requests.head(url, timeout=timeout, allow_redirects=True, headers=headers)
        
        # Check status code
        if response.status_code == 404:
            return False, "HTTP 404"
        elif response.status_code != 200:
            return False, f"HTTP {response.status_code}"
        
        # Check content type
        content_type = response.headers.get('content-type', '').lower()
        if 'image' not in content_type:
            # Some servers don't return content-type in HEAD, try GET with range
            try:
                response = requests.get(url, timeout=timeout, headers={**headers, 'Range': 'bytes=0-1023'}, stream=True)
                content_type = response.headers.get('content-type', '').lower()
                
                if 'image' not in content_type:
                    # Check if it's an HTML error page
                    if 'text/html' in content_type or 'text/plain' in content_type:
                        return False, "Returns HTML/text instead of image"
                    return False, f"Wrong content-type: {content_type}"
                
                # Check content length - if too small, likely an error page
                content_length = response.headers.get('content-length')
                if content_length and int(content_length) < 1000:
                    return False, "File too small (likely error page)"
                    
            except Exception as e:
                return False, f"GET request failed: {str(e)}"
        
        # Additional check: verify Content-Length exists and is reasonable
        content_length = response.headers.get('content-length')
        if content_length:
            size = int(content_length)
            if size < 1000:  # Less than 1KB is suspicious for an image
                return False, "File too small"
            if size > 50_000_000:  # More than 50MB is suspicious
                return False, "File too large"
        
        return True, "OK"
        
    except requests.exceptions.Timeout:
        return False, "Timeout"
    except requests.exceptions.ConnectionError:
        return False, "Connection error"
    except Exception as e:
        return False, f"Error: {str(e)}"

def update_csv_images(csv_path, dry_run=False, limit=None, force_recheck=False, debug=False):
    """
    Update image URLs in a CSV file
   
    Args:
        csv_path: Path to CSV file
        dry_run: If True, only report changes without modifying file
        limit: Maximum number of updates to process (for testing)
        force_recheck: If True, recheck all URLs even if they seem accessible
        debug: If True, print detailed debug info
    """
    print(f"\n{'='*70}")
    print(f"Processing: {csv_path}")
    print(f"{'='*70}")
   
    rows = []
    updates = 0
    skipped = 0
    errors = 0
    updates_made = 0
   
    # Read CSV
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
       
        for idx, row in enumerate(reader, start=1):
            aircraft = row.get('Aircraft', '').strip()
            origin = row.get('Origin', '').strip()
            current_photo = row.get('Photo', '').strip()
           
            if debug:
                print(f"\n[DEBUG Row {idx}] Aircraft: {aircraft}")
                print(f"[DEBUG Row {idx}] Origin: {origin}")
                print(f"[DEBUG Row {idx}] Photo: {current_photo}")
           
            # Check if we've hit the update limit
            if limit and updates_made >= limit:
                if debug:
                    print(f"[DEBUG] Hit limit of {limit} updates, skipping remaining rows")
                rows.append(row)
                continue
           
            # Only process if there's a photo URL from Wikimedia
            if current_photo and is_wikimedia_url(current_photo):
                print(f"\n[Row {idx}] {aircraft} ({origin})")
                print(f" Current: {current_photo}")
               
                # Enhanced URL accessibility check
                is_accessible, reason = test_image_url_enhanced(current_photo)
                
                if is_accessible and not force_recheck:
                    print(f" ℹ️ Current URL is accessible, skipping.")
                    skipped += 1
                    rows.append(row)
                    continue
                
                # URL is dead or we're force rechecking
                if not is_accessible:
                    print(f" ❌ Current URL is dead ({reason}), attempting to replace...")
                else:
                    print(f" 🔄 Force rechecking URL...")
               
                # Try to convert/fix the existing URL
                new_url = convert_wikimedia_url(current_photo, verbose=True)
                found = False
                
                if new_url and new_url != current_photo:
                    is_new_accessible, new_reason = test_image_url_enhanced(new_url)
                    if is_new_accessible:
                        print(f" ✅ Fixed via conversion: {new_url}")
                        if not dry_run:
                            row['Photo'] = new_url
                        updates += 1
                        updates_made += 1
                        found = True
                    else:
                        print(f" ⚠ Converted URL not accessible ({new_reason}).")
                
                if not found:
                    # Fallback to search
                    print(f" 🔍 Searching for replacement image...")
                    search_url = find_image_by_aircraft(aircraft, origin, verbose=True)
                    
                    if search_url:
                        is_search_accessible, search_reason = test_image_url_enhanced(search_url)
                        if is_search_accessible:
                            print(f" ✅ Found via search: {search_url}")
                            if not dry_run:
                                row['Photo'] = search_url
                            updates += 1
                            updates_made += 1
                            found = True
                        else:
                            print(f" ⚠ Search URL not accessible ({search_reason}).")
                    
                    if not found:
                        print(f" ❌ No valid replacement found.")
                        errors += 1
               
                # Rate limiting to be respectful
                time.sleep(1)
           
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
                       help='Limit number of images to UPDATE per CSV (for testing)')
    parser.add_argument('--force-recheck', action='store_true',
                       help='Recheck all URLs even if they seem accessible')
    parser.add_argument('--debug', action='store_true',
                       help='Print debug information')
    parser.add_argument('--test', action='store_true',
                       help='Test Wikimedia API and exit')
    args = parser.parse_args()
   
    # Test API if requested
    if args.test:
        print("🔍 Testing Enhanced URL Checking...")
        
        test_urls = [
            ("https://upload.wikimedia.org/wikipedia/commons/4/43/First_F-35_headed_for_USAF_service.jpg", "Working URL"),
            ("https://upload.wikimedia.org/wikipedia/commons/9/9e/Boeing_E-7_Wedgetail_RAAF_%282020%29.jpg", "Dead URL (year suffix)"),
            ("https://upload.wikimedia.org/wikipedia/commons/invalid/path/test.jpg", "Invalid URL"),
        ]
        
        for url, description in test_urls:
            print(f"\nTesting: {description}")
            print(f"URL: {url}")
            is_accessible, reason = test_image_url_enhanced(url)
            print(f"Result: {'✅ Accessible' if is_accessible else f'❌ Dead ({reason})'}")
        
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
    print(f"🖼️ Aircraft Image Updater - Enhanced Version")
    print(f"{'='*70}")
    print(f"Found {len(csv_files)} CSV files")
    print(f"Mode: LIVE UPDATE - Files will be modified!")
    if args.limit:
        print(f"Limit: {args.limit} UPDATES per file (will skip accessible URLs)")
    if args.force_recheck:
        print(f"Force recheck: ENABLED (will recheck all URLs)")
    if args.debug:
        print(f"Debug: ENABLED")
    print(f"Source: Wikimedia Commons API with enhanced validation")
    print(f"{'='*70}")
    print(f"⚠️  WARNING: This will modify your CSV files!")
    print(f"{'='*70}\n")
   
    total_updates = 0
    total_skipped = 0
    total_errors = 0
   
    # Process each CSV
    for csv_path in sorted(csv_files):
        updates, skipped, errors = update_csv_images(
            csv_path, 
            dry_run=args.dry_run, 
            limit=args.limit,
            force_recheck=args.force_recheck,
            debug=args.debug
        )
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
        print(f" 💡 This limits UPDATES, not total rows processed")
        print(f" 💡 Remove --limit to process all dead links")
   
    print(f"{'='*70}")
   
    return 0

if __name__ == '__main__':
    exit(main())
