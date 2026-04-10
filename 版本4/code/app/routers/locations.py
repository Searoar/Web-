from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import DarkSkySite, LiteraryLocation
from app.pagination import DEFAULT_PAGE_SIZE, LimitQuery, SkipQuery
from app.schemas import DarkSkySiteRead, LiteraryLocationRead

router = APIRouter(prefix="/reference", tags=["reference"])


@router.get("/literary-locations", response_model=list[LiteraryLocationRead])
def list_literary_locations(
    skip: SkipQuery = 0,
    limit: LimitQuery = DEFAULT_PAGE_SIZE,
    db: Session = Depends(get_db),
    region: str | None = Query(None, description="按地区模糊筛选"),
    work_title: str | None = Query(None, description="按作品名模糊筛选"),
) -> list[LiteraryLocation]:
    stmt = select(LiteraryLocation).order_by(LiteraryLocation.id)
    if region:
        stmt = stmt.where(LiteraryLocation.region.contains(region))
    if work_title:
        stmt = stmt.where(LiteraryLocation.work_title.contains(work_title))
    stmt = stmt.offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


@router.get("/dark-sky-sites", response_model=list[DarkSkySiteRead])
def list_dark_sky_sites(
    skip: SkipQuery = 0,
    limit: LimitQuery = DEFAULT_PAGE_SIZE,
    db: Session = Depends(get_db),
    max_tier: int | None = Query(None, ge=1, le=5, description="最暗为 1，筛选 tier ≤ 该值"),
) -> list[DarkSkySite]:
    stmt = select(DarkSkySite).order_by(DarkSkySite.darkness_tier, DarkSkySite.id)
    if max_tier is not None:
        stmt = stmt.where(DarkSkySite.darkness_tier <= max_tier)
    stmt = stmt.offset(skip).limit(limit)
    return list(db.scalars(stmt).all())
