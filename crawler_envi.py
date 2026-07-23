#!/usr/bin/env python3
"""
ENVI Spectral Indices Crawler
Crawls NV5 GeoSpatial Software documentation for spectral indices formulas and metadata.
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
PROXIES = None
if os.environ.get("VEGETATION_SEARCH_USE_PROXY") == "1":
    _proxy_url = os.environ.get("HTTP_PROXY") or os.environ.get("HTTPS_PROXY")
    if _proxy_url:
        PROXIES = {"http": _proxy_url, "https": _proxy_url}

OUTPUT_DIR = "crawled_data/envi_indices"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def fetch_page(url, retries=3):
    """Fetch a page with retries and proxy"""
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


def parse_narrowband_greenness(html):
    """Parse the Narrowband Greenness page for index details"""
    soup = BeautifulSoup(html, "lxml")
    
    # Find the main content area
    content = soup.find("div", {"id": "content"}) or soup.find("div", class_="content") or soup.find("article") or soup.body
    
    # Get the text content
    text = content.get_text(separator="\n") if content else ""
    
    indices = []
    
    # Define the indices listed on this page
    narrowband_indices = [
        ("ARVI", "Atmospherically Resistant Vegetation Index"),
        ("MCARI", "Modified Chlorophyll Absorption Ratio Index"),
        ("MCARI2", "Modified Chlorophyll Absorption Ratio Index - Improved"),
        ("MRENDVI", "Modified Red Edge Normalized Difference Vegetation Index"),
        ("MRESR", "Modified Red Edge Simple Ratio"),
        ("MTVI", "Modified Triangular Vegetation Index"),
        ("MTVI2", "Modified Triangular Vegetation Index - Improved"),
        ("RENDVI", "Red Edge Normalized Difference Vegetation Index"),
        ("REPI", "Red Edge Position Index"),
        ("TCARI", "Transformed Chlorophyll Absorption Reflectance Index"),
        ("TVI", "Triangular Vegetation Index"),
        ("VREI1", "Vogelmann Red Edge Index 1"),
        ("VREI2", "Vogelmann Red Edge Index 2"),
    ]
    
    for abbrev, full_name in narrowband_indices:
        idx = {
            "abbreviation": abbrev,
            "name": full_name,
            "category": "Narrowband Greenness",
            "category_cn": "窄带绿度",
            "source": "ENVI Documentation",
            "url": f"{BASE_URL}/narrowbandgreenness.html",
        }
        indices.append(idx)
    
    return indices


def parse_alphabetical_list(html):
    """Parse the alphabetical list of spectral indices"""
    soup = BeautifulSoup(html, "lxml")
    content = soup.find("div", {"id": "content"}) or soup.find("div", class_="content") or soup.find("article") or soup.body
    
    text = content.get_text(separator="\n") if content else ""
    
    # Extract index names from the alphabetical list
    indices = []
    
    # Pattern: "Index Name (ABBREV)"
    pattern = r'([A-Za-z][A-Za-z0-9 /\-]+?)\s*\(([A-Z][A-Za-z0-9/\-]+?)\)'
    
    # Known categories based on ENVI docs
    categories = {
        "vegetation": [
            "NDVI", "EVI", "SAVI", "MSAVI", "OSAVI", "GNDVI", "NDWI", "LSWI",
            "RVI", "DVI", "PVI", "TSAVI", "ATSAVI", "GOSAVI", "GSAVI", "MCARI",
            "MCARI1", "MCARI2", "MTVI", "MTVI2", "CIgreen", "CIrededge", "TCARI",
            "NDRE", "NDRE1", "NDRE2", "RENDVI", "NDVI705", "mNDVI", "mND750/705",
            "SR", "MSR", "MSR670", "MSR705", "MSR705/445", "MSRNir/Red", "RDVI",
            "WDRVI", "BWDRVI", "GBNDVI", "GRNDVI", "NIRv", "ARVI", "GARI",
            "VARI", "VARIgreen", "GLI", "ExG", "ExR", "ExGR", "CIVE", "VEG",
            "COM1", "COM2", "GRVI", "MGRVI", "RGBVI", "IKAW", "IPVI", "TNDVI",
            "REIP", "SIPI", "PSRI", "PRI", "SIPI2", "PSRI2", "CRI550", "CRI700",
            "ARI", "mARI", "NPCI", "NPQI", "CAI", "NDLI", "NDNI", "NDNI2",
            "NRI", "SIWSI", "LWCI", "HI", "MSI", "NDII", "NDII6", "NDII7",
            "BI", "BI2", "SI", "SI1", "SI2", "SI3", "NDSI", "NDSI2", "NDSI3",
            "YVI", "GYVI", "MYVI", "MGVI", "MNSI", "MSBI", "GVMI", "LSWI2",
            "BSI", "NBSI", "DWSI", "DSWI", "DSWI-5", "CWSI", "MRENDVI", "MRESR",
            "TVI", "VREI1", "VREI2", "REPI", "MNLI", "NLI", "TDVI", "TGI",
            "GVI", "GDVI", "GCI", "GRVI", "GSAVI", "OSAVI2", "MCARI/OSAVI",
            "MCARI/MTVI2", "MCARI/OSAVI750", "MSAVIhyper", "MSAVI2", "MRVI",
            "CASI NDVI", "CASI TM4/3", "Chlgreen", "Chlred-edge", "CVI",
            "Datt1", "Datt4", "Datt6", "DLAI", "D678/500", "D800/550", "D800/680",
            "D833/658", "DD", "DPI", "EPI", "Gitelson2", "IR550", "IR700",
            "IVI", "LCI", "LogR", "MCARI705", "MCARI710", "MCARI1510",
            "MCARI2/OSAVI2", "MD734/747/715/72", "MND750/705", "MRVI", "mCRIG",
            "mCRIRE", "mSR", "MTCI", "MVI", "ND850/1788/1928", "ND850/2218/1928",
            "SOGI", "Vog2",
        ],
        "burn": [
            "BAI", "NBR", "NBR2", "NBRT1", "NBRT2", "CSVI", "SAVI2",
        ],
        "geology": [
            "ALUI", "CALI", "CLAI", "CLAY", "DOLI", "ECAI", "FEAI", "FEI",
            "Ferrous", "FESI", "Iron Oxide", "KAI1", "KAI2", "KAI3", "LATI",
            "MGAI", "OHI1", "OHI2", "OHI3", "PHAI", "PRAI",
        ],
        "mineral": [
            "MONI", "MUSI", "MAGI", "PHEI",
        ],
        "miscellaneous": [
            "NDBI", "NDBI2", "NDPonI", "NDSI2", "NDMSI", "NDMI", "NMDI",
            "SWI", "WBI", "WRI", "WV-BI", "WV-VI", "WV-II", "WV-NHFD", "WV-SI",
            "WV-WI", "WorldView Built-Up Index", "WorldView Improved Vegetative Index",
            "WorldView New Iron Index", "WorldView Non-Homogeneous Feature Difference",
            "WorldView Soil Index", "WorldView Water Index",
        ],
    }
    
    # Parse from the actual text content
    lines = text.split("\n")
    for line in lines:
        line = line.strip()
        match = re.match(r'^([A-Z][A-Za-z][A-Za-z0-9 /\-]+?)\s*\(([A-Z][A-Za-z0-9/\-]+?)\)', line)
        if match:
            name = match.group(1).strip()
            abbrev = match.group(2).strip()
            
            # Determine category
            category = "Miscellaneous"
            for cat, abbrevs in categories.items():
                if abbrev in abbrevs:
                    category = cat
                    break
            
            category_cn_map = {
                "vegetation": "植被指数",
                "burn": "燃烧指数",
                "geology": "地质指数",
                "mineral": "矿物指数",
                "miscellaneous": "其他指数",
            }
            
            indices.append({
                "abbreviation": abbrev,
                "name": name,
                "category": category.replace("_", " ").title(),
                "category_cn": category_cn_map.get(category, "其他"),
                "source": "ENVI Documentation",
                "url": f"{BASE_URL}/alphabeticallistspectralindices.html",
            })
    
    return indices


def parse_index_detail_page(url, abbrev, name):
    """Parse individual index detail pages"""
    html = fetch_page(url)
    if not html:
        return None
    
    soup = BeautifulSoup(html, "lxml")
    content = soup.find("div", {"id": "content"}) or soup.find("div", class_="content") or soup.find("article") or soup.body
    text = content.get_text(separator="\n") if content else ""
    
    result = {
        "abbreviation": abbrev,
        "name": name,
        "url": url,
        "source": "ENVI Documentation",
    }
    
    # Try to extract formula
    formula_patterns = [
        r'[Ff]ormula[:\s]+(.+?)(?:\n|$)',
        r'[Ee]quation[:\s]+(.+?)(?:\n|$)',
    ]
    for pat in formula_patterns:
        match = re.search(pat, text)
        if match:
            result["formula"] = match.group(1).strip()
            break
    
    # Try to extract reference
    ref_patterns = [
        r'[Rr]eference[:\s]+(.+?)(?:\n\n|\n[A-Z])',
        r'[Rr]eferences[:\s]+(.+?)(?:\n\n|\n[A-Z])',
    ]
    for pat in ref_patterns:
        match = re.search(pat, text, re.DOTALL)
        if match:
            result["reference"] = match.group(1).strip()
            break
    
    return result


def main():
    print("=" * 60)
    print("ENVI Spectral Indices Crawler")
    print("=" * 60)
    
    all_indices = []
    
    # 1. Crawl Narrowband Greenness page
    print("\n[1] Crawling Narrowband Greenness page...")
    url = f"{BASE_URL}/narrowbandgreenness.html"
    html = fetch_page(url)
    if html:
        indices = parse_narrowband_greenness(html)
        print(f"  Found {len(indices)} narrowband greenness indices")
        all_indices.extend(indices)
    
    # 2. Crawl Alphabetical List page
    print("\n[2] Crawling Alphabetical List of Spectral Indices...")
    url = f"{BASE_URL}/alphabeticallistspectralindices.html"
    html = fetch_page(url)
    if html:
        indices = parse_alphabetical_list(html)
        print(f"  Found {len(indices)} total spectral indices")
        all_indices.extend(indices)
    
    # Deduplicate by abbreviation
    seen = set()
    unique_indices = []
    for idx in all_indices:
        key = idx["abbreviation"]
        if key not in seen:
            seen.add(key)
            unique_indices.append(idx)
    
    print(f"\nTotal unique indices: {len(unique_indices)}")
    
    # Categorize
    categories = {}
    for idx in unique_indices:
        cat = idx.get("category", "Unknown")
        if cat not in categories:
            categories[cat] = 0
        categories[cat] += 1
    
    print("\nBy category:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")
    
    # Save results
    output_file = os.path.join(OUTPUT_DIR, "envi_spectral_indices.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(unique_indices, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaved to: {output_file}")
    print("=" * 60)


if __name__ == "__main__":
    main()
