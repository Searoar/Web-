# 自动下载结果说明

本目录由 `data/scripts/download_from_datasets_md.py` 生成，对应 `DATASETS.md` 中的链接。

- **transport/**：NaPTAN/NPTG 样本或整表（视体积与服务器响应而定）；ORR 多为**网页存档**，Excel 需浏览器手动下载。
- **heritage/**：世界遗产/英格兰遗产相关**网页存档**；NHLE 矢量全量通常在 ArcGIS Hub 分文件下载。
- **dark_skies/**：IDA / gov.uk **网页存档**。
- **portals/**：检索入口与专题站**网页存档**。
- **meta/**：CKAN API JSON、清单。

若某项标记 `[FAIL]`，常见原因为超时、403、TLS、或目标禁止脚本访问——请用浏览器按 `DATASETS.md` 原链接手动下载。

---

## 补充（curl 与手工补救）

- `meta/ckan_package_show_naptan.json`：已通过 curl 成功保存（含 NaPTAN CSV/XML 官方 API URL）。
- `heritage/whc_unesco_gb.html`：curl 可保存文件，但站点使用 Cloudflare，**内容可能为挑战页**，不等于可解析的遗产列表 HTML；请用浏览器访问原链接。
- `dark_skies/govuk_natural_england.html`：`data/DATASETS.md` 中国立公园集合 URL 曾 404，已改用 **Natural England** 机构页作为 gov.uk 政策引用入口。
- `transport/orr_home.html`：ORR 首页（站内再进入 Rail usage / Station usage 下载 xlsx）。
- 已删除重复的 `naptan_access_nodes_sample500k.csv`（与 2MB 头文件用途重复且体积大）。

详见 **`README.md`** 文件清单。

---

# 下载日志（UTC 2026-04-08T07:28:17Z）

- [FAIL] CKAN package_search NaPTAN
  URL: https://data.gov.uk/api/3/action/package_search?q=naptan&rows=5
  Error: URLError(SSLEOFError(8, '[SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1006)'))

- [FAIL] CKAN package_show naptan
  URL: https://data.gov.uk/api/3/action/package_show?id=naptan
  Error: URLError(SSLEOFError(8, '[SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1006)'))

- [OK] NaPTAN access-nodes CSV (first ~2MB sample)
  -> naptan_access_nodes_HEAD_2mb.csv (ok 2097152 bytes)
  URL: https://naptan.api.dft.gov.uk/v1/access-nodes?dataFormat=csv

- [OK] NPTG localities (full if server allows)
  -> nptg_localities.csv (ok 4854446 bytes)
  URL: https://naptan.api.dft.gov.uk/v1/nptg/localities

- [FAIL] UNESCO UK parties
  URL: https://whc.unesco.org/en/statesparties/gb
  Error: URLError(SSLEOFError(8, '[SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1006)'))

- [FAIL] Historic England data downloads
  URL: https://historicengland.org.uk/listing/the-list/data-downloads/
  Error: <HTTPError 403: 'Forbidden'>

- [OK] HE Open Data Hub
  -> historic_england_open_data_hub.html (ok 70150 bytes)
  URL: https://opendata-historicengland.hub.arcgis.com/

- [FAIL] UK national parks collection
  URL: https://www.gov.uk/government/collections/national-parks
  Error: <HTTPError 404: 'Not Found'>

- [FAIL] IDA Dark Sky Finder
  URL: https://www.darksky.org/our-work/conservation/idsp/finder/
  Error: <HTTPError 403: 'Forbidden'>

- [FAIL] ORR station usage estimates page
  URL: https://www.orr.gov.uk/published-statistics/rail-usage/station-usage-estimates
  Error: <HTTPError 404: 'Not Found'>

- [FAIL] ORR dataportal root
  URL: https://dataportal.orr.gov.uk/
  Error: URLError(SSLEOFError(8, '[SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1006)'))

- [OK] data.gov.uk naptan search
  -> data_gov_uk_search_naptan.html (ok 20693 bytes)
  URL: https://www.data.gov.uk/search?q=naptan

- [FAIL] VisitBritain home
  URL: https://www.visitbritain.com/gb/en
  Error: URLError(SSLEOFError(8, '[SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1006)'))

- [FAIL] Screen Scotland
  URL: https://www.screen.scot/
  Error: URLError(SSLEOFError(8, '[SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1006)'))

- [OK] Kaggle datasets
  -> kaggle_datasets.html (ok 5685 bytes)
  URL: https://www.kaggle.com/datasets

- [OK] Google Dataset Search
  -> google_dataset_search.html (ok 508611 bytes)
  URL: https://datasetsearch.research.google.com/

- [FAIL] UCI repository
  URL: https://archive.ics.uci.edu/
  Error: URLError(SSLEOFError(8, '[SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1006)'))
