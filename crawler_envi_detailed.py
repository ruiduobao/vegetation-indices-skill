#!/usr/bin/env python3
"""
ENVI Detailed Formula Crawler - Category pages
Crawls ENVI documentation category pages for detailed index formulas.
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
import os

BASE_URL = "https://www.nv5geospatialsoftware.com/docs"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}
PROXIES = {
    "http": "http://127.0.0.1:7897",
    "https": "http://127.0.0.1:7897",
}

OUTPUT_DIR = "crawled_data/envi_indices"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def fetch_page(url, retries=3):
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=30, proxies=PROXIES)
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            print(f"  Error fetching {url}: {e}")
            if attempt < retries - 1:
                time.sleep(2 * (attempt + 1))
    return None


def extract_vegetation_indices_from_page(html, page_name):
    """Extract vegetation index formulas and details from category pages"""
    soup = BeautifulSoup(html, "lxml")
    content = soup.find("div", {"id": "content"}) or soup.find("div", class_="content") or soup.find("article") or soup.body
    text = content.get_text(separator="\n") if content else ""
    
    indices = []
    
    # Split by index sections - each index starts with its abbreviation in bold
    # Pattern: Index Name (ABBREV) followed by description
    sections = re.split(r'\n(?=[A-Z][a-z].*?\([A-Z]{2,}\))', text)
    
    for section in sections:
        section = section.strip()
        if not section:
            continue
        
        # Try to extract abbreviation and name
        match = re.match(r'(.*?)\s*\(([A-Z][A-Za-z0-9/\-]+?)\)', section)
        if match:
            name = match.group(1).strip()
            abbrev = match.group(2).strip()
            
            idx = {
                "abbreviation": abbrev,
                "name": name,
                "category": page_name,
                "category_cn": page_name,
                "source": "ENVI Documentation",
                "url": f"{BASE_URL}/{page_name.lower().replace(' ', '')}.html",
            }
            
            # Look for formula in the section
            # ENVI uses LaTeX-like math notation
            formula_match = re.search(r'(?:[Ff]ormula|INDEX|VI)\s*[=:]\s*(.+?)(?:\n\n|\.|$)', section, re.DOTALL)
            if formula_match:
                idx["formula"] = formula_match.group(1).strip()
            
            # Look for value range
            range_match = re.search(r'[Vv]alue[s]?\s*(?:range|between)[:\s]+(.+?)(?:\.|$)', section)
            if range_match:
                idx["value_range"] = range_match.group(1).strip()
            
            # Look for reference
            ref_match = re.search(r'[Rr]eference[s]?[:\s]+(.+?)(?:\n\n|\n[A-Z])', section, re.DOTALL)
            if ref_match:
                idx["reference"] = ref_match.group(1).strip()
            
            # Look for wavelengths used
            wavelengths = re.findall(r'(\d{3})\s*nm', section)
            if wavelengths:
                idx["wavelengths_nm"] = sorted(set(wavelengths))
            
            indices.append(idx)
    
    return indices


def parse_narrowband_page_detailed(html):
    """Parse narrowband greenness page with formulas"""
    soup = BeautifulSoup(html, "lxml")
    content = soup.find("div", {"id": "content"}) or soup.find("div", class_="content") or soup.find("article") or soup.body
    text = content.get_text(separator="\n") if content else ""
    
    indices = []
    
    # The narrowband page has detailed sections for each index
    # Split by index headers
    index_sections = re.split(r'\n(?=[A-Z][a-z].*?\([A-Z]{2,}\)\n)', text)
    
    for section in index_sections:
        section = section.strip()
        if not section or len(section) < 50:
            continue
        
        match = re.match(r'(.*?)\s*\(([A-Z][A-Za-z0-9/\-]+?)\)', section)
        if not match:
            continue
        
        name = match.group(1).strip()
        abbrev = match.group(2).strip()
        
        idx = {
            "abbreviation": abbrev,
            "name": name,
            "category": "Narrowband Greenness",
            "category_cn": "窄带绿度",
            "source": "ENVI Documentation",
            "url": f"{BASE_URL}/narrowbandgreenness.html",
        }
        
        # Extract formula
        formula_match = re.search(r'(?:index|VI)\s*(?:is|=|equals?)\s*(.+?)(?:\.|$)', section, re.DOTALL)
        if not formula_match:
            formula_match = re.search(r'(?:[Ff]ormula|equation)[:\s]*(.+?)(?:\.|$)', section, re.DOTALL)
        if formula_match:
            idx["formula"] = formula_match.group(1).strip()
        
        # Value range
        range_match = re.search(r'(?:[Vv]alues?\s*(?:range|from|between))\s*(.+?)(?:\.|common range)', section)
        if range_match:
            idx["value_range"] = range_match.group(1).strip()
        
        # Common range
        common_match = re.search(r'[Cc]ommon range.*?:\s*(.+?)(?:\.|$)', section)
        if common_match:
            idx["common_range"] = common_match.group(1).strip()
        
        # Reference
        ref_match = re.search(r'[Rr]eference[:\s]+(.+?)(?:\n\n|$)', section, re.DOTALL)
        if ref_match:
            idx["reference"] = ref_match.group(1).strip()
        
        # Extract all mentioned wavelengths
        wavelengths = re.findall(r'(\d{3})\s*nm', section)
        if wavelengths:
            idx["wavelengths_nm"] = sorted(set(wavelengths))
        
        # Extract description (first meaningful sentence)
        sentences = section.split('.')
        if sentences:
            desc = sentences[0].strip()
            if len(desc) > 20:
                idx["description"] = desc
        
        indices.append(idx)
    
    return indices


def main():
    print("=" * 60)
    print("ENVI Detailed Formula Crawler")
    print("=" * 60)
    
    all_indices = {}
    
    # 1. Narrowband Greenness - has formulas
    print("\n[1] Parsing Narrowband Greenness (with formulas)...")
    url = f"{BASE_URL}/narrowbandgreenness.html"
    html = fetch_page(url)
    if html:
        indices = parse_narrowband_page_detailed(html)
        print(f"  Found {len(indices)} indices with formulas")
        for idx in indices:
            all_indices[idx["abbreviation"]] = idx
    
    # 2. Vegetation Indices Background
    print("\n[2] Crawling Vegetation Indices Background...")
    url = f"{BASE_URL}/vegetationindicesbackground.html"
    html = fetch_page(url)
    if html:
        indices = extract_vegetation_indices_from_page(html, "Vegetation Indices")
        print(f"  Found {len(indices)} vegetation indices")
        for idx in indices:
            if idx["abbreviation"] not in all_indices:
                all_indices[idx["abbreviation"]] = idx
            elif not all_indices[idx["abbreviation"]].get("formula") and idx.get("formula"):
                all_indices[idx["abbreviation"]]["formula"] = idx["formula"]
    
    # 3. Broadband Greenness
    print("\n[3] Crawling Broadband Greenness...")
    url = f"{BASE_URL}/broadbandgreenness.html"
    html = fetch_page(url)
    if html:
        indices = extract_vegetation_indices_from_page(html, "Broadband Greenness")
        print(f"  Found {len(indices)} broadband greenness indices")
        for idx in indices:
            if idx["abbreviation"] not in all_indices:
                all_indices[idx["abbreviation"]] = idx
    
    # 4. Other Vegetation categories
    for category in ["lightuseefficiency", "canopynitrogen", "dryorsenescentcarbon", 
                      "leafpigments", "canopywatercontent"]:
        print(f"\n  Crawling {category}...")
        url = f"{BASE_URL}/{category}.html"
        html = fetch_page(url)
        if html:
            cat_name = category.replace("lightuseefficiency", "Light Use Efficiency") \
                               .replace("canopynitrogen", "Canopy Nitrogen") \
                               .replace("dryorsenescentcarbon", "Dry or Senescent Carbon") \
                               .replace("leafpigments", "Leaf Pigments") \
                               .replace("canopywatercontent", "Canopy Water Content")
            indices = extract_vegetation_indices_from_page(html, cat_name)
            print(f"    Found {len(indices)} indices")
            for idx in indices:
                if idx["abbreviation"] not in all_indices:
                    all_indices[idx["abbreviation"]] = idx
    
    # Convert to list
    result = list(all_indices.values())
    
    print(f"\n{'='*60}")
    print(f"Total unique indices collected: {len(result)}")
    
    # Count by category
    cats = {}
    for idx in result:
        cat = idx.get("category", "Unknown")
        cats[cat] = cats.get(cat, 0) + 1
    
    print("\nBy category:")
    for cat, count in sorted(cats.items()):
        print(f"  {cat}: {count}")
    
    # Count indices with formulas
    with_formula = sum(1 for idx in result if idx.get("formula"))
    print(f"\nIndices with formulas: {with_formula}/{len(result)}")
    
    # Save
    output_file = os.path.join(OUTPUT_DIR, "envi_detailed_indices.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaved to: {output_file}")
    print("=" * 60)


if __name__ == "__main__":
    main()
