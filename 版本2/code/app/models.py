import enum
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    pass


class StopType(str, enum.Enum):
    transit = "transit"
    story_poi = "story_poi"
    dark_sky = "dark_sky"


class TransportMode(str, enum.Enum):
    walk = "walk"
    bicycle = "bicycle"
    bus = "bus"
    train = "train"
    car = "car"
    flight = "flight"


class LiteraryLocation(Base):
    __tablename__ = "literary_locations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    work_title: Mapped[str] = mapped_column(String(255), nullable=False)
    creator: Mapped[str | None] = mapped_column(String(255), nullable=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    region: Mapped[str | None] = mapped_column(String(128), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)


class DarkSkySite(Base):
    __tablename__ = "dark_sky_sites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    darkness_tier: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class NaptanAccessNode(Base):
    """NaPTAN 公交/铁路等访问点（来自 DfT CSV/API 导入）。"""

    __tablename__ = "naptan_access_nodes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    atco_code: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    naptan_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    common_name: Mapped[str] = mapped_column(String(512), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    stop_type: Mapped[str | None] = mapped_column(String(16), nullable=True)
    locality_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    nptg_locality_code: Mapped[str | None] = mapped_column(String(32), nullable=True)
    administrative_area_code: Mapped[str | None] = mapped_column(String(16), nullable=True)
    status: Mapped[str | None] = mapped_column(String(32), nullable=True)


class NptgLocality(Base):
    """NPTG 地名库（来自 DfT localities CSV 导入）。"""

    __tablename__ = "nptg_localities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nptg_locality_code: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    locality_name: Mapped[str] = mapped_column(String(255), nullable=False)
    parent_locality_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    administrative_area_code: Mapped[str | None] = mapped_column(String(16), nullable=True)
    source_locality_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    grid_type: Mapped[str | None] = mapped_column(String(16), nullable=True)
    easting: Mapped[float | None] = mapped_column(Float, nullable=True)
    northing: Mapped[float | None] = mapped_column(Float, nullable=True)


class Journey(Base):
    __tablename__ = "journeys"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    stops: Mapped[list["JourneyStop"]] = relationship(
        "JourneyStop",
        back_populates="journey",
        cascade="all, delete-orphan",
        order_by="JourneyStop.sequence_order",
    )


class JourneyStop(Base):
    __tablename__ = "journey_stops"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    journey_id: Mapped[int] = mapped_column(ForeignKey("journeys.id", ondelete="CASCADE"), nullable=False)
    sequence_order: Mapped[int] = mapped_column(Integer, nullable=False)
    stop_type: Mapped[StopType] = mapped_column(Enum(StopType), nullable=False)
    literary_location_id: Mapped[int | None] = mapped_column(
        ForeignKey("literary_locations.id"), nullable=True
    )
    dark_sky_site_id: Mapped[int | None] = mapped_column(ForeignKey("dark_sky_sites.id"), nullable=True)
    naptan_access_node_id: Mapped[int | None] = mapped_column(
        ForeignKey("naptan_access_nodes.id"), nullable=True
    )
    label: Mapped[str | None] = mapped_column(String(255), nullable=True)
    transport_mode: Mapped[TransportMode | None] = mapped_column(Enum(TransportMode), nullable=True)
    distance_km: Mapped[float | None] = mapped_column(Float, nullable=True)

    journey: Mapped["Journey"] = relationship("Journey", back_populates="stops")
    literary_location: Mapped["LiteraryLocation | None"] = relationship("LiteraryLocation")
    dark_sky_site: Mapped["DarkSkySite | None"] = relationship("DarkSkySite")
    naptan_access_node: Mapped["NaptanAccessNode | None"] = relationship("NaptanAccessNode")
