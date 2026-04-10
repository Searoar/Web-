import pytest
from collections.abc import Generator

from fastapi.testclient import TestClient


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    # 在设置 SQLITE_PATH 之后导入应用；必须使用 with 以触发 lifespan（建表 + 种子数据）
    from app.main import app

    with TestClient(app) as c:
        yield c


def test_health(client: TestClient) -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_reference_literary_and_sky(client: TestClient) -> None:
    lit = client.get("/reference/literary-locations")
    assert lit.status_code == 200
    assert len(lit.json()) >= 1
    sky = client.get("/reference/dark-sky-sites")
    assert sky.status_code == 200
    assert len(sky.json()) >= 1


def test_journey_crud_summary_analytics(client: TestClient) -> None:
    body = {
        "title": "英国慢游示例",
        "notes": "测试行程",
        "stops": [
            {
                "sequence_order": 0,
                "stop_type": "transit",
                "transport_mode": "train",
                "distance_km": 120.0,
                "label": "伦敦→德比",
            },
            {
                "sequence_order": 1,
                "stop_type": "story_poi",
                "literary_location_id": 1,
                "label": "取景地",
            },
            {
                "sequence_order": 2,
                "stop_type": "dark_sky",
                "dark_sky_site_id": 1,
                "label": "暗夜停留",
            },
        ],
    }
    create = client.post("/journeys", json=body)
    assert create.status_code == 201
    jid = create.json()["id"]

    r_get = client.get(f"/journeys/{jid}")
    assert r_get.status_code == 200
    assert len(r_get.json()["stops"]) == 3

    r_sum = client.get(f"/journeys/{jid}/summary")
    assert r_sum.status_code == 200
    assert r_sum.json()["dark_sky_stop_count"] == 1

    r_an = client.get(f"/journeys/{jid}/analytics")
    assert r_an.status_code == 200
    data = r_an.json()
    assert "carbon" in data and "narrative" in data and "stargazing" in data

    patch = client.patch(
        f"/journeys/{jid}",
        json={"title": "已改名", "stops": body["stops"]},
    )
    assert patch.status_code == 200
    assert patch.json()["title"] == "已改名"

    r_del = client.delete(f"/journeys/{jid}")
    assert r_del.status_code == 204
    assert client.get(f"/journeys/{jid}").status_code == 404
