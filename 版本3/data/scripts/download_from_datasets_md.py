"""
根据 data/DATASETS.md 中的公开链接，尽可能自动下载数据或页面存档。

说明：
- NaPTAN 全国 CSV 体积极大，默认仅下载「前 N 字节」作为本地样本；要全量请用文档中的 API URL 自行流式下载。
- ORR、ArcGIS 等常为 403/需登录，失败会记入 DOWNLOAD_LOG.md。
"""

from __future__ import annotations

import json
import ssl
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # data/
OUT = ROOT / "downloads"
UA = "Mozilla/5.0 (compatible; coursework-bot/1.0; +local research)"


def fetch_bytes(url: str, max_bytes: int | None = None) -> tuple[bytes, str | None]:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, timeout=180, context=ctx) as resp:
        err = getattr(resp, "status", None)
        if max_bytes is None:
            return resp.read(), None
        return resp.read(max_bytes), None


def fetch_to_file(url: str, dest: Path, max_bytes: int | None = None) -> str:
    dest.parent.mkdir(parents=True, exist_ok=True)
    data, _ = fetch_bytes(url, max_bytes=max_bytes)
    dest.write_bytes(data)
    return f"ok {len(data)} bytes"


def fetch_html(url: str, dest: Path) -> str:
    return fetch_to_file(url, dest, max_bytes=None)


def main() -> None:
    log_lines: list[str] = []
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def log(msg: str) -> None:
        log_lines.append(msg)
        print(msg)

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "transport").mkdir(exist_ok=True)
    (OUT / "heritage").mkdir(exist_ok=True)
    (OUT / "dark_skies").mkdir(exist_ok=True)
    (OUT / "portals").mkdir(exist_ok=True)
    (OUT / "meta").mkdir(exist_ok=True)

    jobs: list[tuple[str, Path, str]] = []

    # CKAN：NaPTAN / NPTG 元数据
    jobs.append(
        (
            "CKAN package_search NaPTAN",
            OUT / "meta" / "ckan_package_naptan.json",
            "https://data.gov.uk/api/3/action/package_search?q=naptan&rows=5",
        )
    )
    jobs.append(
        (
            "CKAN package_show naptan",
            OUT / "meta" / "ckan_package_show_naptan.json",
            "https://data.gov.uk/api/3/action/package_show?id=naptan",
        )
    )

    # NaPTAN：全国 CSV 仅截取前 2MB 作为「可放入仓库的样本」
    jobs.append(
        (
            "NaPTAN access-nodes CSV (first ~2MB sample)",
            OUT / "transport" / "naptan_access_nodes_HEAD_2mb.csv",
            "https://naptan.api.dft.gov.uk/v1/access-nodes?dataFormat=csv",
        )
    )

    # NPTG localities — 尝试完整拉取（若过大则仅保留脚本说明）
    jobs.append(
        (
            "NPTG localities (full if server allows)",
            OUT / "transport" / "nptg_localities.csv",
            "https://naptan.api.dft.gov.uk/v1/nptg/localities",
        )
    )

    # 网页存档（叙事/政策）
    html_pages = [
        ("UNESCO UK parties", OUT / "heritage" / "whc_unesco_gb.html", "https://whc.unesco.org/en/statesparties/gb"),
        ("Historic England data downloads", OUT / "heritage" / "historic_england_data_downloads.html", "https://historicengland.org.uk/listing/the-list/data-downloads/"),
        ("HE Open Data Hub", OUT / "heritage" / "historic_england_open_data_hub.html", "https://opendata-historicengland.hub.arcgis.com/"),
        ("UK national parks collection", OUT / "dark_skies" / "govuk_national_parks_collection.html", "https://www.gov.uk/government/collections/national-parks"),
        ("IDA Dark Sky Finder", OUT / "dark_skies" / "ida_dark_sky_finder.html", "https://www.darksky.org/our-work/conservation/idsp/finder/"),
        ("ORR station usage estimates page", OUT / "transport" / "orr_station_usage_page.html", "https://www.orr.gov.uk/published-statistics/rail-usage/station-usage-estimates"),
        ("ORR dataportal root", OUT / "transport" / "orr_dataportal.html", "https://dataportal.orr.gov.uk/"),
        ("data.gov.uk naptan search", OUT / "portals" / "data_gov_uk_search_naptan.html", "https://www.data.gov.uk/search?q=naptan"),
        ("VisitBritain home", OUT / "portals" / "visitbritain_home.html", "https://www.visitbritain.com/gb/en"),
        ("Screen Scotland", OUT / "portals" / "screen_scotland.html", "https://www.screen.scot/"),
        ("Kaggle datasets", OUT / "portals" / "kaggle_datasets.html", "https://www.kaggle.com/datasets"),
        ("Google Dataset Search", OUT / "portals" / "google_dataset_search.html", "https://datasetsearch.research.google.com/"),
        ("UCI repository", OUT / "portals" / "uci_repository.html", "https://archive.ics.uci.edu/"),
    ]

    log(f"# 下载日志（UTC {ts}）\n")

    for label, path, url in jobs:
        try:
            if path.name.startswith("naptan_access_nodes_HEAD"):
                msg = fetch_to_file(url, path, max_bytes=2 * 1024 * 1024)
            else:
                msg = fetch_to_file(url, path, max_bytes=None)
            log(f"- [OK] {label}\n  -> {path.name} ({msg})\n  URL: {url}\n")
        except Exception as e:
            log(f"- [FAIL] {label}\n  URL: {url}\n  Error: {e!r}\n")

    for label, path, url in html_pages:
        try:
            msg = fetch_html(url, path)
            log(f"- [OK] {label}\n  -> {path.name} ({msg})\n  URL: {url}\n")
        except Exception as e:
            log(f"- [FAIL] {label}\n  URL: {url}\n  Error: {e!r}\n")

    manifest = {
        "generated_at_utc": ts,
        "note": "NaPTAN full national CSV is very large; use API URL in meta JSON for bulk download.",
        "files": [str(OUT.relative_to(ROOT)) + "/**"],
    }
    (OUT / "meta" / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    log_path = OUT / "DOWNLOAD_LOG.md"
    header = """# 自动下载结果说明

本目录由 `data/scripts/download_from_datasets_md.py` 生成，对应 `DATASETS.md` 中的链接。

- **transport/**：NaPTAN/NPTG 样本或整表（视体积与服务器响应而定）；ORR 多为**网页存档**，Excel 需浏览器手动下载。
- **heritage/**：世界遗产/英格兰遗产相关**网页存档**；NHLE 矢量全量通常在 ArcGIS Hub 分文件下载。
- **dark_skies/**：IDA / gov.uk **网页存档**。
- **portals/**：检索入口与专题站**网页存档**。
- **meta/**：CKAN API JSON、清单。

若某项标记 `[FAIL]`，常见原因为超时、403、TLS、或目标禁止脚本访问——请用浏览器按 `DATASETS.md` 原链接手动下载。

"""
    log_path.write_text(header + "\n".join(log_lines), encoding="utf-8")
    print(f"\nWrote {log_path}")


if __name__ == "__main__":
    main()
