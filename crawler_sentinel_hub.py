#!/usr/bin/env python3
"""
Sentinel Hub Custom Scripts Crawler
Crawls Sentinel-2 RS indices from sentinel-hub.github.io
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
import os

BASE_URL = "https://sentinel-hub.github.io/custom-scripts"
PROXIES = None
if os.environ.get("VEGETATION_SEARCH_USE_PROXY") == "1":
    _proxy_url = os.environ.get("HTTP_PROXY") or os.environ.get("HTTPS_PROXY")
    if _proxy_url:
        PROXIES = {"http": _proxy_url, "https": _proxy_url}
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

OUTPUT_DIR = "crawled_data/sentinel_hub"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def fetch_page(url, retries=3):
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=30, proxies=PROXIES)
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            print(f"  Error: {e}")
            if attempt < retries - 1:
                time.sleep(2 * (attempt + 1))
    return None


def parse_index_list(html):
    """Parse the main index list page"""
    soup = BeautifulSoup(html, "lxml")
    table = soup.find("table")
    if not table:
        return []
    
    indices = []
    rows = table.find_all("tr")[1:]  # skip header
    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 3:
            continue
        
        abbrev = cols[0].get_text(strip=True)
        name = cols[1].get_text(strip=True)
        script_link = cols[2].find("a")
        script_url = script_link.get("href", "") if script_link else ""
        
        # Extract ID from script URL
        id_match = re.search(r'id_(\d+)\.js', script_url)
        index_id = int(id_match.group(1)) if id_match else 0
        
        indices.append({
            "abbreviation": abbrev,
            "name": name,
            "index_id": index_id,
            "script_url": f"{BASE_URL}/sentinel-2/{script_url}" if script_url else "",
            "source": "Sentinel Hub Custom Scripts",
            "source_url": f"{BASE_URL}/sentinel-2/indexdb/",
            "sensor": "Sentinel-2",
        })
    
    return indices


def parse_script_formula(js_text, abbrev):
    """Extract formula from JavaScript code"""
    formula = ""
    
    # Look for formula in comments
    comment_formula = re.search(r'//\s*[Ff]ormula[:\s]*(.+?)(?:\n|$)', js_text)
    if comment_formula:
        formula = comment_formula.group(1).strip()
    
    # Look for band mapping comments
    bands = {}
    for match in re.finditer(r'//\s*(\w+)[:\s]+(\d+|\w+)\s*(?:nm)?', js_text):
        bands[match.group(1)] = match.group(2)
    
    # Look for the actual calculation in JS
    calc_match = re.search(r'return\s+(.+?);', js_text, re.DOTALL)
    if calc_match and not formula:
        formula = calc_match.group(1).strip()
        # Clean up JS syntax
        formula = formula.replace("B04", "Red").replace("B08", "NIR").replace("B03", "Green").replace("B02", "Blue")
        formula = formula.replace("B05", "RedEdge1").replace("B06", "RedEdge2").replace("B07", "RedEdge3")
        formula = formula.replace("B8A", "NIRn").replace("B11", "SWIR1").replace("B12", "SWIR2")
        formula = formula.replace("B01", "Coastal").replace("B09", "WaterVapor")
        formula = formula.replace("B10", "Cirrus")
        formula = re.sub(r'math\.', '', formula, flags=re.IGNORECASE)
    
    return formula, bands


def main():
    print("=" * 60)
    print("Sentinel Hub Custom Scripts Crawler")
    print("=" * 60)
    
    # 1. Parse main index list
    print("\n[1] Parsing main index list...")
    html = fetch_page(f"{BASE_URL}/sentinel-2/indexdb/")
    if not html:
        print("Failed to fetch main page")
        return
    
    indices = parse_index_list(html)
    print(f"  Found {len(indices)} indices")
    
    # 2. Fetch individual script files for formulas
    print("\n[2] Fetching JavaScript formulas...")
    formulas_found = 0
    for i, idx in enumerate(indices):
        if idx["script_url"]:
            js = fetch_page(idx["script_url"])
            if js:
                formula, bands = parse_script_formula(js, idx["abbreviation"])
                if formula:
                    idx["formula"] = formula
                    formulas_found += 1
                if bands:
                    idx["bands"] = bands
            time.sleep(0.1)
        
        if (i + 1) % 50 == 0:
            print(f"  Processed {i+1}/{len(indices)}...")
    
    print(f"  Formulas found: {formulas_found}/{len(indices)}")
    
    # Save
    output_file = os.path.join(OUTPUT_DIR, "sentinel_hub_indices.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(indices, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaved to: {output_file}")
    
    # Summary
    categories = {}
    for idx in indices:
        cat = idx.get("category", "Unknown")
        categories[cat] = categories.get(cat, 0) + 1
    
    print(f"\nTotal: {len(indices)} indices")
    print("=" * 60)


if __name__ == "__main__":
    main()
