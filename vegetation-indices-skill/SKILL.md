# 植被指数查询工具 | Vegetation Indices Query Skill

查询和搜索来自 IndexDatabase.de (IDB) 的遥感植被指数综合数据库，包含 **519个指数**、**167个传感器**、**43个应用领域**。

Query and search the complete database of remote sensing vegetation indices from IndexDatabase.de (IDB). Contains **519 indices**, **167 sensors**, and **43 applications**.

## 特性 | Features

- 🔍 **智能搜索 | Smart Search** - 按名称/缩写/公式内容搜索（支持中英文）
- 📊 **详细信息 | Details** - 查看指数完整信息（含原始网页链接）
- 📡 **传感器查询 | Sensors** - 列出所有兼容的卫星/航空传感器
- 🌿 **应用领域 | Applications** - 按应用领域浏览（含中文分类）
- 🌐 **双语输出 | Bilingual** - 所有结果同时提供中英文说明
- 🔗 **原始链接 | Source Links** - 每个指数都附带IDB原始网址
- 💡 **智能建议 | Smart Suggestions** - 查不到时建议访问IDB网站搜索
- 📚 **相关数据库 | Related DBs** - 列出其他植被指数资源网站

---

## 数据来源 | Data Source

数据爬取自 [IndexDatabase.de](https://www.indexdatabase.de/) — 最全面的遥感植被指数数据库。
Data crawled from [IndexDatabase.de](https://www.indexdatabase.de/) — the most comprehensive remote sensing vegetation index database.

---

## 使用方法 | Usage

### 搜索指数 | Search indices
```bash
python scripts/vegetation_indices.py search "NDVI"
python scripts/vegetation_indices.py search "叶绿素" --limit 20
python scripts/vegetation_indices.py search "EVI"
python scripts/vegetation_indices.py search "chlorophyll"
```

### 查看详情 | Get index details
```bash
python scripts/vegetation_indices.py show <id>
python scripts/vegetation_indices.py show 58
```

### 列出应用领域 | List applications
```bash
python scripts/vegetation_indices.py applications
```

### 列出传感器 | List sensors
```bash
python scripts/vegetation_indices.py sensors
```

### 数据库统计 | Statistics
```bash
python scripts/vegetation_indices.py stats
```

### 其他数据库 | Other databases
```bash
python scripts/vegetation_indices.py databases
```

---

## 参数说明 | Parameters

| 参数 Parameter | 类型 Type | 必填 Required | 说明 Description |
|---|---|---|---|
| command | string | 是 Yes | 操作命令 |
| query | string | 条件 Conditional | 搜索关键词（用于 "search"） |
| id | int | 条件 Conditional | 指数ID（用于 "show"） |
| --limit | int | 否 No | 最大搜索结果数，默认10 |

---

## 输出格式 | Output Format

### 搜索结果 | Search Result
```json
{
  "success": true,
  "query": "NDVI",
  "num_results": 5,
  "results": [
    {
      "id": 58,
      "name": "Normalized Difference NIR/Red NDVI",
      "abbreviation": "NDVI",
      "formula": "NIR-REDNIR+RED",
      "zh_name": "归一化植被指数",
      "variables": "RED=[670;50;30],NIR=[800;10;10]",
      "source": "Original Formula",
      "n_sensors": 71,
      "n_applications": 13,
      "n_references": 116,
      "url": "https://www.indexdatabase.de/db/i-single.php?id=58"
    }
  ],
  "message": "找到 5 个与 'NDVI' 相关的指数 / Found 5 indices for 'NDVI'"
}
```

### 查不到时 | When no results found
```json
{
  "success": true,
  "query": "XYZ123",
  "num_results": 0,
  "results": [],
  "message": "未找到与 'XYZ123' 相关的指数 / No indices found for 'XYZ123'",
  "suggestion": "建议直接访问 IDB 网站搜索 / Try searching directly on the IDB website: https://www.indexdatabase.de/db/i.php",
  "suggestion_url": "https://www.indexdatabase.de/db/i.php"
}
```

---

## 应用领域分类 | Application Categories

| 英文 English | 中文 Chinese | 指数数 # Indices |
|---|---|---|
| Vegetation | 植被 | 261 |
| Vegetation - Chlorophyll | 植被 - 叶绿素 | 112 |
| Vegetation - LAI | 植被 - 叶面积指数 | 10 |
| Vegetation - Water | 植被 - 水分 | 33 |
| Vegetation - Water stress | 植被 - 水分胁迫 | 12 |
| Vegetation - Biomass | 植被 - 生物量 | 9 |
| Vegetation - Stress | 植被 - 胁迫 | 10 |
| Vegetation - Nitrogen content | 植被 - 氮含量 | 8 |
| Agriculture | 农业 | 22 |
| Agriculture - Crop yield | 农业 - 作物产量 | 2 |
| Forestry | 林业 | 3 |
| Soil | 土壤 | 14 |
| Geology | 地质 | 28 |
| Water resource management | 水资源管理 | 0 |
| Fire | 火灾 | 2 |

---

## 常用指数常见名称 | Common Index Names

| 缩写 | 中文 | 英文 |
|---|---|---|
| NDVI | 归一化植被指数 | Normalized Difference Vegetation Index |
| EVI | 增强型植被指数 | Enhanced Vegetation Index |
| SAVI | 土壤调节植被指数 | Soil Adjusted Vegetation Index |
| GNDVI | 绿色归一化植被指数 | Green Normalized Difference Vegetation Index |
| NDWI | 归一化水体指数 | Normalized Difference Water Index |
| LSWI | 地表水体指数 | Land Surface Water Index |
| RVI | 比值植被指数 | Ratio Vegetation Index |
| DVI | 差值植被指数 | Difference Vegetation Index |
| MSAVI | 修正土壤调节植被指数 | Modified Soil Adjusted Vegetation Index |
| OSAVI | 优化土壤调节植被指数 | Optimized Soil Adjusted Vegetation Index |
| MCARI | 修正叶绿素吸收指数 | Modified Chlorophyll Absorption Ratio Index |
| MTCI | MERIS陆地叶绿素指数 | MERIS Terrestrial Chlorophyll Index |
| CIrededge | 叶绿素指数(红边) | Chlorophyll Index Red Edge |
| TCARI | 转换叶绿素吸收反射指数 | Transformed Chlorophyll Absorption Reflectance Index |
| NDRE | 归一化红边指数 | Normalized Difference Red Edge |
| IPVI | 红外百分比植被指数 | Infrared Percentage Vegetation Index |
| GVI | 全球植被指数 | Global Vegetation Index |
| GEMI | 全球环境监测指数 | Global Environment Monitoring Index |
| ARVI | 抗大气植被指数 | Atmospherically Resistant Vegetation Index |
| SIPI | 结构不敏感色素指数 | Structure Intensive Pigment Index |
| PSRI | 植物衰老反射指数 | Plant Senescence Reflectance Index |
| PRI | 光化学反射指数 | Photochemical Reflectance Index |
| CAI | 纤维素吸收指数 | Cellulose Absorption Index |
| NDNI | 归一化氮指数 | Normalized Difference Nitrogen Index |
| MSI | 水分胁迫指数 | Moisture Stress Index |
| WDRVI | 宽动态范围植被指数 | Wide Dynamic Range Vegetation Index |

---

## 其他植被指数资源 | Other Vegetation Index Resources

| 数据库/网站 | 说明 | URL |
|---|---|---|
| Sentinel Hub Custom Scripts | 基于IDB的Sentinel-2在线指数计算 | [链接](https://sentinel-hub.github.io/custom-scripts/sentinel-2/indexdb/) |
| NASA MODIS Vegetation Index | MODIS植被指数产品官方页面 | [链接](https://modis.gsfc.nasa.gov/data/dataprod/mod13.php) |
| ENVI Spectral Indices | ENVI软件光谱指数工具文档 | [链接](https://www.l3harrisgeospatial.com/docs/spectralindices.html) |
| Google Earth Engine Catalog | GEE数据目录（含多种植被指数） | [链接](https://developers.google.com/earth-engine/datasets/catalog) |
| USGS Spectral Library | 美国地质调查局光谱库 | [链接](https://crustal.usgs.gov/speclab/QueryAll07a.php) |
| 遥感指数汇总(CSDN) | 中文遥感指数博客汇总 | [链接](https://blog.csdn.net/) |
| 常用植被指数(知乎) | 知乎专栏详细介绍 | [链接](https://zhuanlan.zhihu.com/p/365793028) |

---

## 注意事项 | Notes

1. 数据来源：IndexDatabase.de，版权归The IDB Project (2011-2026)所有
2. 公式中的特殊字符使用HTML实体表示（如 `&InvisibleTimes;` 表示乘法）
3. 每个指数都有指向IDB原始网页的完整链接，可查看更详细的信息、兼容传感器和参考文献
4. 本地搜索不到时，请直接访问 [IDB官网](https://www.indexdatabase.de/db/i.php) 在线搜索
5. 传感器数据包含波段数、光谱范围、空间分辨率、平台和发射日期等信息

---

## 执行方式 | Execution

**类型 type**: script
**脚本路径 script_path**: scripts/vegetation_indices.py
**入口函数 entry_point**: main
**依赖 dependencies**: 无（仅使用Python标准库 / None, only Python stdlib）
