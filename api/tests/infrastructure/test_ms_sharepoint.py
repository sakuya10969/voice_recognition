import pytest
from unittest.mock import patch, MagicMock, mock_open
from app.infrastructure.ms_sharepoint import MsSharePointClient

@pytest.fixture
def sharepoint_client():
    with patch("app.infrastructure.ms_sharepoint.msal.ConfidentialClientApplication") as mock_msal:
        # MSALモックでトークン取得成功
        instance = mock_msal.return_value
        instance.acquire_token_for_client.return_value = {"access_token": "fake_token"}

        client = MsSharePointClient(
            client_id="fake_id",
            client_secret="fake_secret",
            tenant_id="fake_tenant"
        )
        return client

@patch("app.infrastructure.ms_sharepoint.requests.get")
def test_get_sites(mock_get, sharepoint_client):
    mock_get.return_value = MagicMock(status_code=200)
    mock_get.return_value.json.return_value = {
        "value": [{"id": "site123", "name": "TestSite"}]
    }

    result = sharepoint_client.get_sites()
    assert result["value"][0]["name"] == "TestSite"

@patch("app.infrastructure.ms_sharepoint.requests.get")
def test_get_site_id(mock_get, sharepoint_client):
    mock_get.return_value = MagicMock()
    mock_get.return_value.json.return_value = {
        "value": [{"id": "site123", "name": "MySite"}]
    }

    result = sharepoint_client.get_site_id("MySite")
    assert result == "site123"

@patch("app.infrastructure.ms_sharepoint.requests.get")
def test_get_folders_filter_only_folders(mock_get, sharepoint_client):
    mock_get.return_value = MagicMock()
    mock_get.return_value.json.return_value = {
        "value": [
            {"name": "FolderA", "folder": {}},
            {"name": "file.txt"}  # フォルダじゃない
        ]
    }

    folders = sharepoint_client.get_folders("site123")
    assert len(folders["value"]) == 1
    assert folders["value"][0]["name"] == "FolderA"

@patch("app.infrastructure.ms_sharepoint.requests.get")
def test_get_folder_id(mock_get, sharepoint_client):
    mock_get.return_value = MagicMock()
    mock_get.return_value.json.return_value = {
        "value": [{"name": "Reports", "id": "folder456", "folder": {}}]
    }

    folder_id = sharepoint_client.get_folder_id("site123", "Reports")
    assert folder_id == "folder456"

@patch("app.infrastructure.ms_sharepoint.requests.put")
@patch("builtins.open", new_callable=mock_open, read_data=b"dummy_content")
def test_upload_file(mock_open_file, mock_put, sharepoint_client):
    mock_put.return_value = MagicMock(status_code=200)

    from pathlib import Path
    test_path = Path("dummy.txt")
    sharepoint_client.upload_file("site123", "folder789", test_path)

    mock_open_file.assert_called_once_with(test_path, "rb")
    mock_put.assert_called_once()
    assert "dummy.txt" in mock_put.call_args[1]["url"]

@patch("app.infrastructure.ms_sharepoint.msal.ConfidentialClientApplication")
def test_missing_token_raises_error(mock_msal):
    # MSALのトークン取得を正常にモックする（トークン入れるけど、あとで外す）
    instance = mock_msal.return_value
    instance.acquire_token_for_client.return_value = {"access_token": "mock_token"}

    client = MsSharePointClient("fake", "fake", "fake")
    client.access_token = None  # 明示的にNoneにする

    with pytest.raises(ValueError) as exc_info:
        client._validate_token()

    assert "アクセストークンが設定されていません" in str(exc_info.value)
