#!/usr/bin/env python3
"""
为植被指数添加应用场景映射和标签体系
"""

import json
import os

DATA_DIR = "vegetation-indices-skill/data"

# ============================================================
# 应用场景 → 指数映射表（核心优化）
# 用户搜"不透水面"→ 推荐 NDBI 等
# ============================================================
APPLICATION_MAP = {
    # 1. 不透水面/城市建筑
    "不透水面": {
        "en": "Impervious Surface",
        "abbrevs": ["NDBBI", "NDBI", "NDBI2", "NDBI3", "WV-BI", "ISI", "UI", "IBI", "UBI", "BAEI", "BRBA", "BRB"],
        "description": "城市不透水面提取，区分建筑区与植被/水体",
        "description_en": "Urban impervious surface extraction",
    },
    "城市扩张": {
        "en": "Urban Expansion",
        "abbrevs": ["NDBBI", "NDBI", "NDBI2", "WV-BI", "IBI", "UBI"],
        "description": "监测城市扩张和建设用地变化",
        "description_en": "Urban expansion monitoring",
    },
    "城市建筑": {
        "en": "Urban Built-up",
        "abbrevs": ["NDBI", "NDBBI", "WV-BI", "IBI"],
        "description": "城市建筑用地识别",
        "description_en": "Urban built-up area detection",
    },

    # 2. 植被覆盖/绿度
    "植被覆盖": {
        "en": "Vegetation Coverage",
        "abbrevs": ["NDVI", "EVI", "EVI2", "GNDVI", "SAVI", "MSAVI", "OSAVI", "GSAVI", "GOSAVI", "GRVI", "RVI", "DVI"],
        "description": "植被覆盖度监测，最基本的植被指数",
        "description_en": "Vegetation coverage monitoring",
    },
    "植被绿度": {
        "en": "Vegetation Greenness",
        "abbrevs": ["NDVI", "EVI", "GNDVI", "GLI", "TGI", "ExG", "CIVE", "VEG"],
        "description": "植被绿度测量，反映光合作用强度",
        "description_en": "Vegetation greenness measurement",
    },
    "森林监测": {
        "en": "Forest Monitoring",
        "abbrevs": ["NDVI", "EVI", "GNDVI", "NBR", "NBR2", "RVI", "EVI2", "SAVI", "MSAVI", "NDMI"],
        "description": "森林覆盖、健康状况和变化监测",
        "description_en": "Forest cover and health monitoring",
    },
    "植被健康": {
        "en": "Vegetation Health",
        "abbrevs": ["NDVI", "EVI", "NDMI", "MSI", "VCI", "VH", "GVMI"],
        "description": "植被健康状况综合评估",
        "description_en": "Vegetation health assessment",
    },

    # 3. 作物/农业
    "作物监测": {
        "en": "Crop Monitoring",
        "abbrevs": ["NDVI", "EVI", "GNDVI", "CIrededge", "CIgreen", "SAVI", "MSAVI", "NDRE", "MTCI"],
        "description": "作物长势监测和产量估算",
        "description_en": "Crop growth monitoring",
    },
    "作物产量": {
        "en": "Crop Yield",
        "abbrevs": ["NDVI", "EVI", "GNDVI", "SAVI", "CIrededge", "NDRE", "MTVCI"],
        "description": "作物产量估算和预测",
        "description_en": "Crop yield estimation",
    },
    "作物分类": {
        "en": "Crop Classification",
        "abbrevs": ["NDVI", "EVI", "GNDVI", "NDWI", "NDBI"],
        "description": "农作物类型分类识别",
        "description_en": "Crop type classification",
    },
    "精准农业": {
        "en": "Precision Agriculture",
        "abbrevs": ["NDVI", "EVI", "CIrededge", "MCARI", "MTCI", "NDRE", "CCCI", "TCARI"],
        "description": "精准农业管理决策支持",
        "description_en": "Precision agriculture support",
    },

    # 4. 水分/干旱
    "水分胁迫": {
        "en": "Water Stress",
        "abbrevs": ["NDWI", "MSI", "CWSI", "DSWI", "DSWI-5", "NDMI", "NDII", "GVMI", "SIWSI"],
        "description": "植被水分胁迫监测，用于干旱预警",
        "description_en": "Vegetation water stress monitoring",
    },
    "干旱监测": {
        "en": "Drought Monitoring",
        "abbrevs": ["NDWI", "NDMI", "VCI", "TCI", "NMDI", "MSI", "CWSI", "DSWI", "NDVI", "EVI"],
        "description": "农业干旱和气象干旱综合监测",
        "description_en": "Agricultural and meteorological drought monitoring",
    },
    "土壤水分": {
        "en": "Soil Moisture",
        "abbrevs": ["NDWI", "LSM", "SWCI", "SMCI", "NDMI"],
        "description": "土壤含水量估算",
        "description_en": "Soil moisture estimation",
    },

    # 5. 叶绿素
    "叶绿素": {
        "en": "Chlorophyll",
        "abbrevs": ["CIgreen", "CIrededge", "CIrededge710", "MCARI", "MCARI1", "MCARI2", "MTCI", "TCARI", "NDRE", "Chlgreen", "Chlred-edge", "CVI", "CARI", "CARI2"],
        "description": "叶片和冠层叶绿素含量估算",
        "description_en": "Leaf/canopy chlorophyll content estimation",
    },
    "光合作用": {
        "en": "Photosynthesis",
        "abbrevs": ["PRI", "SIPI", "SIPI1", "SIPI3", "NPCI", "NDVI", "EVI"],
        "description": "植被光合作用活性监测",
        "description_en": "Photosynthesis activity monitoring",
    },
    "叶面积指数": {
        "en": "Leaf Area Index",
        "abbrevs": ["NDVI", "EVI", "SAVI", "MSAVI", "MTVI", "MTVI2", "LAI", "LAIDI"],
        "description": "叶面积指数(LAI)估算",
        "description_en": "Leaf Area Index estimation",
    },

    # 6. 火灾
    "火灾监测": {
        "en": "Fire Monitoring",
        "abbrevs": ["NBR", "NBR2", "BAI", "NBRT1", "NBRT2", "CSI", "GEMI"],
        "description": "森林火灾监测和火烧迹地识别",
        "description_en": "Forest fire monitoring and burn scar detection",
    },
    "火烧迹地": {
        "en": "Burn Scar",
        "abbrevs": ["NBR", "NBR2", "BAI", "NBRT1", "NBRT2"],
        "description": "火灾后火烧迹地提取和评估",
        "description_en": "Burn scar extraction and assessment",
    },

    # 7. 水体
    "水体监测": {
        "en": "Water Monitoring",
        "abbrevs": ["NDWI", "MNDWI", "NDMI", "WRI", "WBI", "SWI", "NDSI"],
        "description": "地表水体提取和监测",
        "description_en": "Surface water extraction and monitoring",
    },
    "水体提取": {
        "en": "Water Extraction",
        "abbrevs": ["NDWI", "MNDWI", "AWEI", "WRI", "WBI"],
        "description": "从遥感影像中提取水体范围",
        "description_en": "Water body extraction from imagery",
    },
    "水质监测": {
        "en": "Water Quality",
        "abbrevs": ["NDWI", "NDSI", "FAI", "CI", "TCI"],
        "description": "水体浊度、叶绿素a等水质参数估算",
        "description_en": "Water quality parameter estimation",
    },

    # 8. 雪/冰
    "雪盖监测": {
        "en": "Snow Cover",
        "abbrevs": ["NDSI", "NDSI2", "S3", "SNW", "SIND"],
        "description": "积雪覆盖范围监测",
        "description_en": "Snow cover monitoring",
    },
    "冰川监测": {
        "en": "Glacier Monitoring",
        "abbrevs": ["NDSI", "NBR"],
        "description": "冰川和冰盖变化监测",
        "description_en": "Glacier and ice cover monitoring",
    },

    # 9. 土壤/地质
    "土壤监测": {
        "en": "Soil Monitoring",
        "abbrevs": ["BSI", "NBSI", "BI", "BI2", "SI", "CLAY"],
        "description": "裸土识别和土壤退化监测",
        "description_en": "Bare soil identification and degradation monitoring",
    },
    "地质矿物": {
        "en": "Geology/Mineral",
        "abbrevs": ["ALUI", "CALI", "CLAI", "DOLI", "KAI1", "KAI2", "KAI3", "MONI", "MUSI", "MAGI", "PHEI"],
        "description": "地质矿物识别和岩性分类",
        "description_en": "Geological mineral identification",
    },

    # 10. 生物量/碳
    "生物量": {
        "en": "Biomass",
        "abbrevs": ["NDVI", "EVI", "GNDVI", "SAVI", "MSAVI", "RVI", "DVI"],
        "description": "植被地上生物量估算",
        "description_en": "Above-ground biomass estimation",
    },
    "碳储量": {
        "en": "Carbon Stock",
        "abbrevs": ["NDVI", "EVI", "LAI", "FAPAR", "GPP", "NPP"],
        "description": "碳储量和碳循环研究",
        "description_en": "Carbon stock and cycling research",
    },

    # 11. 热环境
    "城市热岛": {
        "en": "Urban Heat Island",
        "abbrevs": ["LST", "UTFVI", "UHI"],
        "description": "城市热岛效应监测",
        "description_en": "Urban heat island monitoring",
    },

    # 12. 灾害
    "洪涝灾害": {
        "en": "Flood Disaster",
        "abbrevs": ["NDWI", "MNDWI", "AWEI", "NDMI"],
        "description": "洪涝灾害监测和损失评估",
        "description_en": "Flood monitoring and damage assessment",
    },
    "病虫害": {
        "en": "Disease/Pest",
        "abbrevs": ["DSWI", "DSWI-5", "SIPI", "PRI", "NDVI", "EVI"],
        "description": "作物病虫害早期检测",
        "description_en": "Crop disease and pest early detection",
    },
}

# ============================================================
# 每个指数的标签体系
# ============================================================
INDEX_TAGS = {
    "NDVI": ["植被绿度", "覆盖度", "光合作用", "基础指数"],
    "EVI": ["植被绿度", "覆盖度", "大气校正", "高植被区"],
    "EVI2": ["植被绿度", "覆盖度", "大气校正"],
    "SAVI": ["植被绿度", "土壤调节", "稀疏植被"],
    "MSAVI": ["植被绿度", "土壤调节", "稀疏植被", "自适应"],
    "OSAVI": ["植被绿度", "土壤调节", "优化"],
    "GNDVI": ["植被绿度", "绿波段", "叶绿素敏感"],
    "GOSAVI": ["植被绿度", "土壤调节", "绿波段"],
    "GSAVI": ["植被绿度", "土壤调节", "绿波段"],
    "GRVI": ["植被绿度", "绿红比"],
    "GLI": ["植被绿度", "绿叶指数", "可见光"],
    "DVI": ["植被绿度", "差值", "简单"],
    "RVI": ["植被绿度", "比值", "简单"],
    "GDVI": ["植被绿度", "绿差值"],
    "GVI": ["植被绿度", "绿植被指数"],
    "TGI": ["植被绿度", "三角绿度"],
    "ExG": ["植被绿度", "超绿", "可见光"],
    "CIVE": ["植被绿度", "彩色植被指数", "可见光"],
    "VEG": ["植被绿度", "自主植被指数"],
    "CIgreen": ["叶绿素", "绿波段", "作物"],
    "CIrededge": ["叶绿素", "红边", "作物"],
    "CIrededge710": ["叶绿素", "红边710nm"],
    "MCARI": ["叶绿素", "修正吸收", "红边"],
    "MCARI1": ["叶绿素", "修正吸收", "改进"],
    "MCARI2": ["叶绿素", "修正吸收", "改进", "土壤调节"],
    "TCARI": ["叶绿素", "变换吸收", "红边"],
    "MTCI": ["叶绿素", "MERIS", "红边", "作物"],
    "NDRE": ["叶绿素", "红边", "作物"],
    "Chlgreen": ["叶绿素", "绿波段"],
    "Chlred-edge": ["叶绿素", "红边"],
    "CVI": ["叶绿素", "植被指数"],
    "CARI": ["叶绿素", "吸收比"],
    "CARI2": ["叶绿素", "吸收比", "改进"],
    "CCCI": ["叶绿素", "冠层含量", "综合"],
    "MTVI": ["叶绿素", "三角指数", "LAI"],
    "MTVI1": ["叶绿素", "三角指数", "改进"],
    "MTVI2": ["叶绿素", "三角指数", "改进", "土壤调节"],
    "LAI": ["叶面积指数", "冠层结构"],
    "LAIDI": ["叶面积指数", "确定指数"],
    "NDWI": ["水分", "水体", "近红外绿波段"],
    "MNDWI": ["水分", "水体", "改进", "建筑区分"],
    "MSI": ["水分", "胁迫", "短波红外"],
    "CWSI": ["水分", "胁迫", "作物"],
    "DSWI": ["水分", "胁迫", "病害"],
    "DSWI-5": ["水分", "胁迫", "病害"],
    "NDMI": ["水分", "含量", "近红外短波红外"],
    "NDII": ["水分", "红外", "含量"],
    "GVMI": ["水分", "全球植被", "含量"],
    "SIWSI": ["水分", "短波红外", "胁迫"],
    "WBI": ["水分", "波段", "含量"],
    "WRI": ["水分", "比值", "含量"],
    "SWI": ["水分", "简单", "含量"],
    "NMDI": ["水分", "多波段", "干旱"],
    "NBR": ["火灾", "燃烧", "近红外短波红外"],
    "NBR2": ["火灾", "燃烧", "短波红外"],
    "BAI": ["火灾", "燃烧", "亮度"],
    "NBRT1": ["火灾", "燃烧", "热"],
    "NBRT2": ["火灾", "燃烧", "热"],
    "NDBI": ["建筑", "城市", "不透水面", "近红外短波红外"],
    "NDBBI": ["建筑", "城市", "不透水面", "蓝波段"],
    "NDBI2": ["建筑", "城市", "不透水面"],
    "WV-BI": ["建筑", "城市", "WorldView"],
    "IBI": ["建筑", "城市", "指数建筑"],
    "UBI": ["建筑", "城市", "城市背景"],
    "BSI": ["土壤", "裸土", "亮度"],
    "NBSI": ["土壤", "裸土", "归一化"],
    "BI": ["土壤", "亮度", "简单"],
    "BI2": ["土壤", "亮度", "改进"],
    "SI": ["土壤", "盐分", "含量"],
    "CLAY": ["土壤", "粘土", "矿物"],
    "NDSI": ["雪", "积雪", "冰", "绿短波红外"],
    "NDSI2": ["雪", "积雪", "改进"],
    "PRI": ["光合作用", "光化学", "反射"],
    "SIPI": ["光合作用", "色素", "结构不敏感"],
    "SIPI1": ["光合作用", "色素"],
    "SIPI3": ["光合作用", "色素"],
    "NPCI": ["光合作用", "色素", "叶绿素"],
    "PSRI": ["衰老", "植物", "反射"],
    "ARI": ["花青素", "反射", "红边"],
    "CRI": ["类胡萝卜素", "反射", "绿波段"],
    "CRI550": ["类胡萝卜素", "反射", "550nm"],
    "CRI700": ["类胡萝卜素", "反射", "700nm"],
    "CAI": ["纤维素", "吸收", "干旱"],
    "NDLI": ["木质素", "归一化"],
    "NDNI": ["氮", "归一化", "含量"],
    "NDMSI": ["水分", "盐分", "含水量"],
    "NDPI": ["池塘", "水体", "归一化"],
    "RDVI": ["植被", "重归一化", "差值"],
    "TDVI": ["植被", "变换", "差值"],
    "WDRVI": ["植被", "宽动态范围", "差值"],
    "MNLI": ["植被", "非线性", "土壤调节"],
    "NLI": ["植被", "非线性", "简单"],
    "MSR": ["植被", "修正比值", "土壤调节"],
    "SR": ["植被", "比值", "简单"],
    "IPVI": ["植被", "红外百分比", "简单"],
    "VARI": ["植被", "大气校正", "可见光"],
    "GEMI": ["植被", "全球环境", "监测"],
    "TNDVI": ["植被", "变换", "归一化"],
    "BNDVI": ["植被", "蓝波段", "归一化"],
    "RBNDVI": ["植被", "红蓝", "归一化"],
    "RENDVI": ["红边", "归一化", "植被"],
    "MRENDVI": ["红边", "修正", "归一化"],
    "MRESR": ["红边", "修正", "比值"],
    "REPI": ["红边", "位置", "反射"],
    "REIP1": ["红边", "位置", "1"],
    "REIP2": ["红边", "位置", "2"],
    "REIP3": ["红边", "位置", "3"],
    "VREI": ["红边", "Vogelmann", "反射"],
    "VREI1": ["红边", "Vogelmann", "1"],
    "VREI2": ["红边", "Vogelmann", "2"],
    "TVI": ["三角", "植被", "面积"],
    "IF": ["形状", "指数"],
    "H": ["色相", "颜色"],
    "I": ["强度", "颜色"],
    "Hue": ["色相", "颜色"],
    "Intensity": ["强度", "颜色"],
    "SARVI": ["土壤", "大气", "植被", "阻力"],
    "SARVI2": ["土壤", "大气", "植被", "阻力"],
    "SAVI2": ["土壤", "植被", "调节2"],
    "SAVI3": ["土壤", "植被", "调节3"],
    "SBL": ["土壤", "背景", "线"],
    "SLAVI": ["比叶面积", "植被", "指数"],
    "RDVI2": ["重归一化", "差值", "2"],
    "NGRDI": ["绿红", "差值", "归一化"],
}

# ============================================================
# 标签 → 指数反查表
# ============================================================
TAG_TO_INDEXES = {}
for abbrev, tags in INDEX_TAGS.items():
    for tag in tags:
        if tag not in TAG_TO_INDEXES:
            TAG_TO_INDEXES[tag] = []
        TAG_TO_INDEXES[tag].append(abbrev)

# Save
with open(os.path.join(DATA_DIR, "application_map.json"), "w", encoding="utf-8") as f:
    json.dump(APPLICATION_MAP, f, indent=2, ensure_ascii=False)

with open(os.path.join(DATA_DIR, "index_tags.json"), "w", encoding="utf-8") as f:
    json.dump({"tags": INDEX_TAGS, "tag_to_indexes": TAG_TO_INDEXES}, f, indent=2, ensure_ascii=False)

print("Saved application_map.json and index_tags.json")
print("Applications:", len(APPLICATION_MAP))
print("Tags:", len(TAG_TO_INDEXES))
print("Tagged indices:", len(INDEX_TAGS))
