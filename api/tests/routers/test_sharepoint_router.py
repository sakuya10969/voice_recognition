import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def inject_mock_sharepoint_client(mocker):
    """MsSharePointClientのMockをapp.stateに注入"""
    mock_client = MagicMock()
    factory_mock = MagicMock()
    factory_mock.create_ms_sharepoint_client.return_value = mock_client
    app.state.az_client_factory = factory_mock
    return mock_client

def test_get_sites(client, inject_mock_sharepoint_client):
    mock_client = inject_mock_sharepoint_client
    mock_client.get_sites.return_value = {"sites": ["SiteA", "SiteB"]}

    response = client.get("/sites")

    assert response.status_code == 200
    assert response.json() == {"sites": ["SiteA", "SiteB"]}
    mock_client.get_sites.assert_called_once()

def test_get_directories(client, inject_mock_sharepoint_client):
    mock_client = inject_mock_sharepoint_client
    mock_client.get_folders.return_value = {"folders": ["Folder1", "Folder2"]}

    response = client.get("/directories", params={"site_id": "site123"})

    assert response.status_code == 200
    assert response.json() == {"folders": ["Folder1", "Folder2"]}
    mock_client.get_folders.assert_called_once_with("site123")

def test_get_subdirectories(client, inject_mock_sharepoint_client):
    mock_client = inject_mock_sharepoint_client
    mock_client.get_subfolders.return_value = {"subfolders": ["Sub1", "Sub2"]}

    response = client.get("/subdirectories", params={
        "site_id": "site123",
        "directory_id": "dir456"
    })

    assert response.status_code == 200
    assert response.json() == {"subfolders": ["Sub1", "Sub2"]}
    mock_client.get_subfolders.assert_called_once_with("site123", "dir456")
