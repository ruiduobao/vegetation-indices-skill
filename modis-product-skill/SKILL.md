# MODIS Product Data Query Skill | MODIS产品数据查询工具

Comprehensive local query tool for NASA MODIS satellite products. Covers **46 products** across **13 categories** with bilingual (Chinese/English) descriptions, algorithm principles, band information, Google Earth Engine integration, and download information.

全面的NASA MODIS卫星产品本地查询工具。涵盖**46个产品**、**13个类别**，提供双语（中英文）介绍、算法原理、波段信息、Google Earth Engine集成和下载信息。

## Features | 特性

- 🔍 **Smart Search** - Search by product ID, name, category, or keyword (bilingual)
- 📊 **Detailed Info** - Complete product details with algorithms, formulas, bands
- 🌐 **Bilingual** - All descriptions in Chinese and English
- 🛰️ **GEE Integration** - Ready-to-use Google Earth Engine code examples
- 📥 **Download Info** - Multiple download methods and citations
- 🔄 **Product Comparison** - Compare two products side-by-side
- 📈 **Statistics** - Database statistics and category breakdowns

---

## Data Source | 数据来源

Data collected from official NASA MODIS product pages:
- NASA MODIS Web: https://modis.gsfc.nasa.gov/data/dataprod/
- LP DAAC: https://lpdaac.usgs.gov/
- GEE Data Catalog: https://developers.google.com/earth-engine/datasets/catalog/modis

---

## Usage | 用法

### Search products | 搜索产品
```bash
python scripts/modis_products.py search NDVI
python scripts/modis_products.py search 植被指数
python scripts/modis_products.py search LST --limit 5
python scripts/modis_products.py search fire
```

### Show product details | 查看产品详情
```bash
python scripts/modis_products.py show MOD13Q1
python scripts/modis_products.py show MOD11A1
python scripts/modis_products.py show MCD12Q1
```

### GEE code example | GEE代码示例
```bash
python scripts/modis_products.py gee MOD13Q1
python scripts/modis_products.py gee MOD11A1
python scripts/modis_products.py gee MCD12Q1
```

### Download information | 下载信息
```bash
python scripts/modis_products.py download MOD13Q1
python scripts/modis_products.py download MOD09GA
```

### List by category | 按类别列出
```bash
python scripts/modis_products.py category vegetation_indices
python scripts/modis_products.py category land_surface_temperature
python scripts/modis_products.py categories
```

### Filter by platform | 按平台筛选
```bash
python scripts/modis_products.py platform Terra
python scripts/modis_products.py platform Aqua
python scripts/modis_products.py platform Combined
```

### Filter by resolution | 按分辨率筛选
```bash
python scripts/modis_products.py resolution 250m
python scripts/modis_products.py resolution 500m
python scripts/modis_products.py resolution 1km
```

### Compare products | 对比产品
```bash
python scripts/modis_products.py compare MOD13Q1 MYD13Q1
python scripts/modis_products.py compare MOD13A1 MOD13A2
```

### Database statistics | 数据库统计
```bash
python scripts/modis_products.py stats
```

---

## Parameters | 参数

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| command | string | Yes | Operation command |
| query | string | Conditional | Search keyword |
| product_id | string | Conditional | Product ID (e.g., MOD13Q1) |
| --limit | int | No | Max results (default 10) |

---

## Product Categories | 产品类别

| Category | 类别 | Products |
|----------|------|----------|
| Vegetation Indices | 植被指数 | 12 (MOD13 series) |
| Surface Reflectance | 地表反射率 | 5 (MOD09 series) |
| Land Surface Temperature | 地表温度 | 4 (MOD11 series) |
| Land Cover | 土地覆盖 | 2 (MCD12 series) |
| Thermal Anomalies/Fire | 热异常/火灾 | 4 (MOD14 series) |
| LAI/FPAR | 叶面积指数/FPAR | 4 (MOD15/MCD15 series) |
| Evapotranspiration | 蒸散发 | 3 (MOD16 series) |
| GPP/NPP | 总/净初级生产力 | 3 (MOD17 series) |
| BRDF/Albedo | BRDF/反照率 | 3 (MCD43 series) |
| Vegetation Continuous Fields | 植被连续场 | 1 (MOD44B) |
| Water Mask | 水体掩膜 | 1 (MOD44W) |
| Burned Area | 燃烧面积 | 1 (MCD64A1) |
| Snow Cover | 积雪 | 3 (MOD10 series) |

---

## Key Products | 核心产品

| Product | 产品 | GEE Collection | Scale |
|---------|------|----------------|-------|
| MOD13Q1 | 植被指数16天250m | MODIS/061/MOD13Q1 | NDVI×0.0001 |
| MOD13A1 | 植被指数16天500m | MODIS/061/MOD13A1 | NDVI×0.0001 |
| MOD13A2 | 植被指数16天1km | MODIS/061/MOD13A2 | NDVI×0.0001 |
| MOD13A3 | 植被指数月值1km | MODIS/061/MOD13A3 | NDVI×0.0001 |
| MOD09GA | 地表反射率每日 | MODIS/061/MOD09GA | ×0.0001 |
| MOD09A1 | 地表反射率8天500m | MODIS/061/MOD09A1 | ×0.0001 |
| MOD11A1 | 地表温度每日1km | MODIS/061/MOD11A1 | ×0.02 (K) |
| MOD11A2 | 地表温度8天1km | MODIS/061/MOD11A2 | ×0.02 (K) |
| MCD12Q1 | 土地覆盖年值500m | MODIS/061/MCD12Q1 | Class 1-17 |
| MOD14A1 | 火灾每日1km | MODIS/061/MOD14A1 | Fire mask |
| MOD15A2H | LAI/FPAR 8天500m | MODIS/061/MOD15A2H | LAI×0.1 |
| MOD16A2 | 蒸散发8天500m | MODIS/061/MOD16A2 | ET×0.1 |
| MOD17A2H | GPP 8天500m | MODIS/061/MOD17A2H | GPP×0.01 |
| MCD43A4 | NBAR 16天500m | MODIS/061/MCD43A4 | ×0.0001 |
| MOD44W | 水体掩膜250m | MODIS/061/MOD44W | 0/1 |
| MCD64A1 | 燃烧面积月值500m | MODIS/061/MCD64A1 | DOY |
| MOD10A1 | 积雪每日500m | MODIS/006/MOD10A1 | % |

---

## GEE Quick Start | GEE快速开始

```javascript
// Load MODIS NDVI data
var modisNDVI = ee.ImageCollection('MODIS/061/MOD13Q1');

// Filter by date and region
var roi = ee.Geometry.Rectangle([100, 30, 110, 40]);
var filtered = modisNDVI
  .filterDate('2020-01-01', '2020-12-31')
  .filterBounds(roi)
  .select('NDVI');

// Apply scale factor
var ndvi = filtered.map(function(img) {
  return img.multiply(0.0001);
});

// Visualize
Map.addLayer(ndvi.mean(), {min: 0, max: 1, palette: ['red', 'yellow', 'green']}, 'NDVI');
```

---

## Download Methods | 下载方式

1. **NASA Earthdata Search**: https://search.earthdata.nasa.gov/
2. **LP DAAC Data Pool**: https://e4ftl01.cr.usgs.gov/
3. **LAADS DAAC**: https://ladsweb.modaps.eosdis.nasa.gov/
4. **AppEEARS**: https://appeears.earthdatacloud.nasa.gov/
5. **Google Earth Engine**: Use GEE collection IDs directly
6. **NSIDC** (Snow products): https://nsidc.org/data/

**Note**: NASA Earthdata account required for download.
**注意**：下载需要NASA Earthdata账号。Register at: https://urs.earthdata.nasa.gov/

---

## Notes | 注意事项

1. Data source: NASA MODIS Web, copyright belongs to NASA
2. All MODIS products are freely available for research and commercial use
3. GEE Collection IDs use version 061 (Collection 6.1) where available
4. Snow products (MOD10/MYD10) use Collection 006 and are hosted at NSIDC
5. Scale factors must be applied to get physical values
6. Quality bands should be used to filter unreliable pixels

---

## Execution | Execution

**type**: script
**script_path**: scripts/modis_products.py
**entry_point**: main
**dependencies**: None (Python stdlib only / 仅使用Python标准库)
