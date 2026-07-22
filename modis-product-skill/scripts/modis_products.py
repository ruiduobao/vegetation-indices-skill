#!/usr/bin/env python3
"""
MODIS Product Data Query Tool
MODIS产品数据查询工具

Query NASA MODIS satellite product information including:
- Product details and descriptions (bilingual)
- Algorithm principles and formulas
- Band information and scale factors
- Google Earth Engine integration
- Download information and citations

Data source: NASA MODIS Web (https://modis.gsfc.nasa.gov/data/dataprod/)
GEE Catalog: https://developers.google.com/earth-engine/datasets/catalog/modis
"""

import json
import os
import re
import sys


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "data")

# Chinese category name mapping
CATEGORY_ZH = {
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

# Platform Chinese names
PLATFORM_ZH = {
    "Terra": "Terra卫星",
    "Aqua": "Aqua卫星",
    "Combined Terra+Aqua": "Terra+Aqua联合",
}

# Validation stage descriptions
STAGE_DESC = {
    "Stage 1": "最小验证/概念验证",
    "Stage 2": "广泛验证",
    "Stage 3": "高质量/全面验证",
    "Provisional": "临时产品",
}


def load_data():
    """Load all data files"""
    data = {}
    for fname in ["products.json", "gee_codes.json"]:
        fpath = os.path.join(DATA_DIR, fname)
        if os.path.exists(fpath):
            with open(fpath, "r", encoding="utf-8") as f:
                key = fname.replace(".json", "")
                data[key] = json.load(f)
    return data


def search_products(query, data, max_results=10):
    """Search products by keyword"""
    query_lower = query.lower()
    results = []

    for p in data.get("products", {}).get("products", []):
        score = 0
        pid = p.get("product_id", "").lower()
        name = p.get("name", "").lower()
        name_cn = p.get("name_cn", "").lower()
        cat = p.get("category", "").lower()
        cat_zh = CATEGORY_ZH.get(p.get("category", ""), "").lower()
        desc = p.get("description", "").lower()
        desc_cn = p.get("description_cn", "").lower()

        # Exact product ID match
        if query_lower == pid:
            score = 100
        # Product ID starts with query
        elif pid.startswith(query_lower):
            score = 90
        # Product ID contains query
        elif query_lower in pid:
            score = 80
        # Name contains query
        elif query_lower in name:
            score = 70
        # Chinese name contains query
        elif query_lower in name_cn:
            score = 65
        # Category match
        elif query_lower in cat or query_lower in cat_zh:
            score = 50
        # Description contains query
        elif query_lower in desc or query_lower in desc_cn:
            score = 30
        # Applications match
        elif any(query_lower in app.lower() for app in p.get("applications", []) + p.get("applications_en", [])):
            score = 25

        if score > 0:
            results.append((score, p))

    results.sort(key=lambda x: (-x[0], x[1].get("product_id", "")))
    return [p for _, p in results[:max_results]]


def get_product_by_id(product_id, data):
    """Get product by ID"""
    for p in data.get("products", {}).get("products", []):
        if p["product_id"].upper() == product_id.upper():
            return p
    return None


def get_products_by_category(category, data):
    """Get all products in a category"""
    results = []
    for p in data.get("products", {}).get("products", []):
        if p.get("category", "").lower() == category.lower():
            results.append(p)
    return results


def get_products_by_platform(platform, data):
    """Filter products by platform"""
    results = []
    platform_lower = platform.lower()
    for p in data.get("products", {}).get("products", []):
        p_platform = p.get("platform", "").lower()
        if platform_lower in p_platform or p_platform in platform_lower:
            results.append(p)
    return results


def get_products_by_resolution(resolution, data):
    """Filter products by resolution"""
    results = []
    res_lower = resolution.lower()
    for p in data.get("products", {}).get("products", []):
        p_res = p.get("spatial_resolution", "").lower()
        if res_lower in p_res:
            results.append(p)
    return results


def format_product_summary(p):
    """Format product summary"""
    lines = []
    lines.append(f"  ID: {p.get('product_id', 'N/A')}")
    lines.append(f"  Name: {p.get('name', 'N/A')}")
    lines.append(f"  名称: {p.get('name_cn', 'N/A')}")
    lines.append(f"  Category/C类别: {CATEGORY_ZH.get(p.get('category', ''), p.get('category', 'N/A'))}")
    lines.append(f"  Platform/平台: {PLATFORM_ZH.get(p.get('platform', ''), p.get('platform', 'N/A'))}")
    lines.append(f"  Resolution/分辨率: {p.get('spatial_resolution', 'N/A')} / {p.get('temporal_resolution', 'N/A')}")
    lines.append(f"  GEE Collection: {p.get('gee_collection', 'N/A')}")
    return "\n".join(lines)


def format_product_detail(p):
    """Format detailed product information"""
    lines = []
    lines.append("=" * 70)
    lines.append(f"Product ID: {p.get('product_id', 'N/A')}")
    lines.append(f"产品名称: {p.get('name_cn', 'N/A')}")
    lines.append(f"Product Name: {p.get('name', 'N/A')}")
    lines.append("=" * 70)
    lines.append("")

    # Basic info
    lines.append("[Basic Info / 基本信息]")
    lines.append(f"  Category/类别: {CATEGORY_ZH.get(p.get('category', ''), p.get('category', 'N/A'))} ({p.get('category', 'N/A')})")
    lines.append(f"  Platform/平台: {PLATFORM_ZH.get(p.get('platform', ''), p.get('platform', 'N/A'))}")
    lines.append(f"  Spatial Resolution/空间分辨率: {p.get('spatial_resolution', 'N/A')}")
    lines.append(f"  Temporal Resolution/时间分辨率: {p.get('temporal_resolution', 'N/A')}")
    lines.append(f"  Temporal Range/时间范围: {p.get('temporal_range', 'N/A')}")
    lines.append(f"  Version/版本: {p.get('version', 'N/A')}")
    lines.append(f"  Validation Stage/验证等级: {p.get('validated_stage', 'N/A')} ({STAGE_DESC.get(p.get('validated_stage', ''), '')})")
    lines.append("")

    # Description
    lines.append("[Description / 产品介绍]")
    lines.append(f"  EN: {p.get('description', 'N/A')}")
    lines.append(f"  CN: {p.get('description_cn', 'N/A')}")
    lines.append("")

    # Algorithm
    if p.get("algorithm"):
        lines.append("[Algorithm / 算法原理]")
        lines.append(f"  EN: {p.get('algorithm', 'N/A')}")
        if p.get("algorithm_cn"):
            lines.append(f"  CN: {p.get('algorithm_cn', 'N/A')}")
        lines.append("")

    # Formulas
    if p.get("ndvi_formula") or p.get("evi_formula"):
        lines.append("[Formulas / 公式]")
        if p.get("ndvi_formula"):
            lines.append(f"  NDVI: {p['ndvi_formula']}")
        if p.get("evi_formula"):
            lines.append(f"  EVI: {p['evi_formula']}")
        lines.append("")

    # Bands
    if p.get("bands"):
        lines.append("[Bands / 波段信息]")
        for b in p["bands"]:
            line = f"  {b.get('name', 'N/A')} ({b.get('name_cn', '')})"
            if b.get("type"):
                line += f" | Type: {b['type']}"
            if b.get("scale"):
                line += f" | Scale: {b['scale']}"
            if b.get("wavelength"):
                line += f" | λ: {b['wavelength']}"
            if b.get("units"):
                line += f" | Units: {b['units']}"
            if b.get("description"):
                line += f" | {b['description']}"
            lines.append(line)
        lines.append("")

    # Quality bands
    if p.get("quality_bands"):
        lines.append("[Quality Information / 质量信息]")
        for qb in p["quality_bands"]:
            bit_info = qb.get("bits", qb.get("bit", ""))
            lines.append(f"  Bits {bit_info}: {qb.get('meaning', '')}")
        lines.append("")

    # GEE Integration
    if p.get("gee_collection"):
        lines.append("[Google Earth Engine / GEE集成]")
        lines.append(f"  Collection ID: {p['gee_collection']}")
        if p.get("gee_bands"):
            lines.append(f"  Bands: {', '.join(p['gee_bands'][:10])}")
            if len(p.get("gee_bands", [])) > 10:
                lines.append(f"  ... and {len(p['gee_bands']) - 10} more bands")
        lines.append("")

    # Applications
    if p.get("applications"):
        lines.append("[Applications / 应用领域]")
        for i, app in enumerate(p.get("applications", [])):
            app_en = p.get("applications_en", [])[i] if i < len(p.get("applications_en", [])) else ""
            lines.append(f"  {app} ({app_en})")
        lines.append("")

    # Links
    lines.append("[Links / 相关链接]")
    lines.append(f"  Official Page: {p.get('official_url', 'N/A')}")
    lines.append(f"  Download: {p.get('download_url', 'N/A')}")
    lines.append(f"  DOI: {p.get('doi', 'N/A')}")
    if p.get("atbd_url"):
        lines.append(f"  ATBD: {p['atbd_url']}")
    if p.get("user_guide"):
        lines.append(f"  User Guide: {p['user_guide']}")
    lines.append("")

    # Citation
    if p.get("citation"):
        lines.append("[Citation / 引用]")
        lines.append(f"  {p['citation']}")
        lines.append("")

    # PI info
    if p.get("pi"):
        lines.append("[Principal Investigator / 首席科学家]")
        lines.append(f"  {p.get('pi', 'N/A')}")
        if p.get("pi_url"):
            lines.append(f"  URL: {p['pi_url']}")
        lines.append("")

    return "\n".join(lines)


def format_gee_code(product_id, data):
    """Format GEE code example"""
    gee_codes = data.get("gee_codes", {})
    if product_id.upper() in gee_codes:
        code_info = gee_codes[product_id.upper()]
        lines = []
        lines.append("=" * 70)
        lines.append(f"GEE Code Example for {product_id}")
        lines.append(f"GEE代码示例 - {code_info.get('description_cn', '')}")
        lines.append("=" * 70)
        lines.append("")
        lines.append("[English Version]")
        lines.append("```javascript")
        lines.append(code_info.get("code", "No code example available"))
        lines.append("```")
        lines.append("")
        lines.append("[中文版]")
        lines.append("```javascript")
        lines.append(code_info.get("code_cn", "暂无中文代码示例"))
        lines.append("```")
        return "\n".join(lines)
    else:
        # Generate basic GEE code
        p = get_product_by_id(product_id, data)
        if p and p.get("gee_collection"):
            coll = p["gee_collection"]
            lines = []
            lines.append("=" * 70)
            lines.append(f"GEE Code Example for {product_id} (Auto-generated)")
            lines.append(f"GEE代码示例 - {p.get('name_cn', '')} (自动生成)")
            lines.append("=" * 70)
            lines.append("")
            lines.append("```javascript")
            lines.append(f"// Load {product_id} data from GEE")
            lines.append(f"var collection = ee.ImageCollection('{coll}');")
            lines.append(f"")
            lines.append(f"// Define region of interest")
            lines.append(f"var roi = ee.Geometry.Rectangle([100, 30, 110, 40]);")
            lines.append(f"")
            lines.append(f"// Filter by date and region")
            lines.append(f"var filtered = collection")
            lines.append(f"  .filterDate('2020-01-01', '2020-12-31')")
            lines.append(f"  .filterBounds(roi);")
            lines.append(f"")
            lines.append(f"print('Collection size:', filtered.size());")
            lines.append(f"Map.centerObject(roi, 6);")
            lines.append("```")
            return "\n".join(lines)
        return f"No GEE collection found for {product_id}"


def format_download_info(product_id, data):
    """Format download information"""
    p = get_product_by_id(product_id, data)
    if not p:
        return f"Product {product_id} not found"

    lines = []
    lines.append("=" * 70)
    lines.append(f"Download Information for {product_id}")
    lines.append(f"{product_id} 下载信息")
    lines.append("=" * 70)
    lines.append("")
    lines.append(f"Product: {p.get('name', 'N/A')}")
    lines.append(f"产品: {p.get('name_cn', 'N/A')}")
    lines.append("")
    lines.append("[Download Methods / 下载方式]")
    lines.append(f"  1. NASA Earthdata Search:")
    lines.append(f"     https://search.earthdata.nasa.gov/search")
    lines.append(f"  2. Direct DAAC Link:")
    lines.append(f"     {p.get('download_url', 'N/A')}")
    lines.append(f"  3. LP DAAC Data Pool:")
    lines.append(f"     https://e4ftl01.cr.usgs.gov/")
    lines.append(f"  4. AppEEARS (subset/extract):")
    lines.append(f"     https://appeears.earthdatacloud.nasa.gov/")
    lines.append(f"  5. Google Earth Engine:")
    lines.append(f"     Collection: {p.get('gee_collection', 'N/A')}")
    lines.append(f"     https://developers.google.com/earth-engine/datasets")
    lines.append("")
    lines.append("[Requirements / 要求]")
    lines.append("  - NASA Earthdata account required for download")
    lines.append("  - 下载需要NASA Earthdata账号")
    lines.append("  - Register at: https://urs.earthdata.nasa.gov/")
    lines.append("")
    if p.get("doi"):
        lines.append(f"[DOI / 数字对象标识符]")
        lines.append(f"  {p['doi']}")
        lines.append("")
    return "\n".join(lines)


def compare_products(id1, id2, data):
    """Compare two products"""
    p1 = get_product_by_id(id1, data)
    p2 = get_product_by_id(id2, data)

    if not p1 or not p2:
        missing = []
        if not p1:
            missing.append(id1)
        if not p2:
            missing.append(id2)
        return f"Products not found: {', '.join(missing)}"

    lines = []
    lines.append("=" * 70)
    lines.append(f"Product Comparison: {id1} vs {id2}")
    lines.append(f"产品对比: {id1} 与 {id2}")
    lines.append("=" * 70)
    lines.append("")

    # Comparison table
    attrs = [
        ("Product ID", "product_id"),
        ("Name", "name"),
        ("名称", "name_cn"),
        ("Category", "category"),
        ("Platform", "platform"),
        ("Spatial Resolution", "spatial_resolution"),
        ("Temporal Resolution", "temporal_resolution"),
        ("Temporal Range", "temporal_range"),
        ("Version", "version"),
        ("Validation", "validated_stage"),
        ("GEE Collection", "gee_collection"),
        ("DOI", "doi"),
    ]

    for label, key in attrs:
        v1 = p1.get(key, "N/A")
        v2 = p2.get(key, "N/A")
        if key == "category":
            v1 = CATEGORY_ZH.get(v1, v1)
            v2 = CATEGORY_ZH.get(v2, v2)
        elif key == "platform":
            v1 = PLATFORM_ZH.get(v1, v1)
            v2 = PLATFORM_ZH.get(v2, v2)
        lines.append(f"  {label:25s} | {v1:30s} | {v2}")

    lines.append("")
    lines.append(f"  {'Bands Count':25s} | {len(p1.get('bands', [])):30d} | {len(p2.get('bands', []))}")

    return "\n".join(lines)


def get_statistics(data):
    """Get database statistics"""
    products = data.get("products", {}).get("products", [])
    categories = data.get("products", {}).get("categories", [])

    stats = {
        "total_products": len(products),
        "total_categories": len(categories),
        "by_platform": {},
        "by_category": {},
        "by_resolution": {},
        "by_temporal": {},
        "gee_available": 0,
        "with_code_examples": len(data.get("gee_codes", {})),
    }

    for p in products:
        # By platform
        plat = p.get("platform", "Unknown")
        stats["by_platform"][plat] = stats["by_platform"].get(plat, 0) + 1

        # By category
        cat = p.get("category", "Unknown")
        cat_zh = CATEGORY_ZH.get(cat, cat)
        stats["by_category"][cat_zh] = stats["by_category"].get(cat_zh, 0) + 1

        # By resolution
        res = p.get("spatial_resolution", "Unknown")
        stats["by_resolution"][res] = stats["by_resolution"].get(res, 0) + 1

        # By temporal
        tres = p.get("temporal_resolution", "Unknown")
        stats["by_temporal"][tres] = stats["by_temporal"].get(tres, 0) + 1

        # GEE available
        if p.get("gee_collection"):
            stats["gee_available"] += 1

    return stats


def format_statistics(stats):
    """Format statistics output"""
    lines = []
    lines.append("=" * 70)
    lines.append("MODIS Product Database Statistics")
    lines.append("MODIS产品数据库统计")
    lines.append("=" * 70)
    lines.append("")
    lines.append(f"Total Products / 产品总数: {stats['total_products']}")
    lines.append(f"Total Categories / 类别总数: {stats['total_categories']}")
    lines.append(f"GEE Available / GEE可用: {stats['gee_available']}")
    lines.append(f"Code Examples / 代码示例: {stats['with_code_examples']}")
    lines.append("")

    lines.append("[By Platform / 按平台]")
    for plat, count in sorted(stats["by_platform"].items(), key=lambda x: -x[1]):
        plat_zh = PLATFORM_ZH.get(plat, plat)
        lines.append(f"  {plat} ({plat_zh}): {count}")
    lines.append("")

    lines.append("[By Category / 按类别]")
    for cat, count in sorted(stats["by_category"].items(), key=lambda x: -x[1]):
        lines.append(f"  {cat}: {count}")
    lines.append("")

    lines.append("[By Resolution / 按分辨率]")
    for res, count in sorted(stats["by_resolution"].items(), key=lambda x: -x[1]):
        lines.append(f"  {res}: {count}")
    lines.append("")

    lines.append("[By Temporal Resolution / 按时间分辨率]")
    for tres, count in sorted(stats["by_temporal"].items(), key=lambda x: -x[1]):
        lines.append(f"  {tres}: {count}")

    return "\n".join(lines)


def list_categories(data):
    """List all categories"""
    categories = data.get("products", {}).get("categories", [])
    products = data.get("products", {}).get("products", [])

    lines = []
    lines.append("=" * 70)
    lines.append("MODIS Product Categories / MODIS产品类别")
    lines.append("=" * 70)
    lines.append("")

    for cat in categories:
        cat_id = cat.get("id", "")
        cat_name = cat.get("name", "")
        cat_name_cn = cat.get("name_cn", "")
        cat_desc = cat.get("description", "")
        cat_desc_cn = cat.get("description_cn", "")
        icon = cat.get("icon", "")

        # Count products in this category
        count = sum(1 for p in products if p.get("category") == cat_id)

        lines.append(f"{icon} {cat_name} ({cat_name_cn})")
        lines.append(f"   ID: {cat_id}")
        lines.append(f"   EN: {cat_desc}")
        lines.append(f"   CN: {cat_desc_cn}")
        lines.append(f"   Products / 产品数: {count}")
        lines.append("")

    return "\n".join(lines)


def main(args=None):
    """Main entry point"""
    if args is None:
        args = sys.argv[1:]

    if not args:
        return {
            "success": False,
            "message": "MODIS Product Query Tool / MODIS产品查询工具\n"
                       "Commands / 命令:\n"
                       "  search <keyword> [--limit N]     Search products / 搜索产品\n"
                       "  show <product_id>                Show product details / 查看产品详情\n"
                       "  gee <product_id>                 Show GEE code example / 显示GEE代码\n"
                       "  download <product_id>            Show download info / 显示下载信息\n"
                       "  category <name>                  List products in category / 列出类别产品\n"
                       "  categories                       List all categories / 列出所有类别\n"
                       "  platform <name>                  Filter by platform / 按平台筛选\n"
                       "  resolution <res>                 Filter by resolution / 按分辨率筛选\n"
                       "  compare <id1> <id2>              Compare two products / 对比两个产品\n"
                       "  stats                            Database statistics / 数据库统计\n"
                       "  help                             Show help / 显示帮助",
        }

    data = load_data()
    command = args[0].lower()

    if command == "search":
        if len(args) < 2:
            return {"success": False, "message": "Usage: search <keyword> [--limit N]"}

        max_results = 10
        query_parts = []
        i = 1
        while i < len(args):
            if args[i] == "--limit" and i + 1 < len(args):
                try:
                    max_results = int(args[i + 1])
                except ValueError:
                    pass
                i += 2
            else:
                query_parts.append(args[i])
                i += 1

        query = " ".join(query_parts)
        if not query:
            return {"success": False, "message": "Usage: search <keyword>"}

        results = search_products(query, data, max_results)

        if not results:
            return {
                "success": True,
                "query": query,
                "num_results": 0,
                "results": [],
                "message": f"No products found for '{query}' / 未找到与'{query}'相关的产品",
                "suggestion": "Try broader keywords like 'NDVI', 'LST', 'reflectance', 'fire', 'snow'",
            }

        output_lines = [f"Found {len(results)} products for '{query}':\n"]
        for p in results:
            output_lines.append(format_product_summary(p))
            output_lines.append("")

        return {
            "success": True,
            "query": query,
            "num_results": len(results),
            "results": [{"product_id": p.get("product_id"), "name": p.get("name"), "name_cn": p.get("name_cn"), "category": CATEGORY_ZH.get(p.get("category", ""), p.get("category", "")), "platform": p.get("platform"), "resolution": f"{p.get('spatial_resolution')} / {p.get('temporal_resolution')}", "gee_collection": p.get("gee_collection")} for p in results],
            "message": "\n".join(output_lines),
        }

    elif command == "show":
        if len(args) < 2:
            return {"success": False, "message": "Usage: show <product_id>"}

        product_id = args[1]
        p = get_product_by_id(product_id, data)

        if not p:
            return {
                "success": False,
                "message": f"Product '{product_id}' not found / 未找到产品 '{product_id}'",
                "suggestion": "Use 'search <keyword>' to find products / 使用'search <关键词>'查找产品",
            }

        return {
            "success": True,
            "product": p,
            "message": format_product_detail(p),
        }

    elif command == "gee":
        if len(args) < 2:
            return {"success": False, "message": "Usage: gee <product_id>"}

        product_id = args[1]
        p = get_product_by_id(product_id, data)

        if not p:
            return {"success": False, "message": f"Product '{product_id}' not found"}

        return {
            "success": True,
            "product_id": product_id,
            "gee_collection": p.get("gee_collection", "N/A"),
            "message": format_gee_code(product_id, data),
        }

    elif command == "download":
        if len(args) < 2:
            return {"success": False, "message": "Usage: download <product_id>"}

        product_id = args[1]
        p = get_product_by_id(product_id, data)

        if not p:
            return {"success": False, "message": f"Product '{product_id}' not found"}

        return {
            "success": True,
            "product_id": product_id,
            "message": format_download_info(product_id, data),
        }

    elif command == "category":
        if len(args) < 2:
            return {"success": False, "message": "Usage: category <category_name>"}

        cat_name = args[1].lower()
        results = get_products_by_category(cat_name, data)

        if not results:
            # Try Chinese name
            for cat_id, cat_zh in CATEGORY_ZH.items():
                if cat_name in cat_zh.lower():
                    results = get_products_by_category(cat_id, data)
                    break

        if not results:
            return {
                "success": False,
                "message": f"No products in category '{args[1]}' / 类别'{args[1]}'中无产品",
                "available_categories": list(CATEGORY_ZH.values()),
            }

        output_lines = [f"Products in category '{args[1]}' ({len(results)}):\n"]
        for p in results:
            output_lines.append(format_product_summary(p))
            output_lines.append("")

        return {
            "success": True,
            "category": args[1],
            "num_results": len(results),
            "results": [{"product_id": p.get("product_id"), "name": p.get("name_cn"), "resolution": p.get("spatial_resolution")} for p in results],
            "message": "\n".join(output_lines),
        }

    elif command == "categories":
        return {
            "success": True,
            "categories": data.get("products", {}).get("categories", []),
            "message": list_categories(data),
        }

    elif command == "platform":
        if len(args) < 2:
            return {"success": False, "message": "Usage: platform <Terra|Aqua|Combined>"}

        platform = args[1]
        results = get_products_by_platform(platform, data)

        if not results:
            return {"success": False, "message": f"No products for platform '{platform}'"}

        output_lines = [f"Products for platform '{platform}' ({len(results)}):\n"]
        for p in results:
            output_lines.append(f"  {p.get('product_id'):12s} | {p.get('name_cn', 'N/A'):40s} | {p.get('spatial_resolution'):8s}")
        output_lines.append("")

        return {
            "success": True,
            "platform": platform,
            "num_results": len(results),
            "results": [{"product_id": p.get("product_id"), "name": p.get("name_cn")} for p in results],
            "message": "\n".join(output_lines),
        }

    elif command == "resolution":
        if len(args) < 2:
            return {"success": False, "message": "Usage: resolution <250m|500m|1km|0.05°>"}

        res = args[1]
        results = get_products_by_resolution(res, data)

        if not results:
            return {"success": False, "message": f"No products with resolution '{res}'"}

        output_lines = [f"Products with resolution '{res}' ({len(results)}):\n"]
        for p in results:
            output_lines.append(f"  {p.get('product_id'):12s} | {p.get('name_cn', 'N/A'):40s} | {CATEGORY_ZH.get(p.get('category', ''), '')}")

        return {
            "success": True,
            "resolution": res,
            "num_results": len(results),
            "results": [{"product_id": p.get("product_id"), "name": p.get("name_cn")} for p in results],
            "message": "\n".join(output_lines),
        }

    elif command == "compare":
        if len(args) < 3:
            return {"success": False, "message": "Usage: compare <product_id1> <product_id2>"}

        id1, id2 = args[1], args[2]
        return {
            "success": True,
            "product1": id1,
            "product2": id2,
            "message": compare_products(id1, id2, data),
        }

    elif command == "stats":
        stats = get_statistics(data)
        return {
            "success": True,
            "statistics": stats,
            "message": format_statistics(stats),
        }

    elif command == "help":
        return {
            "success": True,
            "message": "MODIS Product Query Tool / MODIS产品查询工具\n"
                       "========================================\n"
                       "Commands / 命令:\n"
                       "  search <keyword> [--limit N]     Search products by keyword / 按关键词搜索产品\n"
                       "  show <product_id>                Show detailed product info / 查看产品详细信息\n"
                       "  gee <product_id>                 Show GEE code example / 显示GEE代码示例\n"
                       "  download <product_id>            Show download information / 显示下载信息\n"
                       "  category <name>                  List products in category / 列出类别中的产品\n"
                       "  categories                       List all categories / 列出所有类别\n"
                       "  platform <name>                  Filter by platform / 按平台筛选\n"
                       "  resolution <res>                 Filter by resolution / 按分辨率筛选\n"
                       "  compare <id1> <id2>              Compare two products / 对比两个产品\n"
                       "  stats                            Database statistics / 数据库统计\n"
                       "  help                             Show this help / 显示帮助\n"
                       "\n"
                       "Examples / 示例:\n"
                       "  python modis_products.py search NDVI\n"
                       "  python modis_products.py search 植被指数\n"
                       "  python modis_products.py show MOD13Q1\n"
                       "  python modis_products.py gee MOD13Q1\n"
                       "  python modis_products.py download MOD13Q1\n"
                       "  python modis_products.py category vegetation_indices\n"
                       "  python modis_products.py platform Terra\n"
                       "  python modis_products.py resolution 250m\n"
                       "  python modis_products.py compare MOD13Q1 MYD13Q1\n"
                       "  python modis_products.py stats",
        }

    else:
        return {
            "success": False,
            "message": f"Unknown command: '{command}'. Use 'help' for usage.",
        }


if __name__ == "__main__":
    result = main()
    print(json.dumps(result, indent=2, ensure_ascii=False))
