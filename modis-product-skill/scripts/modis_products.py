#!/usr/bin/env python3
"""MODIS Product Query Tool - Comprehensive NASA MODIS satellite product database query script."""

import json
import os
import sys
from typing import Any, Dict, List, Optional, Tuple


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "data")
PRODUCTS_FILE = os.path.join(DATA_DIR, "products.json")
GEE_CODES_FILE = os.path.join(DATA_DIR, "gee_codes.json")

CATEGORY_MAP = {
    "vegetation_indices": "植被指数",
    "surface_reflectance": "地表反射率",
    "land_surface_temperature": "地表温度",
    "land_cover": "土地覆盖",
    "thermal_anomalies": "热异常/火灾",
    "lai_fpar": "叶面积指数/FPAR",
    "evapotranspiration": "蒸散发",
    "gpp_npp": "总/净初级生产力",
    "brdf_albedo": "BRDF/反照率",
    "vegetation_continuous_fields": "植被连续场",
    "water_mask": "水体掩膜",
    "burned_area": "燃烧面积",
    "snow_cover": "积雪",
}

PLATFORM_MAP = {
    "Terra": "Terra卫星",
    "Aqua": "Aqua卫星",
    "Combined": "Terra+Aqua融合",
}

RESOLUTION_ORDER = ["250m", "500m", "500m/1km", "1km", "0.05°"]


def load_data() -> Tuple[Dict, Dict]:
    """Load products.json and gee_codes.json data files."""
    with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
        products_data = json.load(f)
    with open(GEE_CODES_FILE, "r", encoding="utf-8") as f:
        gee_data = json.load(f)
    return products_data, gee_data


def search_products(query: str, data: Dict, max_results: int = 10) -> List[Dict]:
    """Search products by keyword with scoring. Supports bilingual search."""
    products = data["products"]
    query_lower = query.lower()
    scored_results = []

    cn_category_map = {v: k for k, v in CATEGORY_MAP.items()}
    cn_platform_map = {v: k for k, v in PLATFORM_MAP.items()}

    for product in products:
        score = 0
        pid = product["id"].lower()
        name = product["name"].lower()
        name_cn = product["name_cn"].lower()
        category = product["category"]
        platform = product["platform"]
        resolution = product["resolution"]
        desc = product.get("description", "").lower()
        desc_cn = product.get("description_cn", "").lower()

        if query_lower == pid:
            score = 100
        elif query_lower in pid:
            score = 80
        elif query_lower in name or query_lower in name_cn:
            score = 60
        elif query_lower in category or query_lower in CATEGORY_MAP.get(category, "").lower():
            score = 50
        elif query_lower == CATEGORY_MAP.get(category, "").lower():
            score = 55
        elif query_lower in platform.lower() or query_lower == PLATFORM_MAP.get(platform, "").lower():
            score = 40
        elif query_lower in resolution.lower():
            score = 30
        elif query_lower in desc or query_lower in desc_cn:
            score = 20
        elif query_lower in cn_category_map and cn_category_map[query_lower] == category:
            score = 55
        elif query_lower in cn_platform_map and cn_platform_map[query_lower] == platform:
            score = 40

        for band in product.get("bands", []):
            if query_lower in band.get("name", "").lower() or query_lower in band.get("description_cn", "").lower():
                score = max(score, 25)
                break

        if score > 0:
            scored_results.append((score, product))

    scored_results.sort(key=lambda x: (-x[0], x[1]["id"]))
    return [item[1] for item in scored_results[:max_results]]


def get_product_by_id(product_id: str, data: Dict) -> Optional[Dict]:
    """Look up a product by its ID."""
    for product in data["products"]:
        if product["id"].upper() == product_id.upper():
            return product
    return None


def get_products_by_category(category: str, data: Dict) -> List[Dict]:
    """Filter products by category key or Chinese name."""
    cat_key = category.lower()
    if cat_key not in CATEGORY_MAP:
        for k, v in CATEGORY_MAP.items():
            if v == category:
                cat_key = k
                break
    return [p for p in data["products"] if p["category"].lower() == cat_key]


def get_products_by_platform(platform: str, data: Dict) -> List[Dict]:
    """Filter products by platform (Terra, Aqua, Combined)."""
    platform_lower = platform.lower()
    platform_key = platform_lower
    for k, v in PLATFORM_MAP.items():
        if platform_lower == k.lower() or platform_lower == v.lower():
            platform_key = k.lower()
            break
    return [p for p in data["products"] if p["platform"].lower() == platform_key]


def get_products_by_resolution(resolution: str, data: Dict) -> List[Dict]:
    """Filter products by resolution."""
    results = []
    res_lower = resolution.lower()
    for p in data["products"]:
        if res_lower in p["resolution"].lower():
            results.append(p)
    return results


def format_product_summary(p: Dict) -> str:
    """Format a one-line product summary."""
    cat_cn = CATEGORY_MAP.get(p["category"], p["category"])
    return f"{p['id']:12s} | {p['platform']:8s} | {p['resolution']:10s} | {p['temporal_resolution']:10s} | {cat_cn}"


def format_product_detail(p: Dict) -> str:
    """Format full product details."""
    lines = []
    lines.append("=" * 70)
    lines.append(f"Product ID: {p['id']}")
    lines.append(f"产品名称: {p['name_cn']}")
    lines.append(f"Name: {p['name']}")
    lines.append("-" * 70)
    lines.append(f"Platform/平台: {p['platform']} ({PLATFORM_MAP.get(p['platform'], '')})")
    lines.append(f"Category/类别: {p['category']} ({CATEGORY_MAP.get(p['category'], '')})")
    lines.append(f"Resolution/分辨率: {p['resolution']}")
    lines.append(f"Temporal Resolution/时间分辨率: {p['temporal_resolution']}")
    lines.append(f"Time Range/时间范围: {p['start_date']} ~ {p['end_date']}")
    lines.append(f"Version/版本: v{p['version']}")
    lines.append(f"Stage/阶段: {p['stage']}")
    lines.append(f"PI/首席研究员: {p.get('pi', 'N/A')}")
    lines.append(f"DOI: {p.get('doi', 'N/A')}")
    lines.append(f"GEE Collection: {p.get('gee_collection', 'N/A')}")
    lines.append("")
    lines.append(f"Description: {p.get('description', 'N/A')}")
    lines.append(f"中文介绍: {p.get('description_cn', 'N/A')}")

    if p.get("algorithms"):
        lines.append("")
        lines.append("Algorithms/算法:")
        for algo in p["algorithms"]:
            lines.append(f"  - {algo}")

    if p.get("bands"):
        lines.append("")
        lines.append("Bands/波段:")
        for band in p["bands"]:
            scale_str = f"x{band['scale']}" if band.get("scale", 1) != 1 else ""
            offset_str = f" +{band['offset']}" if band.get("offset") else ""
            wl_str = f" ({band['wavelength']})" if band.get("wavelength") else ""
            unit_str = f" [{band['units']}]" if band.get("units") else ""
            lines.append(f"  {band['name']:30s} {band['dtype']:8s} {scale_str}{offset_str}{unit_str}{wl_str}")
            lines.append(f"    {band.get('description_cn', band.get('description', ''))}")

    if p.get("official_url"):
        lines.append("")
        lines.append(f"Official Page: {p['official_url']}")
    if p.get("download_url"):
        lines.append(f"Download: {p['download_url']}")

    lines.append("=" * 70)
    return "\n".join(lines)


def format_gee_code(product_id: str, data: Dict, gee_data: Dict) -> str:
    """Return GEE code example for a product. Auto-generate if not in gee_codes.json."""
    pid_upper = product_id.upper()

    if pid_upper in gee_data:
        entry = gee_data[pid_upper]
        return (
            f"// {'='*60}\n"
            f"// {entry['description']}\n"
            f"// {entry['description_cn']}\n"
            f"// {'='*60}\n\n"
            f"{entry['code']}\n\n"
            f"{'='*60}\n"
            f"// 中文注释版本:\n"
            f"{'='*60}\n\n"
            f"{entry['code_cn']}"
        )

    product = get_product_by_id(pid_upper, data)
    if not product:
        return f"Product '{product_id}' not found."

    gee_collection = product.get("gee_collection", "N/A")
    bands = product.get("bands", [])
    main_band = bands[0]["name"] if bands else "None"
    resolution = product["resolution"]

    if "250" in resolution:
        scale = 250
    elif "500" in resolution:
        scale = 500
    elif "1km" in resolution or "1 km" in resolution:
        scale = 1000
    elif "0.05" in resolution:
        scale = 5000
    else:
        scale = 500

    auto_code = f"""// {'='*60}
// Auto-generated GEE code for {pid_upper}
// {product.get('description_cn', '')}
// {'='*60}

var collection = ee.ImageCollection('{gee_collection}');

var roi = ee.Geometry.Rectangle([110, 30, 120, 40]);

var filtered = collection
  .filterDate('2020-01-01', '2020-12-31')
  .filterBounds(roi);

print('Number of images:', filtered.size());

var median = filtered.median();
Map.addLayer(median, {{}}, '{pid_upper} Median');
Map.centerObject(roi, 6);
"""

    auto_code_cn = f"""// {'='*60}
// {pid_upper} 自动生成的GEE代码
// {product.get('description_cn', '')}
// {'='*60}

var collection = ee.ImageCollection('{gee_collection}');

// 定义研究区域
var roi = ee.Geometry.Rectangle([110, 30, 120, 40]);

// 筛选数据
var filtered = collection
  .filterDate('2020-01-01', '2020-12-31')
  .filterBounds(roi);

print('影像数量:', filtered.size());

// 可视化
var median = filtered.median();
Map.addLayer(median, {{}}, '{pid_upper} 中值');
Map.centerObject(roi, 6);
"""

    return (
        f"{auto_code}\n\n"
        f"{'='*60}\n"
        f"// 中文注释版本:\n"
        f"{'='*60}\n\n"
        f"{auto_code_cn}"
    )


def format_download_info(product_id: str, data: Dict) -> str:
    """Format download information for a product."""
    product = get_product_by_id(product_id, data)
    if not product:
        return f"Product '{product_id}' not found."

    lines = []
    lines.append(f"Download Information for {product['id']}")
    lines.append(f"{product['name_cn']}")
    lines.append("=" * 50)
    lines.append("")
    lines.append("Official Download Sources:")
    lines.append(f"  1. LAADS DAAC: https://ladsweb.modaps.eosdis.nasa.gov/")
    lines.append(f"  2. NASA Earthdata Search: https://search.earthdata.nasa.gov/")
    lines.append(f"  3. LP DAAC Data Pool: https://e4ftl01.cr.usgs.gov/")
    lines.append("")
    if product.get("download_url"):
        lines.append(f"Direct Download: {product['download_url']}")
    if product.get("doi"):
        lines.append(f"DOI: {product['doi']}")
    lines.append("")
    lines.append("Command Line Download (wget):")
    lines.append(f'  wget --user YOUR_USER --password YOUR_PASS "{product.get("download_url", "URL")}"')
    lines.append("")
    lines.append("Note: NASA Earthdata account required.")
    lines.append("Register at: https://urs.earthdata.nasa.gov/")
    lines.append("")
    lines.append("AppEEARS (area subset): https://appeears.earthdatacloud.nasa.gov/")
    lines.append("Google Earth Engine: Use collection ID directly")
    lines.append(f"  Collection: {product.get('gee_collection', 'N/A')}")

    return "\n".join(lines)


def compare_products(id1: str, id2: str, data: Dict) -> str:
    """Compare two products side-by-side."""
    p1 = get_product_by_id(id1, data)
    p2 = get_product_by_id(id2, data)

    if not p1 or not p2:
        missing = []
        if not p1:
            missing.append(id1)
        if not p2:
            missing.append(id2)
        return f"Product(s) not found: {', '.join(missing)}"

    lines = []
    lines.append("=" * 80)
    lines.append(f"{'Attribute':<25s} | {p1['id']:25s} | {p2['id']:25s}")
    lines.append("-" * 80)

    attrs = [
        ("Name (CN)", "name_cn"),
        ("Platform", "platform"),
        ("Category", "category"),
        ("Resolution", "resolution"),
        ("Temporal Res.", "temporal_resolution"),
        ("Start Date", "start_date"),
        ("End Date", "end_date"),
        ("Version", "version"),
        ("Stage", "stage"),
        ("PI", "pi"),
        ("DOI", "doi"),
        ("GEE Collection", "gee_collection"),
    ]

    for label, key in attrs:
        v1 = p1.get(key, "N/A")
        v2 = p2.get(key, "N/A")
        lines.append(f"{label:<25s} | {v1:<25s} | {v2:<25s}")

    lines.append("-" * 80)
    lines.append(f"{'Bands':<25s} | {', '.join(b['name'] for b in p1.get('bands', []))}")
    lines.append(f"{'':25s} | {', '.join(b['name'] for b in p2.get('bands', []))}")
    lines.append("=" * 80)

    return "\n".join(lines)


def get_statistics(data: Dict) -> Dict:
    """Compute database statistics."""
    products = data["products"]
    stats = {
        "total_products": len(products),
        "categories": {},
        "platforms": {},
        "resolutions": {},
        "versions": {},
        "stages": {},
    }

    for p in products:
        cat = p["category"]
        stats["categories"][cat] = stats["categories"].get(cat, 0) + 1

        plat = p["platform"]
        stats["platforms"][plat] = stats["platforms"].get(plat, 0) + 1

        res = p["resolution"]
        stats["resolutions"][res] = stats["resolutions"].get(res, 0) + 1

        ver = p["version"]
        stats["versions"][ver] = stats["versions"].get(ver, 0) + 1

        stage = p["stage"]
        stats["stages"][stage] = stats["stages"].get(stage, 0) + 1

    return stats


def format_statistics(stats: Dict) -> str:
    """Format database statistics."""
    lines = []
    lines.append("=" * 50)
    lines.append("MODIS Product Database Statistics")
    lines.append("=" * 50)
    lines.append(f"Total Products: {stats['total_products']}")
    lines.append("")

    lines.append("By Category:")
    for cat, count in sorted(stats["categories"].items(), key=lambda x: -x[1]):
        cat_cn = CATEGORY_MAP.get(cat, cat)
        lines.append(f"  {cat:<35s} {cat_cn:<15s} {count:3d} products")

    lines.append("")
    lines.append("By Platform:")
    for plat, count in sorted(stats["platforms"].items(), key=lambda x: -x[1]):
        plat_cn = PLATFORM_MAP.get(plat, plat)
        lines.append(f"  {plat:<20s} {plat_cn:<15s} {count:3d} products")

    lines.append("")
    lines.append("By Resolution:")
    for res, count in sorted(stats["resolutions"].items(), key=lambda x: -x[1]):
        lines.append(f"  {res:<20s} {count:3d} products")

    lines.append("")
    lines.append("By Version:")
    for ver, count in sorted(stats["versions"].items()):
        lines.append(f"  v{ver:<18s} {count:3d} products")

    lines.append("")
    lines.append("By Stage:")
    for stage, count in sorted(stats["stages"].items()):
        lines.append(f"  {stage:<20s} {count:3d} products")

    lines.append("=" * 50)
    return "\n".join(lines)


def list_categories(data: Dict) -> str:
    """List all categories with product counts."""
    products = data["products"]
    cat_counts = {}
    for p in products:
        cat = p["category"]
        cat_counts[cat] = cat_counts.get(cat, 0) + 1

    lines = []
    lines.append("=" * 55)
    lines.append("MODIS Product Categories")
    lines.append("=" * 55)
    lines.append(f"{'Category (EN)':<35s} {'Category (CN)':<15s} {'Count':>5s}")
    lines.append("-" * 55)

    for cat_key, cat_info in data.get("categories", {}).items():
        count = cat_counts.get(cat_key, 0)
        lines.append(f"{cat_info.get('name', cat_key):<35s} {cat_info.get('name_cn', ''):<15s} {count:>5d}")

    lines.append("-" * 55)
    lines.append(f"{'TOTAL':<50s} {len(products):>5d}")
    lines.append("=" * 55)
    return "\n".join(lines)


def show_help() -> str:
    """Return help text."""
    return """
MODIS Product Query Tool | MODIS产品数据查询工具
=================================================

Usage: python modis_products.py <command> [args]

Commands:
  search <keyword> [--limit N]     Search products by keyword (bilingual)
  show <product_id>                Show detailed product information
  gee <product_id>                 Show GEE code example
  download <product_id>            Show download information
  category <category_name>         List products in a category
  categories                       List all categories with counts
  platform <platform>              Filter by platform (Terra/Aqua/Combined)
  resolution <resolution>          Filter by resolution (250m/500m/1km)
  compare <id1> <id2>              Compare two products side-by-side
  stats                            Show database statistics
  help                             Show this help message

Examples:
  python modis_products.py search NDVI
  python modis_products.py search 植被指数
  python modis_products.py show MOD13Q1
  python modis_products.py gee MOD11A1
  python modis_products.py category vegetation_indices
  python modis_products.py platform Terra
  python modis_products.py resolution 500m
  python modis_products.py compare MOD13Q1 MYD13Q1
  python modis_products.py stats
"""


def main(args: Optional[List[str]] = None) -> Any:
    """Main entry point for the MODIS product query tool."""
    if args is None:
        args = sys.argv[1:]

    if not args:
        return {"help": show_help(), "status": "ok"}

    command = args[0].lower()
    data, gee_data = load_data()

    if command == "help":
        return {"help": show_help(), "status": "ok"}

    elif command == "search":
        if len(args) < 2:
            return {"error": "Usage: search <keyword> [--limit N]"}
        query = args[1]
        max_results = 10
        if "--limit" in args:
            idx = args.index("--limit")
            if idx + 1 < len(args):
                max_results = int(args[idx + 1])
        results = search_products(query, data, max_results)
        if not results:
            return {"query": query, "results": [], "message": "No products found."}
        output = f"Search results for '{query}' ({len(results)} found):\n\n"
        for p in results:
            output += format_product_summary(p) + "\n"
        return {"query": query, "results": [p["id"] for p in results], "output": output}

    elif command == "show":
        if len(args) < 2:
            return {"error": "Usage: show <product_id>"}
        product = get_product_by_id(args[1], data)
        if not product:
            return {"error": f"Product '{args[1]}' not found."}
        output = format_product_detail(product)
        return {"product_id": product["id"], "output": output}

    elif command == "gee":
        if len(args) < 2:
            return {"error": "Usage: gee <product_id>"}
        product = get_product_by_id(args[1], data)
        if not product:
            return {"error": f"Product '{args[1]}' not found."}
        output = format_gee_code(product["id"], data, gee_data)
        return {"product_id": product["id"], "output": output}

    elif command == "download":
        if len(args) < 2:
            return {"error": "Usage: download <product_id>"}
        product = get_product_by_id(args[1], data)
        if not product:
            return {"error": f"Product '{args[1]}' not found."}
        output = format_download_info(product["id"], data)
        return {"product_id": product["id"], "output": output}

    elif command == "category":
        if len(args) < 2:
            return {"error": "Usage: category <category_name>"}
        cat_key = args[1].lower()
        valid_cats = list(CATEGORY_MAP.keys()) + list(CATEGORY_MAP.values())
        if cat_key not in [c.lower() for c in valid_cats]:
            return {"error": f"Invalid category. Use 'categories' to list all."}
        results = get_products_by_category(args[1], data)
        if not results:
            return {"category": args[1], "results": [], "message": "No products found."}
        cat_cn = CATEGORY_MAP.get(cat_key, cat_key)
        output = f"Category: {args[1]} ({cat_cn}) - {len(results)} products:\n\n"
        for p in results:
            output += format_product_summary(p) + "\n"
        return {"category": args[1], "results": [p["id"] for p in results], "output": output}

    elif command == "categories":
        output = list_categories(data)
        return {"output": output}

    elif command == "platform":
        if len(args) < 2:
            return {"error": "Usage: platform <Terra|Aqua|Combined>"}
        results = get_products_by_platform(args[1], data)
        if not results:
            return {"platform": args[1], "results": [], "message": "No products found."}
        plat_cn = PLATFORM_MAP.get(args[1].capitalize(), args[1])
        output = f"Platform: {args[1]} ({plat_cn}) - {len(results)} products:\n\n"
        for p in results:
            output += format_product_summary(p) + "\n"
        return {"platform": args[1], "results": [p["id"] for p in results], "output": output}

    elif command == "resolution":
        if len(args) < 2:
            return {"error": "Usage: resolution <250m|500m|1km>"}
        results = get_products_by_resolution(args[1], data)
        if not results:
            return {"resolution": args[1], "results": [], "message": "No products found."}
        output = f"Resolution: {args[1]} - {len(results)} products:\n\n"
        for p in results:
            output += format_product_summary(p) + "\n"
        return {"resolution": args[1], "results": [p["id"] for p in results], "output": output}

    elif command == "compare":
        if len(args) < 3:
            return {"error": "Usage: compare <product_id1> <product_id2>"}
        output = compare_products(args[1], args[2], data)
        return {"products": [args[1], args[2]], "output": output}

    elif command == "stats":
        stats = get_statistics(data)
        output = format_statistics(stats)
        return {"stats": stats, "output": output}

    else:
        return {"error": f"Unknown command: {command}", "help": show_help()}


if __name__ == "__main__":
    result = main()
    print(json.dumps(result, indent=2, ensure_ascii=False))
