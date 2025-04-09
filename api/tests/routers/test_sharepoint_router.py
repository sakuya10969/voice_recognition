# tests/routers/test_sharepoint_router.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

from app.main import app


@pytest.fixture
def client():
    mock_factory = MagicMock()
    mock_client = MagicMock()

    # 各 fetch メソッドをモック
    mock_client.fetch_sites.return_value = [{"id": "1", "name": "Site"}]
    mock_client.fetch_directories.return_value = [{"id": "1", "name": "Dir"}]
    mock_client.fetch_subdirectories.return_value = [{"id": "1", "name": "Subdir"}]
    mock_factory.create_ms_sharepoint_client.return_value = mock_client

    app.state.az_client_factory = mock_factory
    with TestClient(app) as c:
        yield c


def test_get_sites_success(client):
    res = client.get("/sites")
    assert res.status_code == 200
    assert res.json() == [{"id": "1", "name": "Site"}]


def test_get_directories_success(client):
    res = client.get("/directories", params={"site_id": "abc"})
    assert res.status_code == 200
    assert res.json() == [{"id": "1", "name": "Dir"}]


def test_get_directories_missing_param(client):
    res = client.get("/directories")
    assert res.status_code == 422
    assert any("site_id" in str(e["loc"]) for e in res.json()["detail"])


def test_get_subdirectories_success(client):
    res = client.get("/subdirectories", params={"site_id": "abc", "directory_id": "def"})
    assert res.status_code == 200
    assert res.json() == [{"id": "1", "name": "Subdir"}]


def test_get_subdirectories_missing_params(client):
    res = client.get("/subdirectories")
    assert res.status_code == 422
