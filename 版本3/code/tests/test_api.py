import pytest
from collections.abc import Generator

from fastapi.testclient import TestClient


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    # 在设置 SQLITE_PATH 之后导入应用；必须使用 with 以触发 lifespan（建表 + 种子数据）
    from app.main import app

    with TestClient(app) as c:
        yield c


@pytest.fixture()
def write_headers() -> dict[str, str]:
    return {"X-API-Key": "test-api-key"}


def test_health(client: TestClient) -> None:
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data.get("database") == "connected"


def test_reference_literary_and_sky(client: TestClient) -> None:
    lit = client.get("/reference/literary-locations")
    assert lit.status_code == 200
    assert len(lit.json()) >= 1
    sky = client.get("/reference/dark-sky-sites")
    assert sky.status_code == 200
    assert len(sky.json()) >= 1


def test_journey_crud_summary_analytics(client: TestClient, write_headers: dict[str, str]) -> None:
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
    create = client.post("/journeys", json=body, headers=write_headers)
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
        headers=write_headers,
    )
    assert patch.status_code == 200
    assert patch.json()["title"] == "已改名"

    r_del = client.delete(f"/journeys/{jid}", headers=write_headers)
    assert r_del.status_code == 204
    assert client.get(f"/journeys/{jid}").status_code == 404


def test_write_requires_api_key(client: TestClient) -> None:
    r = client.post("/journeys", json={"title": "无密钥", "stops": []})
    assert r.status_code == 401
    err = r.json()
    assert "error" in err
    assert err["error"]["code"] == "unauthorized"


def test_write_rejects_wrong_api_key(client: TestClient) -> None:
    r = client.post(
        "/journeys",
        json={"title": "错密钥", "stops": []},
        headers={"X-API-Key": "wrong"},
    )
    assert r.status_code == 401


def test_delete_journey_not_found(client: TestClient, write_headers: dict[str, str]) -> None:
    r = client.delete("/journeys/999999", headers=write_headers)
    assert r.status_code == 404
    body = r.json()
    assert body["error"]["code"] == "not_found"


def test_get_journey_not_found(client: TestClient) -> None:
    r = client.get("/journeys/999999")
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "not_found"


def test_create_invalid_literary_reference(client: TestClient, write_headers: dict[str, str]) -> None:
    body = {
        "title": "无效文学锚点",
        "stops": [
            {
                "sequence_order": 0,
                "stop_type": "story_poi",
                "literary_location_id": 99999,
            },
        ],
    }
    r = client.post("/journeys", json=body, headers=write_headers)
    assert r.status_code == 422
    j = r.json()
    assert j["error"]["code"] == "invalid_reference"
    assert "literary_location_id" in j["error"]["message"]


def test_create_invalid_dark_sky_reference(client: TestClient, write_headers: dict[str, str]) -> None:
    body = {
        "title": "无效观星点",
        "stops": [
            {
                "sequence_order": 0,
                "stop_type": "dark_sky",
                "dark_sky_site_id": 88888,
            },
        ],
    }
    r = client.post("/journeys", json=body, headers=write_headers)
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "invalid_reference"


def test_create_invalid_body_empty_title(client: TestClient, write_headers: dict[str, str]) -> None:
    r = client.post("/journeys", json={"title": "", "stops": []}, headers=write_headers)
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "validation_error"


def test_create_journey_empty_stops_ok(client: TestClient, write_headers: dict[str, str]) -> None:
    r = client.post(
        "/journeys",
        json={"title": "空经停列表", "stops": []},
        headers=write_headers,
    )
    assert r.status_code == 201
    data = r.json()
    assert data["stops"] == []


def test_malformed_json(client: TestClient, write_headers: dict[str, str]) -> None:
    r = client.post(
        "/journeys",
        content=b"not-json",
        headers={**write_headers, "Content-Type": "application/json"},
    )
    assert r.status_code == 422
