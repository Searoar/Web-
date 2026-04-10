import pytest
from collections.abc import Generator

from fastapi.testclient import TestClient


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    from app.main import app

    with TestClient(app) as c:
        yield c


@pytest.fixture()
def write_headers() -> dict[str, str]:
    return {"X-API-Key": "test-api-key"}


@pytest.fixture()
def sample_naptan_id() -> int:
    from app.database import SessionLocal
    from app.models import NaptanAccessNode

    db = SessionLocal()
    try:
        n = NaptanAccessNode(
            atco_code="ZZTEST0001",
            common_name="Demo NaPTAN Stop",
            latitude=51.5,
            longitude=-0.12,
            stop_type="BCT",
        )
        db.add(n)
        db.commit()
        db.refresh(n)
        return n.id
    finally:
        db.close()


def test_pagination_limit_too_large(client: TestClient) -> None:
    r = client.get("/reference/literary-locations?limit=501")
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "validation_error"


def test_pagination_skip_negative(client: TestClient) -> None:
    r = client.get("/reference/literary-locations?skip=-1")
    assert r.status_code == 422


def test_journey_create_with_naptan_node(
    client: TestClient,
    write_headers: dict[str, str],
    sample_naptan_id: int,
) -> None:
    body = {
        "title": "含 NaPTAN 经停",
        "stops": [
            {
                "sequence_order": 0,
                "stop_type": "transit",
                "naptan_access_node_id": sample_naptan_id,
                "transport_mode": "bus",
                "distance_km": 2.5,
            },
        ],
    }
    r = client.post("/journeys", json=body, headers=write_headers)
    assert r.status_code == 201
    stop = r.json()["stops"][0]
    assert stop["naptan_access_node_id"] == sample_naptan_id
    assert stop.get("naptan_access_node") is not None
    assert stop["naptan_access_node"]["atco_code"] == "ZZTEST0001"


def test_naptan_foreign_key_invalid(client: TestClient, write_headers: dict[str, str]) -> None:
    body = {
        "title": "无效 naptan",
        "stops": [
            {
                "sequence_order": 0,
                "stop_type": "transit",
                "naptan_access_node_id": 999999999,
            },
        ],
    }
    r = client.post("/journeys", json=body, headers=write_headers)
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "invalid_reference"


def test_openapi_includes_api_key_security(client: TestClient) -> None:
    r = client.get("/openapi.json")
    assert r.status_code == 200
    spec = r.json()
    assert "components" in spec and "securitySchemes" in spec["components"]
    schemes = spec["components"]["securitySchemes"]
    assert any("apiKey" in str(v).lower() or v.get("type") == "apiKey" for v in schemes.values())
