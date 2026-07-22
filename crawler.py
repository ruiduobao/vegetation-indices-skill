#!/usr/bin/env python3
"""Crawler for indexdatabase.de - Vegetation Indices Database"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
import os

BASE_URL = "https://www.indexdatabase.de"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

OUTPUT_DIR = "crawled_data"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def fetch_page(url, retries=3):
    """Fetch a page with retries"""
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=30)
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            print(f"  Error fetching {url}: {e}")
            if attempt < retries - 1:
                time.sleep(2 * (attempt + 1))
    return None


def parse_indices_list(html):
    """Parse the indices list page"""
    soup = BeautifulSoup(html, "lxml")
    table = soup.find("table")
    if not table:
        return [], False
    
    indices = []
    rows = table.find_all("tr")[1:]  # skip header
    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 9:
            continue
        
        link = cols[1].find("a")
        if not link:
            continue
        
        index_id = 0
        href = link.get("href", "")
        match = re.search(r'id=(\d+)', href)
        if match:
            index_id = int(match.group(1))
        
        formula_text = cols[3].get_text(strip=True)
        variables = cols[4].get_text(strip=True) if len(cols) > 4 else ""
        source = cols[5].get_text(strip=True) if len(cols) > 5 else ""
        
        n_sensors = 0
        n_apps = 0
        n_refs = 0
        
        sens_text = cols[6].get_text(strip=True)
        if sens_text.isdigit():
            n_sensors = int(sens_text)
        
        app_text = cols[7].get_text(strip=True)
        if app_text.isdigit():
            n_apps = int(app_text)
        
        ref_text = cols[8].get_text(strip=True)
        if ref_text.isdigit():
            n_refs = int(ref_text)
        
        indices.append({
            "id": index_id,
            "name": link.get_text(strip=True),
            "abbreviation": cols[2].get_text(strip=True),
            "formula": formula_text,
            "variables": variables,
            "source": source,
            "n_sensors": n_sensors,
            "n_applications": n_apps,
            "n_references": n_refs,
        })
    
    # Check if there's a next page
    has_next = False
    soup_obj = BeautifulSoup(html, "lxml")
    # Look for "next Page" link
    for a in soup_obj.find_all("a"):
        title = a.get("title", "")
        if "next Page" in title:
            has_next = True
            break
    
    return indices, has_next


def parse_sensors_list(html):
    """Parse the sensors list page"""
    soup = BeautifulSoup(html, "lxml")
    table = soup.find("table")
    if not table:
        return []
    
    sensors = []
    rows = table.find_all("tr")[1:]
    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 10:
            continue
        
        link = cols[1].find("a")
        if not link:
            continue
        
        sensor_id = 0
        href = link.get("href", "")
        match = re.search(r'id=(\d+)', href)
        if match:
            sensor_id = int(match.group(1))
        
        def get_num(text):
            try:
                return int(text)
            except:
                return 0
        
        sensors.append({
            "id": sensor_id,
            "name": link.get_text(strip=True),
            "n_bands": cols[2].get_text(strip=True),
            "spectrum": cols[3].get_text(strip=True),
            "spatial_resolution": cols[4].get_text(strip=True),
            "inclination": cols[5].get_text(strip=True),
            "platform": cols[6].get_text(strip=True),
            "operator": cols[7].get_text(strip=True),
            "launch_date": cols[8].get_text(strip=True),
            "comment": cols[9].get_text(strip=True) if len(cols) > 9 else "",
            "n_indices": get_num(cols[10].get_text(strip=True)) if len(cols) > 10 else 0,
            "n_applications": get_num(cols[11].get_text(strip=True)) if len(cols) > 11 else 0,
            "n_references": get_num(cols[12].get_text(strip=True)) if len(cols) > 12 else 0,
        })
    
    return sensors


def parse_applications_list(html):
    """Parse the applications list page"""
    soup = BeautifulSoup(html, "lxml")
    table = soup.find("table")
    if not table:
        return []
    
    applications = []
    rows = table.find_all("tr")[1:]
    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 5:
            continue
        
        link = cols[1].find("a")
        if not link:
            continue
        
        app_id = 0
        href = link.get("href", "")
        match = re.search(r'id=(\d+)', href)
        if match:
            app_id = int(match.group(1))
        
        def get_num(text):
            try:
                return int(text)
            except:
                return 0
        
        applications.append({
            "id": app_id,
            "name": link.get_text(strip=True),
            "description": cols[2].get_text(strip=True),
            "n_indices": get_num(cols[3].get_text(strip=True)) if len(cols) > 3 else 0,
            "n_sensors": get_num(cols[4].get_text(strip=True)) if len(cols) > 4 else 0,
            "n_references": get_num(cols[5].get_text(strip=True)) if len(cols) > 5 else 0,
        })
    
    return applications


def crawl_all_indices():
    """Crawl all indices from all pages"""
    print("Crawling indices list...")
    all_indices = []
    page = 1
    has_next = True
    
    while has_next:
        url = f"{BASE_URL}/db/i.php"
        if page > 1:
            url += f"?offset={page}"
        
        print(f"  Fetching page {page}...")
        html = fetch_page(url)
        if not html:
            break
        
        indices, has_next = parse_indices_list(html)
        if not indices:
            break
        
        all_indices.extend(indices)
        print(f"  Got {len(indices)} indices (total: {len(all_indices)}, next={has_next})")
        
        page += 1
        time.sleep(0.5)
    
    print(f"Total indices collected: {len(all_indices)}")
    
    with open(os.path.join(OUTPUT_DIR, "indices_list.json"), "w", encoding="utf-8") as f:
        json.dump(all_indices, f, indent=2, ensure_ascii=False)
    
    return all_indices


def crawl_all_sensors():
    """Crawl all sensors"""
    print("\nCrawling sensors list...")
    url = f"{BASE_URL}/db/s.php"
    html = fetch_page(url)
    if not html:
        return []
    
    sensors = parse_sensors_list(html)
    print(f"Total sensors collected: {len(sensors)}")
    
    with open(os.path.join(OUTPUT_DIR, "sensors_list.json"), "w", encoding="utf-8") as f:
        json.dump(sensors, f, indent=2, ensure_ascii=False)
    
    return sensors


def crawl_all_applications():
    """Crawl all applications"""
    print("\nCrawling applications list...")
    url = f"{BASE_URL}/db/a.php"
    html = fetch_page(url)
    if not html:
        return []
    
    applications = parse_applications_list(html)
    print(f"Total applications collected: {len(applications)}")
    
    with open(os.path.join(OUTPUT_DIR, "applications_list.json"), "w", encoding="utf-8") as f:
        json.dump(applications, f, indent=2, ensure_ascii=False)
    
    return applications


def main():
    print("=" * 60)
    print("IndexDatabase.de Crawler")
    print("=" * 60)
    
    indices = crawl_all_indices()
    sensors = crawl_all_sensors()
    applications = crawl_all_applications()
    
    print("\n" + "=" * 60)
    print(f"Crawling complete!")
    print(f"  Indices: {len(indices)}")
    print(f"  Sensors: {len(sensors)}")
    print(f"  Applications: {len(applications)}")
    print(f"  Data saved to: {OUTPUT_DIR}/")
    print("=" * 60)


if __name__ == "__main__":
    main()
