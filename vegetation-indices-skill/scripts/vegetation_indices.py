#!/usr/bin/env python3
"""
植被指数查询工具 Vegetation Indices Query Tool
数据来源：
  - IndexDatabase.de (IDB) - 519个植被指数、167个传感器、43个应用领域
  - ENVI Documentation (NV5) - 56个植被指数（含公式）
总计：575+ 个植被指数
"""

import json
import os
import re
import sys


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "data")
BASE_URL = "https://www.indexdatabase.de"

# 中文翻译对照表
ZH_NAMES = {
    # 常见指数名称翻译
    "NDVI": "归一化植被指数",
    "EVI": "增强型植被指数",
    "EVI2": "增强型植被指数2",
    "SAVI": "土壤调节植被指数",
    "MSAVI": "修正土壤调节植被指数",
    "OSAVI": "优化土壤调节植被指数",
    "GNDVI": "绿色归一化植被指数",
    "NDWI": "归一化水体指数",
    "LSWI": "地表水体指数",
    "NDMI": "归一化水分指数",
    "NBR": "归一化燃烧指数",
    "NBR2": "归一化燃烧指数2",
    "NDSI": "归一化积雪指数",
    "NDBI": "归一化建筑指数",
    "RVI": "比值植被指数",
    "DVI": "差值植被指数",
    "PVI": "垂直植被指数",
    "TVI": "变换植被指数",
    "TSAVI": "转换土壤调节植被指数",
    "ATSAVI": "调整转换土壤调节植被指数",
    "GOSAVI": "绿色优化土壤调节植被指数",
    "GSAVI": "绿色土壤调节植被指数",
    "MCARI": "修正叶绿素吸收指数",
    "MCARI1": "修正叶绿素吸收指数1",
    "MCARI2": "修正叶绿素吸收指数2",
    "MTVI1": "修正三角植被指数1",
    "MTVI2": "修正三角植被指数2",
    "CIgreen": "叶绿素指数(绿边)",
    "CIrededge": "叶绿素指数(红边)",
    "CIrededge710": "叶绿素指数(红边710)",
    "CARI": "叶绿素吸收比值指数",
    "CARI2": "叶绿素吸收比值指数2",
    "MTCI": "MERIS陆地叶绿素指数",
    "TCARI": "转换叶绿素吸收反射指数",
    "TCARI/OSAVI": "转换叶绿素吸收/优化土壤调节指数",
    "MCARI/OSAVI": "修正叶绿素吸收/优化土壤调节指数",
    "MCARI/MTVI2": "修正叶绿素吸收/修正三角植被指数2",
    "NDRE": "归一化红边指数",
    "NDRE1": "归一化红边指数1",
    "NDRE2": "归一化红边指数2",
    "RENDVI": "红边归一化植被指数",
    "NDVI705": "归一化植被指数705",
    "mNDVI": "修正归一化植被指数",
    "mND750/705": "修正归一化750/705",
    "mND680": "修正归一化680",
    "SR": "比值指数",
    "MSR": "修正比值指数",
    "MSR670": "修正比值指数670",
    "MSR705": "修正比值指数705",
    "MSR705/445": "修正比值指数705/445",
    "MSRNir/Red": "修正比值指数(近红外/红)",
    "RDVI": "重归一化植被指数",
    "WDRVI": "宽动态范围植被指数",
    "BWDRVI": "蓝色宽动态范围植被指数",
    "GBNDVI": "绿蓝归一化植被指数",
    "GRNDVI": "绿红归一化植被指数",
    "NIRv": "近红外反射率植被指数",
    "ARVI": "抗大气植被指数",
    "ARVI2": "抗大气植被指数2",
    "GARI": "绿色抗大气植被指数",
    "AFRI1600": "气溶胶自由植被指数1600",
    "AFRI2100": "气溶胶自由植被指数2100",
    "VARI": "可见光抗大气指数",
    "VARIgreen": "绿色可见光抗大气指数",
    "GLI": "绿叶指数",
    "ExG": "超绿指数",
    "ExR": "超红指数",
    "ExGR": "超绿超红差值指数",
    "CIVE": "彩色植被指数",
    "VEG": "植被指数",
    "COM1": "综合指数1",
    "COM2": "综合指数2",
    "GRVI": "绿红比值指数",
    "MGRVI": "修正绿红比值指数",
    "RGBVI": "红绿蓝植被指数",
    "IKAW": "IKAW指数",
    "IPVI": "红外百分比植被指数",
    "TNDVI": "变换归一化植被指数",
    "REIP": "红边拐点位置",
    "SIPI": "结构不敏感色素指数",
    "PSRI": "植物衰老反射指数",
    "PRI": "光化学反射指数",
    "PRI*": "光化学反射指数(修正)",
    "SIPI2": "结构不敏感色素指数2",
    "PSRI2": "植物衰老反射指数2",
    "CRI550": "类胡萝卜素反射指数550",
    "CRI700": "类胡萝卜素反射指数700",
    "ARI": "花青素反射指数",
    "mARI": "修正花青素反射指数",
    "NPCI": "归一化色素叶绿素指数",
    "NPQI": "归一化生理反射指数",
    "CAI": "纤维素吸收指数",
    "NDLI": "归一化木质素指数",
    "NDNI": "归一化氮指数",
    "NDNI2": "归一化氮指数2",
    "NRI": "氮反射指数",
    "SIWSI": "短波红外水分胁迫指数",
    "LWCI": "叶片水分含量指数",
    "HI": "水分指数",
    "HDWI": "湿度干旱水体指数",
    "MSI": "水分胁迫指数",
    "NDII": "归一化差值红外指数",
    "NDII6": "归一化差值红外指数6",
    "NDII7": "归一化差值红外指数7",
    "STSI": "土壤质地指数",
    "BI": "亮度指数",
    "BI2": "亮度指数2",
    "SI": "盐分指数",
    "SI1": "盐分指数1",
    "SI2": "盐分指数2",
    "SI3": "盐分指数3",
    "NDSI2": "归一化差值盐分指数",
    "NDSI3": "归一化差值盐分指数2",
    "YVI": "黄度植被指数",
    "GYVI": "绿黄植被指数",
    "MYVI": "Misra黄度植被指数",
    "MGVI": "Misra绿色植被指数",
    "MNSI": "Misra非此指数",
    "MSBI": "Misra土壤亮度指数",
    "GVMI": "全球植被水分指数",
    "LSWI2": "地表水体指数2",
    "GVWI": "全球植被水体指数",
    "SWCI": "盐分水体指数",
    "SWC": "盐分含量指数",
    "BSI": "裸土指数",
    "NBSI": "归一化裸土指数",
    "NDSWRI": "归一化差值盐分水体反射指数",
    "DWSI": "干旱水分胁迫指数",
    "DSWI": "病害水分胁迫指数",
    "DSWI-5": "病害水分胁迫指数5",
    "CWSI": "作物水分胁迫指数",
    "CWSI2": "作物水分胁迫指数2",
    "CWSI3": "作物水分胁迫指数3",
    "CWSI4": "作物水分胁迫指数4",
    "CWSI5": "作物水分胁迫指数5",
    "GrWDRVI": "绿色宽动态范围植被指数",
    "MGWDRVI": "修正绿色宽动态范围植被指数",
    "YNDVI": "黄色归一化植被指数",
    "YDRVI": "黄色差值植被指数",
    "YRVI": "黄色比值植被指数",
    "YSAVI": "黄色土壤调节植被指数",
    "YOSAVI": "黄色优化土壤调节植被指数",
    "YMSAVI": "黄色修正土壤调节植被指数",
    "YMCARI": "黄色修正叶绿素吸收指数",
    "YTCARI": "黄色转换叶绿素吸收指数",
    "YMCARI1": "黄色修正叶绿素吸收指数1",
    "YMCARI2": "黄色修正叶绿素吸收指数2",
    "YMTVI1": "黄色修正三角植被指数1",
    "YMTVI2": "黄色修正三角植被指数2",
    "YCIrededge": "黄色叶绿素红边指数",
    "YMTCI": "黄色MERIS陆地叶绿素指数",
    "YNDRE": "黄色归一化红边指数",
    "YRENDVI": "黄色红边归一化植被指数",
    "YNDVI705": "黄色归一化植被指数705",
    "YmNDVI": "黄色修正归一化植被指数",
    "YmND750/705": "黄色修正归一化750/705",
    "YMSR": "黄色修正比值指数",
    "YMSR670": "黄色修正比值指数670",
    "YMSR705": "黄色修正比值指数705",
    "YMSR705/445": "黄色修正比值指数705/445",
    "YMSRNir/Red": "黄色修正比值指数(近红外/红)",
    "YRDVI": "黄色重归一化植被指数",
    "YWDRVI": "黄色宽动态范围植被指数",
    "YBWDRVI": "黄色蓝色宽动态范围植被指数",
    "YGBNDVI": "黄色绿蓝归一化植被指数",
    "YGRNDVI": "黄色绿红归一化植被指数",
    "YARVI": "黄色抗大气植被指数",
    "YGARI": "黄色绿色抗大气植被指数",
    "YVARI": "黄色可见光抗大气指数",
    "YGLI": "黄色绿叶指数",
    "YExG": "黄色超绿指数",
    "YExR": "黄色超红指数",
    "YExGR": "黄色超绿超红差值指数",
    "YCIVE": "黄色彩色植被指数",
    "YVEG": "黄色植被指数",
    "YCOM1": "黄色综合指数1",
    "YCOM2": "黄色综合指数2",
    "YGRVI": "黄色绿红比值指数",
    "YMGRVI": "黄色修正绿红比值指数",
    "YRGBVI": "黄色红绿蓝植被指数",
    "YIKAW": "黄色IKAW指数",
    "YIPVI": "黄色红外百分比植被指数",
    "YTNDVI": "黄色变换归一化植被指数",
    "YREIP": "黄色红边拐点位置",
    "YSIPI": "黄色结构不敏感色素指数",
    "YPSRI": "黄色植物衰老反射指数",
    "YPRI": "黄色光化学反射指数",
    "YSIPI2": "黄色结构不敏感色素指数2",
    "YPSRI2": "黄色植物衰老反射指数2",
    "YCRI550": "黄色类胡萝卜素反射指数550",
    "YCRI700": "黄色类胡萝卜素反射指数700",
    "YARI": "黄色花青素反射指数",
    "YmARI": "黄色修正花青素反射指数",
    "YNPCI": "黄色归一化色素叶绿素指数",
    "YNPQI": "黄色归一化生理反射指数",
    "YCAI": "黄色纤维素吸收指数",
    "YNDLI": "黄色归一化木质素指数",
    "YNDNI": "黄色归一化氮指数",
    "YNDNI2": "黄色归一化氮指数2",
    "YNRI": "黄色氮反射指数",
    "YSIWSI": "黄色短波红外水分胁迫指数",
    "YLWCI": "黄色叶片水分含量指数",
    "YHI": "黄色水分指数",
    "YHDWI": "黄色湿度干旱水体指数",
    "YMSI": "黄色水分胁迫指数",
    "YNDII": "黄色归一化差值红外指数",
    "YNDII6": "黄色归一化差值红外指数6",
    "YNDII7": "黄色归一化差值红外指数7",
    "YSTSI": "黄色土壤质地指数",
    "YBI": "黄色亮度指数",
    "YBI2": "黄色亮度指数2",
    "YSI": "黄色盐分指数",
    "YSI1": "黄色盐分指数1",
    "YSI2": "黄色盐分指数2",
    "YSI3": "黄色盐分指数3",
    "YNDSI2": "黄色归一化差值盐分指数",
    "YNDSI3": "黄色归一化差值盐分指数2",
    "YYVI": "黄色黄度植被指数",
    "YGYVI": "黄色绿黄植被指数",
    "YMYVI": "黄色Misra黄度植被指数",
    "YMGVI": "黄色Misra绿色植被指数",
    "YMNSI": "黄色Misra非此指数",
    "YMSBI": "黄色Misra土壤亮度指数",
    "YGVMI": "黄色全球植被水分指数",
    "YLSWI2": "黄色地表水体指数2",
    "YGVWI": "黄色全球植被水体指数",
    "YSWCI": "黄色盐分水体指数",
    "YSWC": "黄色盐分含量指数",
    "YBSI": "黄色裸土指数",
    "YNBSI": "黄色归一化裸土指数",
    "YNDSWRI": "黄色归一化差值盐分水体反射指数",
    "YDWSI": "黄色干旱水分胁迫指数",
    "YDSWI": "黄色病害水分胁迫指数",
    "YDSWI-5": "黄色病害水分胁迫指数5",
    "YCWSI": "黄色作物水分胁迫指数",
    "YCWSI2": "黄色作物水分胁迫指数2",
    "YCWSI3": "黄色作物水分胁迫指数3",
    "YCWSI4": "黄色作物水分胁迫指数4",
    "YCWSI5": "黄色作物水分胁迫指数5",
    # 补充常见缩写中文
    "MTVI": "修正三角植被指数",
    "VREI": "Vogelmann红边指数",
    "VREI1": "Vogelmann红边指数1",
    "VREI2": "Vogelmann红边指数2",
    "LAIDI": "叶面积指数确定指数",
    "NDBleaf": "叶冠生物量指数",
    "Rededge1": "红边1号指数",
    "Rededge2": "红边2号指数",
    "SR670": "比值指数670",
    "SR705": "比值指数705",
    "SR705/445": "比值指数705/445",
    "NDVI705": "归一化植被指数705",
    "NDVI750/650": "归一化植被指数750/650",
    "NDVIg": "绿色归一化植被指数",
    "NDVIc": "校正归一化植被指数",
    "NDVI rededge": "红边归一化植被指数",
    "NDVI690-710": "归一化植被指数690-710",
    "OSAVI2": "优化土壤调节植被指数2",
    "MSAVI2": "修正土壤调节植被指数2",
    "FCI": "森林覆盖指数",
    "FCI1": "森林覆盖指数1",
    "FCI2": "森林覆盖指数2",
    "LWVI": "叶片水分植被指数",
    "LWVI1": "叶片水分植被指数1",
    "LWVI2": "叶片水分植被指数2",
    "NDII6": "归一化差值红外指数6",
    "NDII7": "归一化差值红外指数7",
    "NDMSI": "归一化差值水分指数",
    "NMDI": "归一化多波段干旱指数",
    "NDPI": "归一化池塘指数",
    "NDPonI": "归一化池塘指数",
    "SWI": "简单水体指数",
    "WBI": "水体波段指数",
    "WRI": "水体比值指数",
    "TGI": "三角绿度指数",
    "TDVI": "变换差值植被指数",
    "RDVI": "重归一化植被指数",
    "MNLI": "修正非线性指数",
    "NLI": "非线性指数",
    "MCARI1510": "修正叶绿素吸收指数1510",
    "MCARI705": "修正叶绿素吸收指数705",
    "MCARI710": "修正叶绿素吸收指数710",
    "MSR670": "修正比值指数670",
    "MSR705": "修正比值指数705",
    "MSR705/445": "修正比值指数705/445",
    "MSRNir/Red": "修正比值指数(近红外/红)",
    "ND850/1788/1928": "归一化差值850/1788/1928",
    "ND850/2218/1928": "归一化差值850/2218/1928",
    "MD734/747/715/72": "修正归一化差值734/747/715/72",
    "MND750/705": "修正归一化差值750/705",
    "DLAI": "差值叶面积指数",
    "DWSI": "病害水分胁迫指数",
}

# 中文名称 → 缩写 反向映射（用于中文搜索）
# 注意：如果有多个缩写映射到同一中文名，只保留第一个
ZH_TO_ABBREV = {}
for k, v in ZH_NAMES.items():
    if v not in ZH_TO_ABBREV:
        ZH_TO_ABBREV[v] = k

# 应用领域中文翻译
ZH_APPLICATIONS = {
    "Agriculture": "农业",
    "Agriculture - Crop parameters": "农业 - 作物参数",
    "Agriculture - Crop yield": "农业 - 作物产量",
    "Agriculture - Irrigation": "农业 - 灌溉",
    "Agriculture - Land management": "农业 - 土地管理",
    "Agriculture - Precision Crop Management": "农业 - 精准作物管理",
    "Alpin": "高山",
    "Fire": "火灾",
    "Forestry": "林业",
    "Forestry - Boreal": "林业 - 寒带",
    "Geology": "地质",
    "Geology - Mining area": "地质 - 矿区",
    "Geology - Rock": "地质 - 岩石",
    "Hyperspectral remote sensing": "高光谱遥感",
    "Hyperspectral remote sensing - Red-edge position": "高光谱遥感 - 红边位置",
    "Metal": "金属",
    "Metal - Heavy metal contamination": "金属 - 重金属污染",
    "Metal - Iron": "金属 - 铁",
    "Oil": "石油",
    "Soil": "土壤",
    "Soil - Arsenic": "土壤 - 砷",
    "Soil - Contamination": "土壤 - 污染",
    "Soil - Salinity": "土壤 - 盐分",
    "Vegetation": "植被",
    "Vegetation - Biomass": "植被 - 生物量",
    "Vegetation - Cellulose": "植被 - 纤维素",
    "Vegetation - Chlorophyll": "植被 - 叶绿素",
    "Vegetation - Fluorescence": "植被 - 荧光",
    "Vegetation - LAI": "植被 - 叶面积指数",
    "Vegetation - Lignin": "植被 - 木质素",
    "Vegetation - Nitrogen content": "植被 - 氮含量",
    "Vegetation - Nitrogen stress": "植被 - 氮胁迫",
    "Vegetation - PAR": "植被 - 光合有效辐射",
    "Vegetation - Protein": "植被 - 蛋白质",
    "Vegetation - Salinity stress": "植被 - 盐胁迫",
    "Vegetation - Starch": "植被 - 淀粉",
    "Vegetation - Stress": "植被 - 胁迫",
    "Vegetation - Sugar": "植被 - 糖分",
    "Vegetation - Vitality": "植被 - 活力",
    "Vegetation - Water": "植被 - 水分",
    "Vegetation - Water stress": "植被 - 水分胁迫",
    "Vegetation - Water use efficiency": "植被 - 水分利用效率",
    "Water resource management": "水资源管理",
}

# 传感器平台中文翻译
ZH_PLATFORMS = {
    "airborne": "航空",
    "ENVISAT": "ENVISAT卫星",
    "EO-1": "EO-1卫星",
    "Proba": "Proba卫星",
    "Landsat": "Landsat卫星",
    "Sentinel": "Sentinel卫星",
    "MODIS": "MODIS传感器",
    "NOAA": "NOAA卫星",
    "NASA": "NASA",
    "ESA": "欧洲航天局",
    "JAXA": "日本宇宙航空研究开发机构",
    "ISRO": "印度空间研究组织",
    "DLR": "德国航空航天中心",
    "USGS": "美国地质调查局",
}

# 其他植被指数数据库/网站
OTHER_DATABASES = [
    {
        "name": "Sentinel Hub Custom Scripts - Index Database",
        "url": "https://sentinel-hub.github.io/custom-scripts/sentinel-2/indexdb/",
        "description": "基于IDB数据的Sentinel-2自定义脚本，可直接在Sentinel Hub平台使用",
        "language": "英文",
    },
    {
        "name": "Spectral Indices - Sentinel Hub Documentation",
        "url": "https://docs.sentinel-hub.com/api/latest/data/sen2-l2a/",
        "description": "Sentinel Hub官方文档中的光谱指数说明",
        "language": "英文",
    },
    {
        "name": "MODIS Vegetation Index Products (NASA)",
        "url": "https://modis.gsfc.nasa.gov/data/dataprod/mod13.php",
        "description": "NASA MODIS植被指数产品官方页面（MOD13系列）",
        "language": "英文",
    },
    {
        "name": "ENVI Spectral Indices - Harris Geospatial",
        "url": "https://www.l3harrisgeospatial.com/docs/spectralindices.html",
        "description": "ENVI软件中的光谱指数工具文档，包含常用指数公式",
        "language": "英文",
    },
    {
        "name": "Google Earth Engine Data Catalog",
        "url": "https://developers.google.com/earth-engine/datasets/catalog",
        "description": "Google Earth Engine数据目录，包含多种植被指数数据集",
        "language": "英文",
    },
    {
        "name": "USGS Spectral Library",
        "url": "https://speclab.cr.usgs.gov/spectral-lib.html",
        "description": "【不是植被指数库】美国地质调查局光谱库，包含矿物、岩石等地物光谱曲线（spectral signatures），用于地物光谱识别，但不包含植被指数公式",
        "language": "英文",
        "note": "光谱特征库，非植被指数数据库",
    },
    {
        "name": "Index DataBase (IDB) - 本项目数据源",
        "url": "https://www.indexdatabase.de/",
        "description": "本项目数据来源，最全面的遥感植被指数数据库",
        "language": "英文",
    },
    {
        "name": "遥感指数全面汇总 - CSDN",
        "url": "https://blog.csdn.net/qq_41520741/article/details/128000000",
        "description": "中文遥感指数汇总博客，包含常用指数公式和说明",
        "language": "中文",
    },
    {
        "name": "常用植被指数计算公式 - 知乎",
        "url": "https://zhuanlan.zhihu.com/p/365793028",
        "description": "知乎专栏文章，详细介绍常用植被指数原理和计算方法",
        "language": "中文",
    },
    {
        "name": "Earth Observation Foundation - EO Database",
        "url": "https://eodatabase.skywatch.co/",
        "description": "地球观测数据库，包含多种遥感指数说明",
        "language": "英文",
    },
]


def load_data():
    """加载所有数据"""
    data = {}
    for fname in ["indices.json", "sensors.json", "applications.json", "envi_vegetation_indices.json", "sentinel_hub_indices.json", "modis_vi_products.json"]:
        fpath = os.path.join(DATA_DIR, fname)
        if os.path.exists(fpath):
            with open(fpath, "r", encoding="utf-8") as f:
                key = fname.replace(".json", "")
                data[key] = json.load(f)
    return data


def get_index_url(index_id):
    """获取指数在IDB网站上的原始URL"""
    return f"{BASE_URL}/db/i-single.php?id={index_id}"


def get_sensor_url(sensor_id):
    """获取传感器在IDB网站上的原始URL"""
    return f"{BASE_URL}/db/s-single.php?id={sensor_id}"


def get_application_url(app_id):
    """获取应用在IDB网站上的原始URL"""
    return f"{BASE_URL}/db/a-single.php?id={app_id}"


def get_zh_name(abbrev):
    """获取指数中文名称，支持复合缩写（如NDVI705→归一化植被指数+705）"""
    # 直接匹配
    if abbrev in ZH_NAMES:
        return ZH_NAMES[abbrev]
    
    # 尝试提取基础缩写（去掉尾部数字/后缀）
    base_match = re.match(r'^([A-Za-z]+)', abbrev)
    if base_match:
        base_abbrev = base_match.group(1)
        if base_abbrev in ZH_NAMES:
            base_zh = ZH_NAMES[base_abbrev]
            suffix = abbrev[len(base_abbrev):]
            if suffix:
                return f"{base_zh}({suffix})"
            return base_zh
    
    # 尝试部分匹配（如 NDVI690-710 → NDVI）
    for i in range(len(abbrev), 0, -1):
        prefix = abbrev[:i]
        if prefix in ZH_NAMES:
            suffix = abbrev[i:]
            if suffix:
                return f"{ZH_NAMES[prefix]}({suffix})"
            return ZH_NAMES[prefix]
    
    return ""


def get_zh_application(name):
    """获取应用领域中文名"""
    return ZH_APPLICATIONS.get(name, name)


def search_indices(query, data, max_results=10):
    """搜索指数"""
    query_lower = query.lower()
    results = []
    
    # 检查是否是中文名称搜索，如果是则转换为缩写
    zh_abbrev = ZH_TO_ABBREV.get(query, "")
    if not zh_abbrev:
        # 尝试部分匹配中文名
        for zh_name, abbrev in ZH_TO_ABBREV.items():
            if query in zh_name:
                zh_abbrev = abbrev
                break
    
    for idx in data.get("indices", []):
        score = 0
        name = idx.get("name", "").lower()
        abbrev = idx.get("abbreviation", "").lower()
        formula = idx.get("formula", "").lower()
        
        # 直接匹配
        if query_lower == name or query_lower == abbrev:
            score = 100
        # 中文名完全匹配
        elif zh_abbrev and abbrev == zh_abbrev.lower():
            score = 95
        # 中文名缩写包含在指数缩写中
        elif zh_abbrev and abbrev.startswith(zh_abbrev.lower()):
            score = 85
        # 开头匹配
        elif name.startswith(query_lower) or abbrev.startswith(query_lower):
            score = 80
        # 包含匹配
        elif query_lower in name or query_lower in abbrev:
            score = 60
        # 单词边界匹配
        elif re.search(r'\b' + re.escape(query_lower) + r'\b', name):
            score = 50
        # 公式内容匹配
        elif query_lower in formula:
            score = 30
        
        if score > 0:
            results.append((score, idx))
    
    results.sort(key=lambda x: x[0], reverse=True)
    return [idx for score, idx in results[:max_results]]


def get_index_by_id(index_id, data):
    """根据ID获取指数"""
    for idx in data.get("indices", []):
        if idx["id"] == index_id:
            return idx
    return None


def list_all_applications(data):
    """列出所有应用领域"""
    return data.get("applications", [])


def list_all_sensors(data, max_results=50):
    """列出所有传感器"""
    return data.get("sensors", [])[:max_results]


def get_statistics(data):
    """获取数据库统计信息"""
    idb_count = len(data.get("indices", []))
    envi_count = len(data.get("envi_vegetation_indices", []))
    sentinel_count = len(data.get("sentinel_hub_indices", []))
    modis_data = data.get("modis_vi_products", {})
    modis_count = len(modis_data.get("products", []))
    return {
        "total_indices": idb_count + envi_count + sentinel_count,
        "idb_indices": idb_count,
        "envi_indices": envi_count,
        "sentinel_indices": sentinel_count,
        "modis_products": modis_count,
        "total_sensors": len(data.get("sensors", [])),
        "total_applications": len(data.get("applications", [])),
        "sources": [
            "IndexDatabase.de (IDB)",
            "ENVI Documentation (NV5)",
            "Sentinel Hub Custom Scripts",
            "NASA MODIS MOD13",
        ],
        "source_url": BASE_URL,
        "description": "遥感植被指数综合数据库（IDB + ENVI + Sentinel + MODIS）",
        "description_en": "A comprehensive database of remote sensing vegetation indices (IDB + ENVI + Sentinel + MODIS)",
    }


def format_index_bilingual(idx):
    """双语格式化指数信息"""
    lines = []
    zh_name = get_zh_name(idx.get("abbreviation", ""))
    lines.append(f"  名称/Name: {idx.get('name', 'N/A')}")
    if zh_name:
        lines.append(f"  中文/Chinese: {zh_name}")
    lines.append(f"  缩写/Abbreviation: {idx.get('abbreviation', 'N/A')}")
    lines.append(f"  公式/Formula: {idx.get('formula', 'N/A')}")
    if idx.get("variables"):
        lines.append(f"  变量/Variables: {idx['variables']}")
    lines.append(f"  来源/Source: {idx.get('source', 'N/A')}")
    lines.append(f"  兼容传感器数/Compatible Sensors: {idx.get('n_sensors', 0)}")
    lines.append(f"  应用领域数/Applications: {idx.get('n_applications', 0)}")
    lines.append(f"  参考文献数/References: {idx.get('n_references', 0)}")
    lines.append(f"  原始链接/URL: {get_index_url(idx.get('id', 0))}")
    return "\n".join(lines)


def main(args=None):
    """主入口"""
    if args is None:
        args = sys.argv[1:]
    
    if not args:
        return {
            "success": False,
            "message": "用法 / Usage:\n"
                       "  python vegetation_indices.py <command> [args]\n"
                       "命令 / Commands:\n"
                       "  search <关键词> [--limit N]  搜索IDB指数(519个) / Search IDB indices\n"
                       "  envi [关键词] [--limit N]    搜索ENVI指数(56个) / Search ENVI indices\n"
                       "  sentinel [关键词] [--limit N] 搜索Sentinel-2指数(248个) / Search Sentinel-2\n"
                       "  modis [关键词] [--limit N]   查看MODIS产品(12个) / MODIS VI products\n"
                       "  show <id>                    查看IDB指数详情 / Show IDB details\n"
                       "  applications                  应用领域 / Applications\n"
                       "  sensors                       传感器 / Sensors\n"
                       "  stats                         统计 / Statistics\n"
                       "  databases                     其他数据库 / Other databases\n"
                       "  help                         帮助 / Help",
        }
    
    data = load_data()
    command = args[0].lower()
    
    if command == "search":
        if len(args) < 2:
            return {"success": False, "message": "用法 / Usage: search <关键词/query>"}
        
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
            return {"success": False, "message": "用法 / Usage: search <关键词/query>"}
        
        results = search_indices(query, data, max_results)
        
        if not results:
            return {
                "success": True,
                "query": query,
                "num_results": 0,
                "results": [],
                "message": f"未找到与 '{query}' 相关的指数 / No indices found for '{query}'",
                "suggestion": f"建议直接访问 IDB 网站搜索 / Try searching directly on the IDB website: {BASE_URL}/db/i.php",
                "suggestion_url": f"{BASE_URL}/db/i.php",
            }
        
        # Add URLs to results
        for r in results:
            r["url"] = get_index_url(r["id"])
            zh = get_zh_name(r.get("abbreviation", ""))
            if zh:
                r["zh_name"] = zh
        
        return {
            "success": True,
            "query": query,
            "num_results": len(results),
            "results": results,
            "message": f"找到 {len(results)} 个与 '{query}' 相关的指数 / Found {len(results)} indices for '{query}'",
        }
    
    elif command == "show":
        if len(args) < 2:
            return {"success": False, "message": "用法 / Usage: show <id>"}
        
        try:
            index_id = int(args[1])
        except ValueError:
            return {"success": False, "message": "ID必须是数字 / ID must be a number"}
        
        idx = get_index_by_id(index_id, data)
        if not idx:
            return {
                "success": False,
                "message": f"未找到ID为 {index_id} 的指数 / Index with ID {index_id} not found",
                "suggestion": f"建议直接访问 IDB 网站搜索 / Try searching on: {BASE_URL}/db/i.php",
            }
        
        idx["url"] = get_index_url(idx["id"])
        zh = get_zh_name(idx.get("abbreviation", ""))
        if zh:
            idx["zh_name"] = zh
        
        return {
            "success": True,
            "index": idx,
            "message": f"指数详情 / Index details for ID {index_id}",
        }
    
    elif command == "applications":
        apps = list_all_applications(data)
        # Add Chinese names
        for app in apps:
            app["zh_name"] = get_zh_application(app.get("name", ""))
            app["url"] = get_application_url(app.get("id", 0))
        
        return {
            "success": True,
            "num_applications": len(apps),
            "applications": apps,
            "message": f"共 {len(apps)} 个应用领域 / Found {len(apps)} applications",
        }
    
    elif command == "sensors":
        sensors = list_all_sensors(data)
        for s in sensors:
            s["url"] = get_sensor_url(s.get("id", 0))
        
        return {
            "success": True,
            "num_sensors": len(sensors),
            "sensors": sensors,
            "message": f"显示 {len(sensors)} 个传感器 / Showing {len(sensors)} sensors",
        }
    
    elif command == "stats":
        stats = get_statistics(data)
        return {
            "success": True,
            "statistics": stats,
            "message": "数据库统计 / Database statistics",
        }
    
    elif command == "databases":
        all_dbs = OTHER_DATABASES + [
            {
                "name": "ENVI Spectral Indices (NV5 GeoSpatial)",
                "url": "https://www.nv5geospatialsoftware.com/docs/alphabeticallistspectralindices.html",
                "description": "ENVI软件文档中的光谱指数列表，包含植被指数公式（图片形式）。本Skill已爬取并整合其56个植被指数数据",
                "language": "英文",
                "note": "已整合到本Skill的envi命令中",
                "num_indices": 56,
            },
            {
                "name": "Sentinel Hub Custom Scripts",
                "url": "https://sentinel-hub.github.io/custom-scripts/sentinel-2/indexdb/",
                "description": "基于IDB数据为Sentinel-2卫星定制的遥感指数集合，包含248个指数的JavaScript实现。本Skill已爬取并整合",
                "language": "英文/代码",
                "note": "已整合到本Skill的sentinel命令中",
                "num_indices": 248,
            },
            {
                "name": "NASA MODIS Vegetation Index (MOD13)",
                "url": "https://modis.gsfc.nasa.gov/data/dataprod/mod13.php",
                "description": "NASA官方MODIS植被指数产品（NDVI/EVI），包括12个产品（16天/月度，250m-0.05°分辨率）。本Skill已爬取产品信息",
                "language": "英文",
                "note": "已整合到本Skill的modis命令中",
                "num_products": 12,
            },
        ]
        return {
            "success": True,
            "num_databases": len(all_dbs),
            "databases": all_dbs,
            "message": f"共 {len(all_dbs)} 个植被指数相关数据库/网站 / {len(all_dbs)} vegetation index databases/websites",
        }
    
    elif command == "envi":
        # Search ENVI vegetation indices
        max_results = 20
        query = ""
        if len(args) > 1:
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
            query = " ".join(query_parts).lower()
        
        envi_data = data.get("envi_vegetation_indices", [])
        results = []
        
        for idx in envi_data:
            if not query or query in idx.get("abbreviation", "").lower() or query in idx.get("name", "").lower() or query in idx.get("category", "").lower() or query in idx.get("formula", "").lower():
                results.append(idx)
        
        results = results[:max_results]
        
        # Add Chinese names
        for r in results:
            zh = get_zh_name(r.get("abbreviation", ""))
            if zh:
                r["zh_name"] = zh
        
        return {
            "success": True,
            "source": "ENVI Documentation (NV5 GeoSpatial)",
            "source_url": "https://www.nv5geospatialsoftware.com/docs/",
            "num_results": len(results),
            "total_available": len(envi_data),
            "results": results,
            "message": f"ENVI数据库中找到 {len(results)} 个指数 / Found {len(results)} indices in ENVI database",
            "note": "ENVI公式图片可访问各指数的 formula_image 字段查看",
        }
    
    elif command == "sentinel":
        # Search Sentinel Hub indices
        max_results = 20
        query = ""
        if len(args) > 1:
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
            query = " ".join(query_parts).lower()
        
        sentinel_data = data.get("sentinel_hub_indices", [])
        results = []
        
        for idx in sentinel_data:
            if not query or query in idx.get("abbreviation", "").lower() or query in idx.get("name", "").lower():
                results.append(idx)
        
        results = results[:max_results]
        
        for r in results:
            zh = get_zh_name(r.get("abbreviation", ""))
            if zh:
                r["zh_name"] = zh
        
        return {
            "success": True,
            "source": "Sentinel Hub Custom Scripts",
            "source_url": "https://sentinel-hub.github.io/custom-scripts/sentinel-2/indexdb/",
            "num_results": len(results),
            "total_available": len(sentinel_data),
            "sensor": "Sentinel-2",
            "results": results,
            "message": f"Sentinel-2数据库中找到 {len(results)} 个指数 / Found {len(results)} indices for Sentinel-2",
            "note": "Sentinel-2专用指数列表，支持直接在Copernicus Browser中使用",
        }
    
    elif command == "modis":
        # Show MODIS VI products
        modis_data = data.get("modis_vi_products", {})
        products = modis_data.get("products", [])
        algorithm = modis_data.get("algorithm", {})
        
        max_results = 20
        query = ""
        if len(args) > 1:
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
            query = " ".join(query_parts).lower()
        
        filtered = products
        if query:
            filtered = [p for p in products if query in p.get("name", "").lower() or query in p.get("name_cn", "") or query in p.get("platform", "").lower() or query in p.get("spatial_resolution", "").lower()]
        
        filtered = filtered[:max_results]
        
        return {
            "success": True,
            "source": "NASA MODIS",
            "source_url": "https://modis.gsfc.nasa.gov/data/dataprod/mod13.php",
            "algorithm": algorithm,
            "num_products": len(filtered),
            "total_products": len(products),
            "products": filtered,
            "message": f"MODIS植被指数产品 {len(filtered)}/{len(products)} / MODIS VI Products {len(filtered)}/{len(products)}",
        }
    
    elif command == "help":
        return {
            "success": True,
            "message": "植被指数查询工具 / Vegetation Indices Query Tool\n"
                       "命令 / Commands:\n"
                       "  search <关键词> [--limit N]  搜索IDB指数（支持中英文）\n"
                       "  envi [关键词] [--limit N]    搜索ENVI植被指数（含公式）\n"
                       "  sentinel [关键词] [--limit N] 搜索Sentinel-2专用指数(248个)\n"
                       "  modis [关键词] [--limit N]   查看MODIS植被指数产品(12个)\n"
                       "  show <id>                    查看IDB指数详情（含原始链接）\n"
                       "  applications                 列出所有应用领域（含中文翻译）\n"
                       "  sensors                      列出所有传感器/卫星\n"
                       "  stats                        数据库统计信息\n"
                       "  databases                    其他植被指数数据库/网站列表\n"
                       "  help                         帮助信息",
        }
    
    else:
        return {
            "success": False,
            "message": f"未知命令 / Unknown command: {command}. 使用 'help' 查看帮助 / Use 'help' for usage.",
        }


if __name__ == "__main__":
    result = main()
    print(json.dumps(result, indent=2, ensure_ascii=False))
