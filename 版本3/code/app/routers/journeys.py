from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud import journey as journey_crud
from app.deps import require_api_key
from app.database import get_db
from app.pagination import DEFAULT_PAGE_SIZE, LimitQuery, SkipQuery
from app.models import Journey, StopType
from app.schemas import (
    JourneyAnalytics,
    JourneyCreate,
    JourneyListItem,
    JourneyRead,
    JourneySummary,
    JourneyUpdate,
)
from app.services import analytics

router = APIRouter(prefix="/journeys", tags=["journeys"])


def _summary_from_journey(j: Journey) -> JourneySummary:
    stops = list(j.stops)
    lit = sum(
        1
        for s in stops
        if s.literary_location_id is not None or s.stop_type == StopType.story_poi
    )
    ds = sum(1 for s in stops if s.stop_type == StopType.dark_sky)
    transit = sum(1 for s in stops if s.stop_type == StopType.transit)
    dist = sum(s.distance_km or 0.0 for s in stops)
    total_dist = dist if dist > 0 else None
    return JourneySummary(
        journey_id=j.id,
        title=j.title,
        stop_count=len(stops),
        literary_stop_count=lit,
        dark_sky_stop_count=ds,
        transit_leg_count=transit,
        total_distance_km=round(total_dist, 3) if total_dist is not None else None,
    )


@router.post(
    "",
    response_model=JourneyRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_api_key)],
)
def create_journey(payload: JourneyCreate, db: Session = Depends(get_db)) -> Journey:
    return journey_crud.create_journey(db, payload)


@router.get("", response_model=list[JourneyListItem])
def list_journeys(
    skip: SkipQuery = 0,
    limit: LimitQuery = DEFAULT_PAGE_SIZE,
    db: Session = Depends(get_db),
) -> list[JourneyListItem]:
    rows = journey_crud.list_journeys(db, skip=skip, limit=limit)
    out: list[JourneyListItem] = []
    for j in rows:
        out.append(
            JourneyListItem(
                id=j.id,
                title=j.title,
                start_date=j.start_date,
                end_date=j.end_date,
                created_at=j.created_at,
                updated_at=j.updated_at,
                stop_count=len(j.stops),
            )
        )
    return out


@router.get("/{journey_id}", response_model=JourneyRead)
def get_journey(journey_id: int, db: Session = Depends(get_db)) -> Journey:
    j = journey_crud.get_journey(db, journey_id)
    if j is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "not_found", "message": "Journey not found"}},
        )
    return j


@router.patch(
    "/{journey_id}",
    response_model=JourneyRead,
    dependencies=[Depends(require_api_key)],
)
def patch_journey(journey_id: int, payload: JourneyUpdate, db: Session = Depends(get_db)) -> Journey:
    j = journey_crud.update_journey(db, journey_id, payload)
    if j is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "not_found", "message": "Journey not found"}},
        )
    return j


@router.delete(
    "/{journey_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_api_key)],
)
def delete_journey(journey_id: int, db: Session = Depends(get_db)) -> None:
    if not journey_crud.delete_journey(db, journey_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "not_found", "message": "Journey not found"}},
        )


@router.get("/{journey_id}/summary", response_model=JourneySummary)
def journey_summary(journey_id: int, db: Session = Depends(get_db)) -> JourneySummary:
    j = journey_crud.get_journey(db, journey_id)
    if j is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "not_found", "message": "Journey not found"}},
        )
    return _summary_from_journey(j)


@router.get("/{journey_id}/analytics", response_model=JourneyAnalytics)
def journey_analytics(journey_id: int, db: Session = Depends(get_db)) -> JourneyAnalytics:
    j = analytics.journey_with_stops_loaded(db, journey_id)
    if j is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "not_found", "message": "Journey not found"}},
        )
    data = analytics.build_journey_analytics(db, j)
    return JourneyAnalytics.model_validate(data)
