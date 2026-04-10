"""演示用种子数据：文学/影视取景地与暗夜观星点。"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import DarkSkySite, LiteraryLocation


def seed_reference_data(db: Session) -> None:
    if db.scalars(select(LiteraryLocation).limit(1)).first() is not None:
        return

    literary_rows = [
        LiteraryLocation(
            title="九又四分之三站台",
            work_title="哈利·波特",
            creator="J.K. Rowling",
            latitude=51.5322,
            longitude=-0.1240,
            region="伦敦",
            description="国王十字车站取景灵感来源地之一。",
        ),
        LiteraryLocation(
            title="查茨沃斯庄园",
            work_title="傲慢与偏见",
            creator="Jane Austen",
            latitude=53.2272,
            longitude=-1.6110,
            region="德比郡",
            description="2005 版电影彭伯里庄园取景地。",
        ),
        LiteraryLocation(
            title="福尔摩斯博物馆",
            work_title="福尔摩斯探案集",
            creator="Arthur Conan Doyle",
            latitude=51.5238,
            longitude=-0.1585,
            region="伦敦",
            description="贝克街 221B 主题馆。",
        ),
    ]
    sky_rows = [
        DarkSkySite(
            name="布雷肯比肯斯国际暗夜天空保护区",
            latitude=51.9400,
            longitude=-3.3800,
            darkness_tier=1,
            notes="英国首个暗夜保护区，适合银河与流星雨。",
        ),
        DarkSkySite(
            name="诺森伯兰国际暗夜公园",
            latitude=55.2300,
            longitude=-2.5000,
            darkness_tier=2,
            notes="英格兰光污染极低区域之一。",
        ),
        DarkSkySite(
            name="康沃尔海岸观星点（示例）",
            latitude=50.0660,
            longitude=-5.7150,
            darkness_tier=3,
            notes="海岸开阔，需关注云层与月相。",
        ),
    ]
    db.add_all(literary_rows)
    db.add_all(sky_rows)
    db.commit()
