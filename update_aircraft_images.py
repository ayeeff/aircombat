#!/usr/bin/env python3
"""
Aircraft Image Updater - Wikimedia Commons Edition (Enhanced & Timestamped Backups)
Scans CSV files in data directory and updates Photo URLs with hotlink-friendly alternatives.
Uses Wikimedia Commons API (100% free, automation-friendly).
Enhanced validation to catch dead links that return 200 OK.
Now creates timestamped .csv.backup files before modifying CSVs.
"""

import os
import csv
import time
import requests
import json
import re
from pathlib import Path
from urllib.parse import urlparse, quote, unquote
from datetime import datetime


def is_wikimedia_url(url):
    """Check if URL is from Wikimedia"""
    return 'wikimedia.org' in url or 'wikipedia.org' in url


def extract_filename_from_wikimedia_url(url):
    """Extract the filename from a Wikimedia URL"""
    if not url:
        return None

    match = re.search(r'/wikipedia/commons/(?:\w+/)+([^/]+)$', url)
    if match:
        return unquote(match.group(1))

    match = re.search(r'/wiki/File:(.+)$', url)
    if match:
        return unquote(match.group(1))

    match = re.search(r'/([^/]+\.(jpg|jpeg|png|gif|svg))(\?.*)?$', url, re.IGNORECASE)
    if match:
        return unquote(match.group(1))

    return None


def generate_filename_variations(filename):
    """Generate possible filename variations for fallback searches"""
    if not filename:
        return []

    variations = [filename]
    base_name = filename

    air_force_patterns = [
        r'\s+Turkish\s+Air\s+Force', r'\s+USAF', r'\s+US\s+Air\s+Force',
        r'\s+Royal\s+Air\s+Force', r'\s+RAF', r'\s+Israeli\s+Air\s+Force',
        r'\s+Indian\s+Air\s+Force', r'\s+Pakistan\s+Air\s+Force',
        r'\s+Russian\s+Air\s+Force', r'\s+Chinese\s+Air\s+Force',
        r'\s+PLAAF', r'\s+RAAF', r'\s+Australian\s+Air\s+Force',
        r'\s+Canadian\s+Air\s+Force', r'\s+RCAF', r'\s+German\s+Air\s+Force',
        r'\s+Luftwaffe', r'\s+French\s+Air\s+Force', r'\s+Spanish\s+Air\s+Force',
        r'\s+Italian\s+Air\s+Force', r'\s+Japanese\s+Air\s+Force', r'\s+JASDF',
        r'\s+Korean\s+Air\s+Force', r'\s+ROKAF', r'\s+Saudi\s+Air\s+Force',
        r'\s+RSAF', r'\s+Swedish\s+Air\s+Force', r'\s+Thai\s+Air\s+Force',
        r'\s+RTAF'
    ]

    for pattern in air_force_patterns:
        cleaned = re.sub(pattern, '', base_name, flags=re.IGNORECASE)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        if cleaned and cleaned != base_name and cleaned not in variations:
            variations.append(cleaned)

    for pattern in [r'\s*\(\d{4}\)', r'_\d{4}', r'-\d{4}']:
        cleaned = re.sub(pattern, '', base_name)
        if cleaned and cleaned not in variations:
            variations.append(cleaned)

    if '(cropped)' in base_name:
        cleaned = base_name.replace('(cropped)', '').strip()
        if cleaned not in variations:
            variations.append(cleaned)

    cleaned = re.sub(r'_\d+(\.\w+)', r'\1', base_name)
    if cleaned != base_name and cleaned not in variations:
        variations.append(cleaned)

    if '_' in base_name:
        variations.append(base_name.replace('_', ' '))
    if ' ' in base_name:
        variations.append(base_name.replace(' ', '_'))

    return variations


def get_wikimedia_direct_url(filename, preferred_width=1280):
    """Get direct URL for a Wikimedia Commons file using the API"""
    if not filename:
        return None

    try:
        api_url = "https://commons.wikimedia.org/w/api.php"
        params = {
            'action': 'query',
            'titles': f'File:{filename}',
            'prop': 'imageinfo',
            'iiprop': 'url|size',
            'iiurlwidth': preferred_width,
            'format': 'json',
        }
        headers = {'User-Agent': 'AircraftImageUpdater/1.0 (Educational; GitHub Actions)'}

        response = requests.get(api_url, params=params, headers=headers, timeout=10)
        if response.status_code != 200:
            return None

        data = response.json()
        pages = data.get('query', {}).get('pages', {})
        for _, page_data in pages.items():
            imageinfo = page_data.get('imageinfo', [])
            if imageinfo:
                return imageinfo[0].get('thumburl') or imageinfo[0].get('url')
        return None

    except Exception:
        return None


def get_wikimedia_direct_url_with_fallback(filename, preferred_width=1280, verbose=True):
    """Try to get direct URL with filename variations as fallback"""
    result = get_wikimedia_direct_url(filename, preferred_width)
    if result:
        return result

    variations = generate_filename_variations(filename)
    for variation in variations[1:]:
        result = get_wikimedia_direct_url(variation, preferred_width)
        if result:
            return result
    return None


def convert_wikimedia_url(current_url, verbose=True):
    """Convert a Wikimedia URL to a direct hotlink-friendly URL"""
    if not current_url or not is_wikimedia_url(current_url):
        return None
    filename = extract_filename_from_wikimedia_url(current_url)
    if not filename:
        return None
    return get_wikimedia_direct_url_with_fallback(filename, verbose=verbose)


def test_image_url_enhanced(url, timeout=10):
    """Enhanced test for image URL accessibility"""
    if not url:
        return False, "Empty URL"
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.head(url, timeout=timeout, allow_redirects=True, headers=headers)
        if response.status_code == 404:
            return False, "HTTP 404"
        elif response.status_code != 200:
            return False, f"HTTP {response.status_code}"

        content_type = response.headers.get('content-type', '').lower()
        if 'image' not in content_type:
            return False, f"Wrong content-type: {content_type}"
        return True, "OK"
    except Exception as e:
        return False, str(e)


def find_image_by_aircraft(aircraft, origin='', preferred_width=1280, verbose=True):
    """Search for an image on Wikimedia Commons using aircraft name"""
    if not aircraft:
        return None

    queries = [f'"{aircraft}"']
    if origin:
        queries.insert(0, f'"{aircraft}" {origin}')

    api_url = "https://commons.wikimedia.org/w/api.php"
    for query in queries:
        try:
            params = {
                'action': 'query',
                'list': 'search',
                'srsearch': query,
                'srnamespace': 6,
                'format': 'json',
                'srlimit': 10,
            }
            headers = {'User-Agent': 'AircraftImageUpdater/1.0 (Educational; GitHub Actions)'}
            response = requests.get(api_url, params=params, headers=headers, timeout=10)
            if response.status_code != 200:
                continue

            results = response.json().get('query', {}).get('search', [])
            for result in results:
                title = result['title']
                if not title.startswith('File:'):
                    continue
                filename = title[5:]
                url = get_wikimedia_direct_url(filename, preferred_width)
                if url:
                    return url
        except Exception:
            continue
    return None


def update_csv_images(csv_path, dry_run=False, limit=None, force_recheck=False, debug=False):
    """Update image URLs in a CSV file"""
    print(f"\nProcessing: {csv_path}")
    rows = []
    updates = 0
    skipped = 0
    errors = 0
    updates_made = 0

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames

        for idx, row in enumerate(reader, start=1):
            aircraft = row.get('Aircraft', '').strip()
            origin = row.get('Origin', '').strip()
            current_photo = row.get('Photo', '').strip()

            if limit and updates_made >= limit:
                rows.append(row)
                continue

            if current_photo and is_wikimedia_url(current_photo):
                is_accessible, reason = test_image_url_enhanced(current_photo)
                if is_accessible and not force_recheck:
                    skipped += 1
                    rows.append(row)
                    continue

                new_url = convert_wikimedia_url(current_photo, verbose=False)
                found = False
                if new_url and new_url != current_photo:
                    ok, _ = test_image_url_enhanced(new_url)
                    if ok:
                        row['Photo'] = new_url
                        updates += 1
                        updates_made += 1
                        found = True
                if not found:
                    search_url = find_image_by_aircraft(aircraft, origin, verbose=False)
                    if search_url:
                        ok, _ = test_image_url_enhanced(search_url)
                        if ok:
                            row['Photo'] = search_url
                            updates += 1
                            updates_made += 1
                        else:
                            errors += 1
                    else:
                        errors += 1
                time.sleep(1)
            rows.append(row)

    if not dry_run and updates > 0:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_path = csv_path.with_name(f"{csv_path.stem}_{timestamp}.csv.backup")

        with open(backup_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            with open(csv_path, 'r', encoding='utf-8') as orig:
                reader = csv.DictReader(orig)
                writer.writerows(reader)

        with open(csv_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        print(f"💾 Backup saved: {backup_path}")
        print(f"✅ Updated {updates} images in {csv_path.name}")

    return updates, skipped, errors


def main():
    """Main execution function"""
    import argparse
    parser = argparse.ArgumentParser(description='Update aircraft images using Wikimedia Commons API')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--data-dir', default='data')
    parser.add_argument('--limit', type=int, default=None)
    parser.add_argument('--force-recheck', action='store_true')
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    if not data_dir.exists():
        print(f"❌ Directory '{data_dir}' not found")
        return 1

    csv_files = list(data_dir.glob('*.csv'))
    if not csv_files:
        print(f"❌ No CSV files found in '{data_dir}'")
        return 1

    total_updates = total_skipped = total_errors = 0
    for csv_path in sorted(csv_files):
        updates, skipped, errors = update_csv_images(
            csv_path, dry_run=args.dry_run,
            limit=args.limit, force_recheck=args.force_recheck,
            debug=args.debug
        )
        total_updates += updates
        total_skipped += skipped
        total_errors += errors

    print("\n📊 SUMMARY")
    print(f" Files processed: {len(csv_files)}")
    print(f" ✅ Images updated: {total_updates}")
    print(f" ⚠️ Images skipped: {total_skipped}")
    print(f" ❌ Errors: {total_errors}")
    return 0


if __name__ == '__main__':
    exit(main())
