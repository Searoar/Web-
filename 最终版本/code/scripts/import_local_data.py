"""
将仓库根目录 data/ 下的示例 CSV 导入 SQLite，与 LiteraryLocation / DarkSkySite 表对齐。

用法（在 code 目录下）:
  python -m scripts.import_local_data
  python -m scripts.import_local_data --data-root ..\\..\\data

说明：NaPTAN / ORR 类 CSV 与当前数据库表结构不直接对应，见 README「data 目录」。
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

# 保证以「python -m scripts.import_local_data」运行时能 import app
_CODE_ROOT = Path(__file__).resolve().parents[1]
if str(_CODE_ROOT) not in sys.path:
    sys.path.insert(0, str(_CODE_ROOT))

from sqlalchemy import select

from app.database import Base, SessionLocal, engine
from app.models import DarkSkySite, LiteraryLocation
from app.seed import seed_reference_data


def _tier_from_notes(s: str) -> int:
    m = re.search(r"\d", s or "")
    if m:
        n = int(m.group())
        return max(1, min(5, n))
    return 3


def import_film_literary(db, path: Path) -> tuple[int, int, int]:
    """返回 (新增条数, 跳过条数, CSV 有效行数)。"""
    if not path.is_file():
        return 0, 0, 0
    n_new = 0
    n_skip = 0
    n_seen = 0
    with path.open(encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            title = (row.get("LocationName") or "").strip()
            work = (row.get("WorkOrFranchise") or "").strip()
            if not title or not work:
                continue
            n_seen += 1
            lat = float(row["Latitude"])
            lon = float(row["Longitude"])
            region = (row.get("Region") or "").strip() or None
            desc = (row.get("SourceNote") or "").strip() or None
            exists = db.scalars(
                select(LiteraryLocation).where(
                    LiteraryLocation.title == title,
                    LiteraryLocation.latitude == lat,
                )
            ).first()
            if exists:
                n_skip += 1
                continue
            db.add(
                LiteraryLocation(
                    title=title,
                    work_title=work,
                    creator=None,
                    latitude=lat,
                    longitude=lon,
                    region=region,
                    description=desc,
                )
            )
            n_new += 1
    return n_new, n_skip, n_seen


def import_heritage(db, path: Path) -> tuple[int, int, int]:
    if not path.is_file():
        return 0, 0, 0
    n_new = 0
    n_skip = 0
    n_seen = 0
    with path.open(encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            name = (row.get("Name") or "").strip()
            cat = (row.get("Category") or "").strip()
            if not name:
                continue
            n_seen += 1
            lat = float(row["Latitude"])
            lon = float(row["Longitude"])
            desc = (row.get("SourceNote") or "").strip() or None
            work_title = cat if cat else "Heritage"
            exists = db.scalars(
                select(LiteraryLocation).where(
                    LiteraryLocation.title == name,
                    LiteraryLocation.latitude == lat,
                )
            ).first()
            if exists:
                n_skip += 1
                continue
            db.add(
                LiteraryLocation(
                    title=name,
                    work_title=work_title,
                    creator=None,
                    latitude=lat,
                    longitude=lon,
                    region=(row.get("Country") or "").strip() or None,
                    description=desc,
                )
            )
            n_new += 1
    return n_new, n_skip, n_seen


def import_dark_skies(db, path: Path) -> tuple[int, int, int]:
    if not path.is_file():
        return 0, 0, 0
    n_new = 0
    n_skip = 0
    n_seen = 0
    with path.open(encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            name = (row.get("Name") or "").strip()
            if not name:
                continue
            n_seen += 1
            lat = float(row["Latitude"])
            lon = float(row["Longitude"])
            tier = _tier_from_notes((row.get("DarknessTierNotes") or "").strip())
            notes = (row.get("SourceNote") or "").strip() or None
            exists = db.scalars(
                select(DarkSkySite).where(
                    DarkSkySite.name == name,
                    DarkSkySite.latitude == lat,
                )
            ).first()
            if exists:
                n_skip += 1
                continue
            db.add(
                DarkSkySite(
                    name=name,
                    latitude=lat,
                    longitude=lon,
                    darkness_tier=tier,
                    notes=notes,
                )
            )
            n_new += 1
    return n_new, n_skip, n_seen


def main() -> None:
    p = argparse.ArgumentParser(description="从 data/ CSV 导入参考数据到 SQLite")
    p.add_argument(
        "--data-root",
        type=Path,
        default=_CODE_ROOT.parent / "data",
        help="data 目录路径（默认：仓库根目录下的 data）",
    )
    args = p.parse_args()
    root: Path = args.data_root.resolve()

    film_paths = [
        root / "film_literary" / "filming_locations_uk_sample.csv",
        root / "film_literary" / "filming_locations_uk_expanded.csv",
    ]
    heritage = root / "heritage" / "nhle_world_heritage_sites_uk_sample.csv"
    sky_paths = [
        root / "dark_skies" / "uk_dark_sky_places_sample.csv",
        root / "dark_skies" / "uk_dark_sky_places_expanded.csv",
        root / "dark_skies" / "national_parks_england_ogl_centroids.csv",
    ]

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_reference_data(db)
        af = sf = tf = 0
        for film in film_paths:
            a, s, t = import_film_literary(db, film)
            af += a
            sf += s
            tf += t
        bh, sh, th = import_heritage(db, heritage)
        ck = sk = tk = 0
        for skies in sky_paths:
            c, s, t = import_dark_skies(db, skies)
            ck += c
            sk += s
            tk += t
        db.commit()
        print("导入结果（新增 / 跳过=与库中已有重复 / CSV 有效行）：")
        print(f"  film_literary : +{af} 新增, 跳过 {sf} 条, CSV 共 {tf} 行（含 sample + expanded）")
        print(f"  heritage      : +{bh} 新增, 跳过 {sh} 条, CSV 共 {th} 行")
        print(f"  dark_skies    : +{ck} 新增, 跳过 {sk} 条, CSV 共 {tk} 行（含 sample + expanded）")
        if af == 0 and bh == 0 and ck == 0:
            print(
                "提示：三项均为 0 条新增时，通常表示这些数据已在库里（含内置 seed 或上次已导入），"
                "无需重复导入。若要强制从零重建，可删除 code 目录下的 slowtravel.db 后再运行本脚本。"
            )
        print(f"data 根目录：{root}")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
