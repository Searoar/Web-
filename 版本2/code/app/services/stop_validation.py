"""经停中外键存在性校验：无效引用返回 422（语义错误，非 URL 资源缺失）。"""

from sqlalchemy.orm import Session

from app.models import DarkSkySite, LiteraryLocation, NaptanAccessNode
from app.schemas import JourneyStopCreate


def validate_stop_references(db: Session, stops: list[JourneyStopCreate]) -> None:
    """
    - literary_location_id / dark_sky_site_id 若给出，必须在对应表中存在。
    - 不存在时抛出 HTTPException 422，body 由全局处理器格式化为统一 JSON。
    """
    from fastapi import HTTPException, status

    for i, s in enumerate(stops):
        if s.literary_location_id is not None:
            loc = db.get(LiteraryLocation, s.literary_location_id)
            if loc is None:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail={
                        "error": {
                            "code": "invalid_reference",
                            "message": f"literary_location_id {s.literary_location_id} does not exist",
                            "field": f"stops[{i}].literary_location_id",
                        }
                    },
                )
        if s.dark_sky_site_id is not None:
            site = db.get(DarkSkySite, s.dark_sky_site_id)
            if site is None:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail={
                        "error": {
                            "code": "invalid_reference",
                            "message": f"dark_sky_site_id {s.dark_sky_site_id} does not exist",
                            "field": f"stops[{i}].dark_sky_site_id",
                        }
                    },
                )
        if s.naptan_access_node_id is not None:
            node = db.get(NaptanAccessNode, s.naptan_access_node_id)
            if node is None:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail={
                        "error": {
                            "code": "invalid_reference",
                            "message": f"naptan_access_node_id {s.naptan_access_node_id} does not exist",
                            "field": f"stops[{i}].naptan_access_node_id",
                        }
                    },
                )
