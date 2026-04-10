"""
粗算与启发式指标：碳足迹（gCO2e/km→kg）、叙事连贯度、观星适宜度。
系数为教学演示量级，可在报告中说明可替换为更权威数据源。
"""

from collections import Counter
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import DarkSkySite, Journey, JourneyStop, LiteraryLocation, StopType, TransportMode

# g CO2e per passenger-km（简化常量，文献区间因地区年份而异）
_G_PER_KM: dict[TransportMode, float] = {
    TransportMode.walk: 0.0,
    TransportMode.bicycle: 5.0,
    TransportMode.bus: 80.0,
    TransportMode.train: 45.0,
    TransportMode.car: 170.0,
    TransportMode.flight: 230.0,
}


def _kg_from_leg(mode: TransportMode | None, distance_km: float | None) -> float:
    if distance_km is None or distance_km <= 0:
        return 0.0
    m = mode or TransportMode.train
    g = _G_PER_KM.get(m, 50.0) * distance_km
    return g / 1000.0


def estimate_carbon_for_stops(stops: Sequence[JourneyStop]) -> tuple[float, dict[str, float]]:
    per_mode_kg: dict[str, float] = {}
    total = 0.0
    for s in stops:
        if s.distance_km is None or s.distance_km <= 0:
            continue
        mode = s.transport_mode or TransportMode.train
        kg = _kg_from_leg(mode, s.distance_km)
        key = mode.value
        per_mode_kg[key] = per_mode_kg.get(key, 0.0) + kg
        total += kg
    return total, per_mode_kg


def narrative_coherence(
    db: Session,
    stops: Sequence[JourneyStop],
) -> tuple[float, float, str | None, str]:
    n = len(stops)
    if n == 0:
        return 0.0, 0.0, None, "无经停点。"

    story_count = sum(1 for s in stops if s.stop_type == StopType.story_poi)
    ratio = story_count / n

    work_titles: list[str] = []
    for s in stops:
        if s.literary_location_id and s.literary_location:
            work_titles.append(s.literary_location.work_title)
        elif s.literary_location_id:
            loc = db.get(LiteraryLocation, s.literary_location_id)
            if loc:
                work_titles.append(loc.work_title)

    dominant: str | None = None
    if work_titles:
        dominant = Counter(work_titles).most_common(1)[0][0]

    # 启发式：故事点占比 60 分；若存在主导作品再加最多 40 分
    score = min(100.0, ratio * 60.0 + (40.0 if dominant and work_titles.count(dominant) >= 2 else 0.0))
    notes = "基于故事类经停占比与同一作品重复出现次数的简化评分。"
    return score, ratio, dominant, notes


def stargazing_suitability(
    db: Session,
    stops: Sequence[JourneyStop],
) -> tuple[float, int, float | None, str]:
    tiers: list[int] = []
    ds_count = 0
    for s in stops:
        if s.stop_type != StopType.dark_sky:
            continue
        ds_count += 1
        if s.dark_sky_site_id:
            site = s.dark_sky_site or db.get(DarkSkySite, s.dark_sky_site_id)
            if site:
                tiers.append(site.darkness_tier)

    if ds_count == 0:
        return 0.0, 0, None, "未安排暗夜观星经停。"

    avg_tier = sum(tiers) / len(tiers) if tiers else 3.0
    # tier 1–5，越暗分越高：映射到 0–100
    score = min(100.0, max(0.0, (6 - avg_tier) / 5.0 * 100.0))
    notes = "依据 dark_sky 经停数量与关联站点的 darkness_tier（1 最暗）。"
    return score, ds_count, avg_tier, notes


def build_journey_analytics(db: Session, journey: Journey) -> dict:
    stops = list(journey.stops)
    total_kg, per_mode = estimate_carbon_for_stops(stops)
    carb = {
        "total_kg_co2e": round(total_kg, 4),
        "per_mode_kg_co2e": {k: round(v, 4) for k, v in per_mode.items()},
        "assumptions": "使用固定 gCO2e/人·km 系数；未区分电力结构，仅作课程演示。",
    }

    n_score, ratio, dom, n_notes = narrative_coherence(db, stops)
    narrative = {
        "score_0_to_100": round(n_score, 2),
        "story_poi_ratio": round(ratio, 4),
        "dominant_work": dom,
        "notes": n_notes,
    }

    sg_score, ds_n, avg_t, sg_notes = stargazing_suitability(db, stops)
    stargazing = {
        "score_0_to_100": round(sg_score, 2),
        "dark_sky_stops": ds_n,
        "avg_darkness_tier": round(avg_t, 2) if avg_t is not None else None,
        "notes": sg_notes,
    }

    return {"carbon": carb, "narrative": narrative, "stargazing": stargazing}


def journey_with_stops_loaded(db: Session, journey_id: int) -> Journey | None:
    stmt = (
        select(Journey)
        .options(
            selectinload(Journey.stops).selectinload(JourneyStop.literary_location),
            selectinload(Journey.stops).selectinload(JourneyStop.dark_sky_site),
        )
        .where(Journey.id == journey_id)
    )
    return db.execute(stmt).scalar_one_or_none()
