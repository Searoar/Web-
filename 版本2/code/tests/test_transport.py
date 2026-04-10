import pytest
from collections.abc import Generator

from fastapi.testclient import TestClient


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    from app.main import app

    with TestClient(app) as c:
        yield c


def test_naptan_and_nptg_list_ok(client: TestClient) -> None:
    r = client.get("/reference/naptan-access-nodes?limit=5")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    r2 = client.get("/reference/nptg-localities?limit=5")
    assert r2.status_code == 200
    assert isinstance(r2.json(), list)
