from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import NaptanAccessNode, NptgLocality
from app.pagination import DEFAULT_PAGE_SIZE, LimitQuery, SkipQuery
from app.schemas import NaptanAccessNodeRead, NptgLocalityRead

router = APIRouter(prefix="/reference", tags=["reference-transport"])


@router.get("/naptan-access-nodes", response_model=list[NaptanAccessNodeRead])
def list_naptan_nodes(
    skip: SkipQuery = 0,
    limit: LimitQuery = DEFAULT_PAGE_SIZE,
    db: Session = Depends(get_db),
    q: str | None = Query(None, description="按 CommonName / atco_code 子串筛选"),
    stop_type: str | None = Query(None, description="NaPTAN StopType，如 BCT、RLY"),
) -> list[NaptanAccessNode]:
    stmt = select(NaptanAccessNode).order_by(NaptanAccessNode.id)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(
            (NaptanAccessNode.common_name.ilike(like)) | (NaptanAccessNode.atco_code.ilike(like))
        )
    if stop_type:
        stmt = stmt.where(NaptanAccessNode.stop_type == stop_type)
    stmt = stmt.offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


@router.get("/nptg-localities", response_model=list[NptgLocalityRead])
def list_nptg_localities(
    skip: SkipQuery = 0,
    limit: LimitQuery = DEFAULT_PAGE_SIZE,
    db: Session = Depends(get_db),
    q: str | None = Query(None, description="按地名子串筛选"),
) -> list[NptgLocality]:
    stmt = select(NptgLocality).order_by(NptgLocality.locality_name)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(NptgLocality.locality_name.ilike(like))
    stmt = stmt.offset(skip).limit(limit)
    return list(db.scalars(stmt).all())
