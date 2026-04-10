from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Journey, JourneyStop, StopType, TransportMode
from app.schemas import JourneyCreate, JourneyStopCreate, JourneyUpdate


def _stops_from_schema(journey_id: int, items: list[JourneyStopCreate]) -> list[JourneyStop]:
    ordered = sorted(items, key=lambda s: s.sequence_order)
    out: list[JourneyStop] = []
    for s in ordered:
        out.append(
            JourneyStop(
                journey_id=journey_id,
                sequence_order=s.sequence_order,
                stop_type=StopType(s.stop_type.value),
                literary_location_id=s.literary_location_id,
                dark_sky_site_id=s.dark_sky_site_id,
                label=s.label,
                transport_mode=TransportMode(s.transport_mode.value) if s.transport_mode else None,
                distance_km=s.distance_km,
            )
        )
    return out


def _journey_load_options():
    return (
        selectinload(Journey.stops).selectinload(JourneyStop.literary_location),
        selectinload(Journey.stops).selectinload(JourneyStop.dark_sky_site),
    )


def create_journey(db: Session, data: JourneyCreate) -> Journey:
    j = Journey(
        title=data.title,
        start_date=data.start_date,
        end_date=data.end_date,
        notes=data.notes,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(j)
    db.flush()
    for stop in _stops_from_schema(j.id, data.stops):
        db.add(stop)
    db.commit()
    return get_journey(db, j.id)  # type: ignore[return-value]


def get_journey(db: Session, journey_id: int) -> Journey | None:
    stmt = (
        select(Journey)
        .options(*_journey_load_options())
        .where(Journey.id == journey_id)
    )
    return db.execute(stmt).scalar_one_or_none()


def list_journeys(db: Session, skip: int = 0, limit: int = 100) -> list[Journey]:
    stmt = (
        select(Journey)
        .options(selectinload(Journey.stops))
        .order_by(Journey.id.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(db.execute(stmt).scalars().all())


def update_journey(db: Session, journey_id: int, data: JourneyUpdate) -> Journey | None:
    j = get_journey(db, journey_id)
    if j is None:
        return None
    if data.title is not None:
        j.title = data.title
    if data.start_date is not None:
        j.start_date = data.start_date
    if data.end_date is not None:
        j.end_date = data.end_date
    if data.notes is not None:
        j.notes = data.notes
    j.updated_at = datetime.utcnow()
    if data.stops is not None:
        j.stops.clear()
        db.flush()
        for stop in _stops_from_schema(j.id, data.stops):
            db.add(stop)
    db.commit()
    return get_journey(db, journey_id)


def delete_journey(db: Session, journey_id: int) -> bool:
    j = db.get(Journey, journey_id)
    if j is None:
        return False
    db.delete(j)
    db.commit()
    return True
