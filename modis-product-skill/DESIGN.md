# MODIS Product Data Query Skill - Development Document

## 1. Overview

A comprehensive local query skill for NASA MODIS satellite products, covering all major product categories with bilingual (Chinese/English) descriptions, algorithm principles, data access methods, and Google Earth Engine integration.

## 2. Objectives

- **Complete MODIS product catalog**: Cover all major MODIS product categories (40+ products)
- **Bilingual support**: Chinese/English descriptions for all products
- **Algorithm details**: Include processing algorithms, formulas, and methodology
- **GEE integration**: Provide GEE collection IDs, code examples, band information
- **Data access**: Include download links, access methods, and tools
- **Local tool**: Fully offline-capable after initial data collection

## 3. MODIS Product Categories

### 3.1 Vegetation Indices (MOD13 Series)
| Product ID | Name | Resolution | Temporal | Platform |
|---|---|---|---|---|
| MOD13Q1 | VI 16-Day 250m | 250m | 16-day | Terra |
| MOD13A1 | VI 16-Day 500m | 500m | 16-day | Terra |
| MOD13A2 | VI 16-Day 1km | 1km | 16-day | Terra |
| MOD13A3 | VI Monthly 1km | 1km | Monthly | Terra |
| MYD13Q1 | VI 16-Day 250m | 250m | 16-day | Aqua |
| MYD13A1 | VI 16-Day 500m | 500m | 16-day | Aqua |
| MYD13A2 | VI 16-Day 1km | 1km | 16-day | Aqua |
| MYD13A3 | VI Monthly 1km | 1km | Monthly | Aqua |
| MOD13C1 | VI 16-Day 0.05° | ~5.6km | 16-day | Terra |
| MOD13C2 | VI Monthly 0.05° | ~5.6km | Monthly | Terra |
| MYD13C1 | VI 16-Day 0.05° | ~5.6km | 16-day | Aqua |
| MYD13C2 | VI Monthly 0.05° | ~5.6km | Monthly | Aqua |

### 3.2 Surface Reflectance (MOD09 Series)
| Product ID | Name | Resolution | Temporal |
|---|---|---|---|
| MOD09GA | Surface Reflectance Daily L2G Global 1km/500m | 500m/1km | Daily |
| MOD09GQ | Surface Reflectance Daily L2G Global 250m | 250m | Daily |
| MOD09A1 | Surface Reflectance 8-Day L3 Global 500m | 500m | 8-day |
| MYD09GA | Surface Reflectance Daily (Aqua) | 500m/1km | Daily |
| MYD09GQ | Surface Reflectance Daily 250m (Aqua) | 250m | Daily |
| MYD09A1 | Surface Reflectance 8-Day 500m (Aqua) | 500m | 8-day |

### 3.3 Land Surface Temperature (MOD11 Series)
| Product ID | Name | Resolution | Temporal |
|---|---|---|---|
| MOD11A1 | LST Daily 1km | 1km | Daily |
| MOD11A2 | LST 8-Day 1km | 1km | 8-day |
| MOD11C1 | LST Daily 0.05° | ~5.6km | Daily |
| MYD11A1 | LST Daily 1km (Aqua) | 1km | Daily |
| MYD11A2 | LST 8-Day 1km (Aqua) | 1km | 8-day |

### 3.4 Land Cover (MOD12 Series)
| Product ID | Name | Resolution | Temporal |
|---|---|---|---|
| MOD12Q1 | Land Cover Type Yearly L3 Global 500m | 500m | Yearly |
| MOD12Q2 | Land Cover Dynamics Yearly L3 Global 1km | 1km | Yearly |

### 3.5 LAI/FPAR (MOD15 Series)
| Product ID | Name | Resolution | Temporal |
|---|---|---|---|
| MOD15A2H | LAI/FPAR 8-Day 500m | 500m | 8-day |
| MYD15A2H | LAI/FPAR 8-Day 500m (Aqua) | 500m | 8-day |

### 3.6 Gross Primary Productivity (MOD17 Series)
| Product ID | Name | Resolution | Temporal |
|---|---|---|---|
| MOD17A2H | GPP 8-Day 500m | 500m | 8-day |
| MOD17A3HGF | GPP/NPP Yearly L4 Global 500m | 500m | Yearly |
| MYD17A2H | GPP 8-Day 500m (Aqua) | 500m | 8-day |

### 3.7 Evapotranspiration (MOD16 Series)
| Product ID | Name | Resolution | Temporal |
|---|---|---|---|
| MOD16A2 | ET/PET 8-Day 500m | 500m | 8-day |
| MOD16A3 | ET/PET Yearly 500m | 500m | Yearly |
| MYD16A2 | ET/PET 8-Day 500m (Aqua) | 500m | 8-day |

### 3.8 Thermal Anomalies/Fire (MOD14 Series)
| Product ID | Name | Resolution | Temporal |
|---|---|---|---|
| MOD14A1 | Thermal Anomalies/Fire Daily L3 Global 1km | 1km | Daily |
| MOD14A2 | Thermal Anomalies/Fire 8-Day L3 Global 1km | 1km | 8-day |
| MYD14A1 | Thermal/Fire Daily 1km (Aqua) | 1km | Daily |
| MYD14A2 | Thermal/Fire 8-Day 1km (Aqua) | 1km | 8-day |

### 3.9 Albedo (MCD43 Series)
| Product ID | Name | Resolution | Temporal |
|---|---|---|---|
| MCD43A1 | Albedo Model Parameters 16-Day 500m | 500m | 16-day |
| MCD43A3 | Albedo Daily 500m | 500m | Daily |
| MCD43A4 | Nadir BRDF-Adjusted Reflectance 16-Day 500m | 500m | 16-day |

### 3.10 Water/Other Products
| Product ID | Name | Resolution | Temporal |
|---|---|---|---|
| MOD44W | Land Water Mask L3 Global 250m | 250m | Yearly |
| MOD44B | Vegetation Continuous Fields Yearly L3 Global 250m | 250m | Yearly |

## 4. Data Schema

### 4.1 Product Entry
```json
{
  "product_id": "MOD13Q1",
  "name": "MODIS/Terra Vegetation Indices 16-Day L3 Global 250m SIN Grid",
  "name_cn": "MODIS/Terra 植被指数 16天 L3 全球250米",
  "category": "Vegetation Indices",
  "category_cn": "植被指数",
  "platform": "Terra",
  "spatial_resolution": "250m",
  "temporal_resolution": "16-day",
  "temporal_range": "2000-02-18 ~ present",
  "description": "...",
  "description_cn": "...",
  "algorithm": "...",
  "algorithm_cn": "...",
  "parameters": [...],
  "bands": [...],
  "gee_collection": "MODIS/061/MOD13Q1",
  "gee_bands": [...],
  "download_url": "https://ladsweb.modaps.eosdis.nasa.gov/...",
  "official_url": "https://modis.gsfc.nasa.gov/data/dataprod/mod13.php",
  "citation": "...",
  "doi": "10.5067/MODIS/MOD13Q1.061",
  "version": "061",
  "quality_bands": [...],
  "scale_factor": 0.0001,
  "valid_range": [-2000, 10000]
}
```

### 4.2 Band Entry
```json
{
  "band_name": "NDVI",
  "band_name_cn": "归一化植被指数",
  "description": "Normalized Difference Vegetation Index",
  "description_cn": "归一化植被指数",
  "data_type": "Int16",
  "scale": 0.0001,
  "valid_range": [-2000, 10000],
  "units": "unitless",
  "fill_value": -3000
}
```

### 4.3 GEE Code Example
```json
{
  "product_id": "MOD13Q1",
  "code_example": "var modisNDVI = ee.ImageCollection('MODIS/061/MOD13Q1')...",
  "code_example_cn": "// MODIS NDVI 数据获取示例..."
}
```

## 5. Skill Structure

```
modis-product-skill/
├── _meta.json              # Skill metadata
├── SKILL.md                # Skill documentation
├── main.py                 # Entry point
├── scripts/
│   └── modis_products.py  # Main query script
├── data/
│   ├── products.json       # All MODIS products
│   ├── categories.json     # Product categories
│   ├── gee_codes.json      # GEE code examples
│   └── bands.json          # Band details
└── references/
    └── urls.json           # Official URLs
```

## 6. Query Capabilities

| Command | Description |
|---|---|
| `search <query>` | Search products by name/category/parameter |
| `show <product_id>` | Show detailed product information |
| `category <name>` | List products in a category |
| `gee <product_id>` | Show GEE collection ID and code example |
| `bands <product_id>` | Show band details |
| `download <product_id>` | Show download information |
| `categories` | List all product categories |
| `platform <name>` | Filter by platform (Terra/Aqua/Combined) |
| `resolution <res>` | Filter by resolution |
| `stats` | Show database statistics |
| `compare <id1> <id2>` | Compare two products |

## 7. Data Sources

1. **NASA MODIS Product Table**: https://modis.gsfc.nasa.gov/data/dataprod/
2. **LP DAAC**: https://lpdaac.usgs.gov/product_search/?collections=MODIS&status=Operational
3. **GEE Data Catalog**: https://developers.google.com/earth-engine/datasets/catalog/modis
4. **MODIS User Guides**: https://lpdaac.usgs.gov/documents/
5. **NASA Earthdata**: https://earthdata.nasa.gov/

## 8. Development Phases

### Phase 1: Data Collection
- Crawl official MODIS product pages
- Collect product metadata, descriptions, algorithms
- Gather GEE collection information
- Compile band details

### Phase 2: Data Processing
- Structure data into JSON schema
- Add Chinese translations
- Create GEE code examples
- Validate data completeness

### Phase 3: Skill Development
- Implement query script
- Add search/filter capabilities
- Implement GEE code generation
- Add bilingual output

### Phase 4: Testing & Documentation
- Test all query commands
- Write SKILL.md
- Validate output format
- Performance testing

### Phase 5: Publishing
- Sync to GitHub
- Sync to ClawHub
- Create release

## 9. Key Design Decisions

1. **Local-first**: All data stored locally, no API calls needed
2. **Bilingual**: All descriptions in Chinese and English
3. **GEE-ready**: Include ready-to-use GEE code examples
4. **Comprehensive**: Cover all major MODIS products (40+)
5. **Structured**: Clean JSON schema for easy querying
6. **Extensible**: Easy to add new products or update existing ones
