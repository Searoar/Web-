# 数据集资源说明（故事与星空慢游规划 API）

本文档列出与**慢行交通 / 文学与影视取景 / 暗夜星空 / 文化遗产**相关的公开数据源，并附**本仓库 `data/` 内已保存的样本文件**说明。作业报告与代码中引用时请写明**来源与许可证**。

---

## 1. 交通与低碳出行（铁路 / 公共交通节点）

| 用途 | 数据集 | 获取方式 |
|------|--------|----------|
| 车站/站点坐标、名称、模式（铁路/公交等） | **NaPTAN**（National Public Transport Access Nodes） | 英国政府开放数据，常通过 **data.gov.uk** 提供 NaPTAN 全量或分发表。 |
| 车站客流量、区域对比 | **ORR Station usage estimates**（Office of Rail and Road） | ORR 官网「Published statistics」→ Rail usage → Station usage；多为 **Excel (.xlsx)**。 |

**官方入口（链接）**

- data.gov.uk 目录检索（NaPTAN / public transport）：  
  https://www.data.gov.uk/search?q=naptan  
- NaPTAN 相关数据集示例页（ID 可能随发布更新，请以检索结果为准）：  
  https://www.data.gov.uk/dataset/08402372-0828-4e8b-8d1a-6475059bdd1d/national-public-transport-access-nodes  
- ORR 车站使用统计说明与下载：  
  https://www.orr.gov.uk/published-statistics/rail-usage/station-usage-estimates  
- ORR 数据门户（可检索媒体文件）：  
  https://dataportal.orr.gov.uk/

**许可证（通常）**：Open Government Licence v3.0（OGL）— 以各数据集页面声明为准。

**本仓库样本文件**

- `transport/naptan_stations_sample.csv`：按 NaPTAN 常见字段**自编少量示例行**（便于对齐你 API 的「经停 + 交通方式 + 距离」模型）；导入全量请从上述官方 NaPTAN 下载。
- `transport/orr_station_usage_sample.csv`：**结构示意**；真实数值请以 ORR 当年 Excel 为准。

---

## 2. 文化遗产与「叙事」锚点（世界遗产 / 登录建筑）

| 用途 | 数据集 | 获取方式 |
|------|--------|----------|
| 英格兰遗产名录空间数据（点/面、属性） | **NHLE**（National Heritage List for England） | Historic England **Open Data Hub**（ArcGIS Hub），可选 GeoJSON / Shapefile 等。 |
| 世界遗产名录（全球，含英国条目） | **UNESCO World Heritage Centre** | 官方列表 + 部分边界/元数据；可与 NHLE 交叉引用。 |

**官方入口（链接）**

- Historic England 数据下载总览：  
  https://historicengland.org.uk/listing/the-list/data-downloads/  
- Historic England Open Data Hub：  
  https://opendata-historicengland.hub.arcgis.com/  
- UNESCO 世界遗产列表（英国）：  
  https://whc.unesco.org/en/statesparties/gb  

**许可证（通常）**：Historic England 开放数据多标注 **Open Government Licence**；UNESCO 页面内容需遵守其版权与使用说明。

**本仓库样本文件**

- `heritage/nhle_world_heritage_sites_uk_sample.csv`：英国境内部分世界遗产**示例**（名称 + 粗略坐标），用于与「文学/影视线」POI 建模对齐；精化请用 NHLE 全量或 UNESCO 官方资料。

---

## 3. 暗夜星空与光环境（观星点 / 保护区）

| 用途 | 数据集 | 获取方式 |
|------|--------|----------|
| 国际暗夜场所（保护区/公园/储备等） | **IDA Dark Sky Places** | International Dark-Sky Association 官方 **Finder** 与各地公园页面。 |
| 英国国家公园与自然政策背景 | **gov.uk / Natural England** | 国家公园列表、自然英格兰出版物（可作区域划分与科普引用）。 |

**官方入口（链接）**

- IDA Dark Sky Places Finder：  
  https://www.darksky.org/our-work/conservation/idsp/finder/  
- 英国国家公园概览（政府站）：  
  https://www.gov.uk/government/collections/national-parks  

**许可证**：IDA 与各国公园网站条款不一；学术作业一般允许**引用事实与链接**；复制表格请查看各站 **Terms / Copyright**。

**本仓库样本文件**

- `dark_skies/uk_dark_sky_places_sample.csv`：英国及周边**少量**暗夜目的地示例（名称 + 大致坐标 + 分级说明）；扩展请用 IDA Finder 与公园官网。

---

## 4. 影视 / 文学取景与主题旅游（辅助叙事）

此类数据**很少**有单一政府 CSV；常见做法是：

- **VisitBritain / VisitEngland / VisitScotland** 的影视旅游专题页；
- 片方或目的地旅游局发布的取景清单；
- 自行整理维基百科等二次来源时，须在报告中声明**可追溯性与不确定性**。

**官方入口（链接）**

- VisitBritain 灵感与主题（含影视相关专题入口，页面会调整）：  
  https://www.visitbritain.com/gb/en  
- Screen Scotland / 取景资源：  
  https://www.screen.scot/  

**本仓库样本文件**

- `film_literary/filming_locations_uk_sample.csv`：面向课程演示的**少量公开取景地示例**（非官方全库）；正式项目请替换为可验证来源或自行爬取后清洗并注明许可。

---

## 5. 课程 Brief 中提到的聚合平台

- **Kaggle Datasets**：https://www.kaggle.com/datasets  
- **Google Dataset Search**：https://datasetsearch.research.google.com/  
- **UCI ML Repository**（偏机器学习，可作补充）：https://archive.ics.uci.edu/  

建议检索关键词：`UK rail`、`NaPTAN`、`UNESCO heritage`、`dark sky`、`film locations`、`tourism POI`。

---

## 6. 关于本目录中的文件

- 仓库内 CSV 多为**小样本 / 字段示意**，目的是让你快速写 **SQLAlchemy 导入脚本**与对接 API；**论文/报告中应引用上表官方链接**作为权威来源。
- 若需**全量**数据，请在有网络环境下从上述门户下载；部分 ORR 链接在自动化下载时可能返回 403，需**浏览器手动下载**或使用官方 API/条款允许的方式。

---

## 7. 建议在技术报告里写明的要点

1. 每个数据集的名称、发布机构、下载日期、许可证。  
2. 你对 CSV 做了哪些清洗（坐标系、字段映射、去重）。  
3. 若使用生成式 AI 辅助写导入脚本，按课程要求做 **GenAI 声明**并附对话摘录。  

最后更新：2026-04-08（随数据源网址改版，请以页面为准）。
