from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class StopTypeSchema(str, Enum):
    transit = "transit"
    story_poi = "story_poi"
    dark_sky = "dark_sky"


class TransportModeSchema(str, Enum):
    walk = "walk"
    bicycle = "bicycle"
    bus = "bus"
    train = "train"
    car = "car"
    flight = "flight"


class LiteraryLocationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    work_title: str
    creator: str | None
    latitude: float
    longitude: float
    region: str | None
    description: str | None


class DarkSkySiteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    latitude: float
    longitude: float
    darkness_tier: int
    notes: str | None


class JourneyStopCreate(BaseModel):
    sequence_order: int = Field(ge=0)
    stop_type: StopTypeSchema
    literary_location_id: int | None = None
    dark_sky_site_id: int | None = None
    label: str | None = Field(None, max_length=255)
    transport_mode: TransportModeSchema | None = None
    distance_km: float | None = Field(None, ge=0)


class JourneyStopRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sequence_order: int
    stop_type: StopTypeSchema
    literary_location_id: int | None
    dark_sky_site_id: int | None
    label: str | None
    transport_mode: TransportModeSchema | None
    distance_km: float | None


class JourneyStopReadExpanded(JourneyStopRead):
    literary_location: LiteraryLocationRead | None = None
    dark_sky_site: DarkSkySiteRead | None = None


class JourneyCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    start_date: date | None = None
    end_date: date | None = None
    notes: str | None = None
    stops: list[JourneyStopCreate] = Field(default_factory=list)


class JourneyUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    start_date: date | None = None
    end_date: date | None = None
    notes: str | None = None
    stops: list[JourneyStopCreate] | None = None


class JourneyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    start_date: date | None
    end_date: date | None
    notes: str | None
    created_at: datetime
    updated_at: datetime
    stops: list[JourneyStopReadExpanded]


class JourneyListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    start_date: date | None
    end_date: date | None
    created_at: datetime
    updated_at: datetime
    stop_count: int


class JourneySummary(BaseModel):
    journey_id: int
    title: str
    stop_count: int
    literary_stop_count: int
    dark_sky_stop_count: int
    transit_leg_count: int
    total_distance_km: float | None


class CarbonFootprintEstimate(BaseModel):
    total_kg_co2e: float
    per_mode_kg_co2e: dict[str, float]
    assumptions: str


class NarrativeCoherence(BaseModel):
    score_0_to_100: float
    story_poi_ratio: float
    dominant_work: str | None
    notes: str


class StargazingSuitability(BaseModel):
    score_0_to_100: float
    dark_sky_stops: int
    avg_darkness_tier: float | None
    notes: str


class JourneyAnalytics(BaseModel):
    carbon: CarbonFootprintEstimate
    narrative: NarrativeCoherence
    stargazing: StargazingSuitability
