"""
从 data/downloads/transport 下的 NaPTAN / NPTG CSV 批量导入 SQLite（naptan_access_nodes、nptg_localities）。

用法（在 code 目录）:
  python -m scripts.etl_naptan_nptg
  python -m scripts.etl_naptan_nptg --naptan-csv "..\\..\\data\\downloads\\transport\\naptan_access_nodes_HEAD_2mb.csv"

依赖：已执行 alembic upgrade 或应用已至少创建过表。
"""

from __future__ import annotations

import argparse
import csv
import sys
from functools import lru_cache
from pathlib import Path

from pyproj import Transformer

_CODE_ROOT = Path(__file__).resolve().parents[1]
if str(_CODE_ROOT) not in sys.path:
    sys.path.insert(0, str(_CODE_ROOT))

from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import Session

from app.database import SessionLocal, engine
from app.models import NaptanAccessNode, NptgLocality


def _default_paths() -> tuple[Path, Path]:
    root = _CODE_ROOT.parent / "data" / "downloads" / "transport"
    return (
        root / "naptan_access_nodes_HEAD_2mb.csv",
        root / "nptg_localities.csv",
    )


def _parse_float_cell(value: object) -> float | None:
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


@lru_cache(maxsize=1)
def _osgb_to_wgs84() -> Transformer:
    """英国国家网格 BNG (EPSG:27700) → WGS84。NaPTAN 中大量行仅有 Easting/Northing。"""
    return Transformer.from_crs("EPSG:27700", "EPSG:4326", always_xy=True)


def lat_lon_from_naptan_row(row: dict) -> tuple[float, float] | None:
    """
    优先使用 CSV 中的 Latitude/Longitude；若为空则用 Easting/Northing（UKOS 或空 GridType，按 OSGB 处理）。
    """
    lat = _parse_float_cell(row.get("Latitude"))
    lon = _parse_float_cell(row.get("Longitude"))
    if lat is not None and lon is not None:
        return lat, lon

    e = _parse_float_cell(row.get("Easting"))
    n = _parse_float_cell(row.get("Northing"))
    if e is None or n is None:
        return None

    grid = (row.get("GridType") or "").strip()
    if grid not in ("", "UKOS"):
        return None

    lon_o, lat_o = _osgb_to_wgs84().transform(e, n)
    return lat_o, lon_o


def import_naptan(db: Session, path: Path, batch: int = 800) -> tuple[int, int, int]:
    if not path.is_file():
        print(f"跳过 NaPTAN：文件不存在 {path}")
        return 0, 0, 0
    inserted = 0
    skipped = 0
    from_grid = 0
    buf: list[dict] = []
    with path.open(encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            atco = (row.get("ATCOCode") or "").strip()
            if not atco:
                continue
            coords = lat_lon_from_naptan_row(row)
            if coords is None:
                skipped += 1
                continue
            lat, lon = coords
            if not (
                _parse_float_cell(row.get("Latitude")) is not None
                and _parse_float_cell(row.get("Longitude")) is not None
            ):
                from_grid += 1
            buf.append(
                {
                    "atco_code": atco[:32],
                    "naptan_code": (row.get("NaptanCode") or None) and (row.get("NaptanCode") or "")[:64],
                    "common_name": ((row.get("CommonName") or "") or atco)[:512],
                    "latitude": lat,
                    "longitude": lon,
                    "stop_type": (row.get("StopType") or None) and (row.get("StopType") or "")[:16],
                    "locality_name": (row.get("LocalityName") or None) and (row.get("LocalityName") or "")[:255],
                    "nptg_locality_code": (row.get("NptgLocalityCode") or None)
                    and (row.get("NptgLocalityCode") or "")[:32],
                    "administrative_area_code": (row.get("AdministrativeAreaCode") or None)
                    and (row.get("AdministrativeAreaCode") or "")[:16],
                    "status": (row.get("Status") or None) and (row.get("Status") or "")[:32],
                }
            )
            if len(buf) >= batch:
                inserted += _upsert_naptan_batch(db, buf)
                buf.clear()
        if buf:
            inserted += _upsert_naptan_batch(db, buf)
    return inserted, skipped, from_grid


def _upsert_naptan_batch(db: Session, rows: list[dict]) -> int:
    if not rows:
        return 0
    n = 0
    for row in rows:
        stmt = sqlite_insert(NaptanAccessNode).values(**row)
        stmt = stmt.on_conflict_do_nothing(index_elements=["atco_code"])
        db.execute(stmt)
        n += 1
    db.commit()
    return len(rows)


def import_nptg(db: Session, path: Path, batch: int = 1000) -> tuple[int, int]:
    if not path.is_file():
        print(f"跳过 NPTG：文件不存在 {path}")
        return 0, 0
    inserted = 0
    skipped = 0
    buf: list[dict] = []
    with path.open(encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            code = (row.get("NptgLocalityCode") or "").strip()
            name = (row.get("LocalityName") or "").strip()
            if not code or not name:
                skipped += 1
                continue
            def ffloat(x: str | None) -> float | None:
                if x is None or x == "":
                    return None
                try:
                    return float(x)
                except ValueError:
                    return None

            buf.append(
                {
                    "nptg_locality_code": code[:32],
                    "locality_name": name[:255],
                    "parent_locality_name": (row.get("ParentLocalityName") or None)
                    and (row.get("ParentLocalityName") or "")[:255],
                    "administrative_area_code": (row.get("AdministrativeAreaCode") or None)
                    and (row.get("AdministrativeAreaCode") or "")[:16],
                    "source_locality_type": (row.get("SourceLocalityType") or None)
                    and (row.get("SourceLocalityType") or "")[:64],
                    "grid_type": (row.get("GridType") or None) and (row.get("GridType") or "")[:16],
                    "easting": ffloat(row.get("Easting")),
                    "northing": ffloat(row.get("Northing")),
                }
            )
            if len(buf) >= batch:
                inserted += _upsert_nptg_batch(db, buf)
                buf.clear()
        if buf:
            inserted += _upsert_nptg_batch(db, buf)
    return inserted, skipped


def _upsert_nptg_batch(db: Session, rows: list[dict]) -> int:
    if not rows:
        return 0
    for row in rows:
        stmt = sqlite_insert(NptgLocality).values(**row)
        stmt = stmt.on_conflict_do_nothing(index_elements=["nptg_locality_code"])
        db.execute(stmt)
    db.commit()
    return len(rows)


def main() -> None:
    p = argparse.ArgumentParser(description="ETL NaPTAN / NPTG CSV into SQLite")
    n_def, g_def = _default_paths()
    p.add_argument("--naptan-csv", type=Path, default=n_def)
    p.add_argument("--nptg-csv", type=Path, default=g_def)
    args = p.parse_args()

    db = SessionLocal()
    try:
        # 确保表存在（未跑 alembic 时）
        from app.database import Base

        Base.metadata.create_all(bind=engine)

        ni, ns, n_grid = import_naptan(db, args.naptan_csv.resolve())
        gi, gs = import_nptg(db, args.nptg_csv.resolve())
        print(f"NaPTAN：累计 upsert {ni} 行（仍跳过 {ns}；由 Easting/Northing 换算经纬 {n_grid}）")
        print(f"NPTG：处理行约 {gi}（跳过 {gs}）")
        print("完成。可用 GET /reference/naptan-access-nodes 与 /reference/nptg-localities 查看。")
    finally:
        db.close()


if __name__ == "__main__":
    main()
