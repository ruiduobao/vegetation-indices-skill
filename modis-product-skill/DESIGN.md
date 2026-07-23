# MODIS Product Skill - Design Document

## 1. Skill Overview and Objectives

### Overview
The MODIS Product Skill is a comprehensive local query tool for NASA MODIS satellite products. It provides researchers, students, and remote sensing practitioners with quick access to detailed product metadata, algorithm information, Google Earth Engine integration, and download resources.

### Objectives
- **Comprehensive Coverage**: Include all major MODIS land products across 13 categories
- **Bilingual Support**: Full Chinese and English descriptions for all products
- **GEE Integration**: Ready-to-use Google Earth Engine code examples for common workflows
- **Search Capability**: Smart scoring-based search supporting both English and Chinese keywords
- **Offline Operation**: Fully functional without internet connection (data stored locally)
- **Extensibility**: Easy to update with new products or modify existing data

## 2. MODIS Product Categories

The database covers 13 categories with a total of 46 products:

| # | Category | Chinese | Count | Key Products |
|---|----------|---------|-------|--------------|
| 1 | Vegetation Indices | 植被指数 | 12 | MOD13Q1, MOD13A1, MOD13A2, MOD13A3 |
| 2 | Surface Reflectance | 地表反射率 | 5 | MOD09GA, MOD09GQ, MOD09A1, MYD09A1 |
| 3 | Land Surface Temperature | 地表温度 | 4 | MOD11A1, MOD11A2, MYD11A1, MYD11A2 |
| 4 | Land Cover | 土地覆盖 | 2 | MCD12Q1, MCD12Q2 |
| 5 | Thermal Anomalies/Fire | 热异常/火灾 | 4 | MOD14A1, MOD14A2, MYD14A1, MYD14A2 |
| 6 | LAI/FPAR | 叶面积指数/FPAR | 4 | MOD15A2H, MYD15A2H, MCD15A2H, MCD15A3H |
| 7 | Evapotranspiration | 蒸散发 | 3 | MOD16A2, MYD16A2, MOD16A3 |
| 8 | GPP/NPP | 总/净初级生产力 | 3 | MOD17A2H, MYD17A2H, MOD17A3HGF |
| 9 | BRDF/Albedo | BRDF/反照率 | 3 | MCD43A1, MCD43A3, MCD43A4 |
| 10 | Vegetation Continuous Fields | 植被连续场 | 1 | MOD44B |
| 11 | Water Mask | 水体掩膜 | 1 | MOD44W |
| 12 | Burned Area | 燃烧面积 | 1 | MCD64A1 |
| 13 | Snow Cover | 积雪 | 3 | MOD10A1, MYD10A1, MOD10A2 |

## 3. Data Schema

### 3.1 Product Entry

```json
{
  "id": "MOD13Q1",                    // Product identifier
  "name": "MODIS/Terra Vegetation Indices 16-Day L3 Global 250m",  // English name
  "name_cn": "MODIS/Terra 植被指数 16天 全球 250米",                // Chinese name
  "category": "vegetation_indices",   // Category key
  "platform": "Terra",                // Terra/Aqua/Combined
  "resolution": "250m",               // Spatial resolution
  "temporal_resolution": "16-day",    // Temporal resolution
  "start_date": "2000-02-18",         // Data start date
  "end_date": "present",              // Data end date
  "version": "061",                   // Product version (061 = Collection 6.1)
  "stage": "Stage 3",                 // Product maturity stage
  "description": "...",               // English description
  "description_cn": "...",            // Chinese description
  "bands": [...],                     // Band entries array
  "gee_collection": "MODIS/061/MOD13Q1",  // GEE ImageCollection ID
  "doi": "10.5067/MODIS/MOD13Q1.061",    // Digital Object Identifier
  "pi": "Kamel Didan",                // Principal Investigator
  "algorithms": ["..."],              // Algorithm descriptions
  "official_url": "https://...",      // NASA official product page
  "download_url": "https://..."       // Direct download link
}
```

### 3.2 Band Entry

```json
{
  "name": "NDVI",                     // Band name
  "dtype": "Int16",                   // Data type
  "scale": 0.0001,                    // Scale factor
  "offset": 0,                        // Additive offset (optional)
  "units": "dimensionless",          // Physical units
  "wavelength": "620-670nm",          // Wavelength range (optional)
  "description": "Normalized Difference Vegetation Index",  // English description
  "description_cn": "归一化植被指数"                              // Chinese description
}
```

### 3.3 GEE Code Example

```json
{
  "MOD13Q1": {
    "description": "Terra MODIS Vegetation Indices 16-Day 250m - NDVI analysis",
    "description_cn": "Terra MODIS植被指数16天250米 - NDVI分析",
    "code": "// JavaScript GEE code in English",
    "code_cn": "// JavaScript GEE code with Chinese comments"
  }
}
```

## 4. Skill Structure

```
modis-product-skill/
├── _meta.json              # Skill metadata
├── SKILL.md                # Skill documentation and usage guide
├── DESIGN.md               # This design document
├── main.py                 # Entry point script
├── data/
│   ├── products.json       # Main product database (46 products)
│   └── gee_codes.json      # GEE code examples (15 products)
├── scripts/
│   └── modis_products.py   # Main query script with CLI
└── references/
    └── urls.json           # Reference URLs
```

### File Descriptions

- **`_meta.json`**: Skill metadata including name, version, description, author, tags, and entry point
- **`SKILL.md`**: User-facing documentation with usage examples, parameters, and download methods
- **`main.py`**: Entry point that calls the main query script and outputs JSON
- **`data/products.json`**: Complete MODIS product database with all metadata
- **`data/gee_codes.json`**: Pre-built GEE code examples for 15 key products
- **`scripts/modis_products.py`**: Core query engine with search, filter, and format functions

## 5. Query Capabilities

### 5.1 Search (search)
- **Keyword Search**: Supports product ID, name, category, platform, resolution, band names
- **Bilingual**: Works with both English and Chinese keywords
- **Scoring Algorithm**:
  - Exact ID match: 100 points
  - ID substring match: 80 points
  - Name match: 60 points
  - Category match: 50-55 points
  - Platform match: 40 points
  - Resolution match: 30 points
  - Description match: 20 points
  - Band name match: 25 points

### 5.2 Product Details (show)
- Complete metadata display
- All band information with scale factors and units
- Algorithm descriptions
- Official URLs and download links

### 5.3 GEE Code (gee)
- Pre-built code examples for 15 key products
- Auto-generated code for products without specific examples
- Includes: loading, filtering, scale factors, visualization, charting
- Bilingual comments (English and Chinese)

### 5.4 Download Info (download)
- Multiple download sources (LAADS DAAC, NASA Earthdata, LP DAAC)
- wget command examples
- AppEEARS area subset links
- GEE collection ID reference

### 5.5 Category Listing (category/categories)
- Filter products by category
- Count products per category
- Bilingual category names

### 5.6 Platform Filter (platform)
- Filter by Terra, Aqua, or Combined platforms
- Bilingual platform names

### 5.7 Resolution Filter (resolution)
- Filter by spatial resolution (250m, 500m, 1km, etc.)

### 5.8 Product Comparison (compare)
- Side-by-side comparison of two products
- All key attributes compared
- Band lists displayed

### 5.9 Statistics (stats)
- Total product count
- Breakdowns by category, platform, resolution, version, stage
- Formatted output

## 6. Data Sources

All data is collected from official NASA sources:

- **NASA MODIS Web**: https://modis.gsfc.nasa.gov/data/dataprod/
- **LP DAAC**: https://lpdaac.usgs.gov/
- **GEE Data Catalog**: https://developers.google.com/earth-engine/datasets/catalog/modis
- **LAADS DAAC**: https://ladsweb.modaps.eosdis.nasa.gov/
- **NSIDC**: https://nsidc.org/data/ (snow products)

### Data Quality Notes
- All Collection 6.1 (v061) products use the latest algorithms
- Snow products (MOD10/MYD10) remain at Collection 6 (v006)
- Stage 3 products are fully validated; Stage 2 are provisional
- Scale factors must be applied to obtain physical values
- Quality bands should be used to filter unreliable pixels

## 7. Development Phases

### Phase 1: Core Database (Complete)
- [x] Define data schema
- [x] Collect product metadata for all 46 products
- [x] Create products.json with full details
- [x] Include band information with scale factors

### Phase 2: Query Engine (Complete)
- [x] Implement search with scoring algorithm
- [x] Implement filter functions (category, platform, resolution)
- [x] Implement product comparison
- [x] Implement statistics generation
- [x] Add bilingual support

### Phase 3: GEE Integration (Complete)
- [x] Create GEE code examples for 15 key products
- [x] Auto-generate GEE code for remaining products
- [x] Include scale factor application
- [x] Include visualization and charting
- [x] Bilingual code comments

### Phase 4: Documentation (Complete)
- [x] Write comprehensive SKILL.md
- [x] Write DESIGN.md
- [x] Add usage examples
- [x] Document download methods

### Phase 5: Future Enhancements (Planned)
- [ ] Add more GEE code examples
- [ ] Support temporal range queries
- [ ] Add product inter-comparison charts
- [ ] Export results to CSV/Excel
- [ ] Interactive web interface
- [ ] API server mode

## 8. Usage Examples

```bash
# Search for NDVI products
python scripts/modis_products.py search NDVI

# Search in Chinese
python scripts/modis_products.py search 植被指数

# Show product details
python scripts/modis_products.py show MOD13Q1

# Get GEE code
python scripts/modis_products.py gee MOD13Q1

# Download info
python scripts/modis_products.py download MOD13Q1

# List by category
python scripts/modis_products.py category vegetation_indices

# List all categories
python scripts/modis_products.py categories

# Filter by platform
python scripts/modis_products.py platform Terra

# Compare products
python scripts/modis_products.py compare MOD13Q1 MYD13Q1

# Database statistics
python scripts/modis_products.py stats
```

## 9. Technical Notes

- **Python Version**: 3.6+ (uses only standard library)
- **Encoding**: UTF-8 for all files (supports Chinese characters)
- **JSON**: All JSON files use `ensure_ascii=False` for proper Chinese display
- **Cross-platform**: Uses `os.path` for file paths, works on Windows/macOS/Linux
- **No external dependencies**: Uses only `json`, `os`, `sys`, `typing`
