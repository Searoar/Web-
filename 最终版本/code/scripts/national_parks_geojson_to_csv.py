"""
将 Natural England「National Parks (England)」GeoJSON 转为 dark_sky_sites 可导入的 CSV。

官方数据常为 EPSG:27700（英国国家网格）；质心经 pyproj 转为 WGS84。

用法（在 code 目录）:
  python -m scripts.national_parks_geojson_to_csv \\
    --geojson "..\\..\\手动下载全量\\National_Parks_England.geojson\\National_Parks_England.geojson" \\
    --out "..\\..\\data\\dark_skies\\national_parks_england_ogl_centroids.csv"
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

from pyproj import Transformer
from shapely.geometry import shape

_CODE_ROOT = Path(__file__).resolve().parents[1]
if str(_CODE_ROOT) not in sys.path:
    sys.path.insert(0, str(_CODE_ROOT))


def main() -> None:
    p = argparse.ArgumentParser(description="National Parks GeoJSON → dark_skies CSV")
    p.add_argument("--geojson", type=Path, required=True, help="National_Parks_England.geojson 路径")
    p.add_argument(
        "--out",
        type=Path,
        default=_CODE_ROOT.parent / "data" / "dark_skies" / "national_parks_england_ogl_centroids.csv",
        help="输出 CSV（默认 data/dark_skies/national_parks_england_ogl_centroids.csv）",
    )
    args = p.parse_args()

    src = args.geojson.resolve()
    if not src.is_file():
        raise SystemExit(f"找不到文件: {src}")

    to_wgs84 = Transformer.from_crs("EPSG:27700", "EPSG:4326", always_xy=True)

    data = json.loads(src.read_text(encoding="utf-8"))
    features = data.get("features") or []
    rows: list[dict[str, str]] = []

    for feat in features:
        geom = feat.get("geometry")
        props = feat.get("properties") or {}
        if not geom:
            continue
        g = shape(geom)
        c = g.centroid
        lon, lat = to_wgs84.transform(c.x, c.y)
        name = (props.get("name") or "Unnamed").strip()
        code = props.get("code")
        status = (props.get("status") or "").strip()
        note = (
            f"Natural England National Parks (England) OGL; "
            f"polygon centroid EPSG:27700→WGS84; code={code}; status={status}"
        )
        rows.append(
            {
                "Name": f"{name} National Park (England OGL centroid)",
                "Latitude": f"{lat:.6f}",
                "Longitude": f"{lon:.6f}",
                "DarknessTierNotes": "3 (国家公园开敞地—非 IDA 分级)",
                "SourceNote": note,
            }
        )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["Name", "Latitude", "Longitude", "DarknessTierNotes", "SourceNote"],
        )
        w.writeheader()
        w.writerows(rows)

    print(f"已写入 {len(rows)} 行 → {args.out.resolve()}")


if __name__ == "__main__":
    main()
