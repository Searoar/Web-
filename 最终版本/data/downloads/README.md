# `downloads/` 目录说明

本目录存放**按 `DATASETS.md` 链接自动或半自动拉取**的文件，便于离线查阅与作业引用。

## 已成功拉取（可直接打开）

| 文件 | 说明 |
|------|------|
| `transport/naptan_access_nodes_HEAD_2mb.csv` | NaPTAN 全国访问点 CSV 的**前 2MB 样本**（全量极大，官方 API 见下）。 |
| `transport/nptg_localities.csv` | NPTG 地名/ locality **完整** CSV（约 4.8MB，来自 DfT API）。 |
| `transport/orr_home.html` | ORR 官网首页存档（统计 Excel 请在站内用浏览器下载）。 |
| `meta/ckan_package_show_naptan.json` | data.gov.uk CKAN `package_show?id=naptan`，含官方 CSV/XML 直链。 |
| `meta/ckan_naptan_search.json` | （若存在）早期检索结果备份。 |
| `heritage/historic_england_open_data_hub.html` | Historic England ArcGIS Hub 入口页。 |
| `dark_skies/govuk_natural_england.html` | Natural England（gov.uk）机构页，可作国家公园/自然政策引用入口。 |
| `portals/data_gov_uk_search_naptan.html` | data.gov.uk 搜索「naptan」结果页。 |
| `portals/kaggle_datasets.html` | Kaggle 数据集首页（轻量）。 |
| `portals/google_dataset_search.html` | Google Dataset Search 首页存档。 |

## 全量 NaPTAN CSV / XML（勿盲目拖进 Git）

官方直链（亦在 `meta/ckan_package_show_naptan.json` 的 `resources` 中）：

- CSV：`https://naptan.api.dft.gov.uk/v1/access-nodes?dataFormat=csv`
- XML：`https://naptan.api.dft.gov.uk/v1/access-nodes?dataFormat=xml`

建议在本地用浏览器下载或 `curl`/wget **流式**保存到本目录外的大磁盘路径，**不要**提交到公开仓库。

## 自动下载失败时常见原因

- **Cloudflare / 反机器人**（如 UNESCO WHC）：保存下来的可能是挑战页，需浏览器访问。
- **403 / TLS**：脚本与 curl 均可能被拒绝；请手动打开 `DATASETS.md` 原链接。
- **gov.uk 改版**：集合类 URL 会 404；已改用 `Natural England` 等仍有效的页面作替代存档。

## 重新生成

在项目根目录执行：

```bash
python data/scripts/download_from_datasets_md.py
```

详见同目录 `DOWNLOAD_LOG.md`（脚本运行日志）。
