import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.main import app

client = TestClient(app)

@pytest.fixture
def mock_sites():
    """サイト一覧のモックデータ"""
    return [
        {"id": "1", "name": "Site 1"},
        {"id": "2", "name": "Site 2"}
    ]

@pytest.fixture
def mock_directories():
    """ディレクトリ一覧のモックデータ"""
    return [
        {"id": "1", "name": "Directory 1"},
        {"id": "2", "name": "Directory 2"}
    ]

@pytest.fixture
def mock_subdirectories():
    """サブディレクトリ一覧のモックデータ"""
    return [
        {"id": "1", "name": "Subdirectory 1"},
        {"id": "2", "name": "Subdirectory 2"}
    ]

def test_get_sites_success(mock_sites):
    """サイト一覧取得のテスト
    
    期待される動作:
    - ステータスコード200が返される
    - モックデータと一致するレスポンスが返される
    """
    with patch('app.handlers.sharepoint_handler.get_sites', return_value=mock_sites):
        response = client.get("/sites")
        assert response.status_code == 200
        assert response.json() == mock_sites

def test_get_sites_failure():
    """サイト一覧取得失敗のテスト
    
    期待される動作:
    - ステータスコード500が返される
    - エラーメッセージが含まれる
    """
    with patch('app.handlers.sharepoint_handler.get_sites', side_effect=Exception("SharePoint error")):
        response = client.get("/sites")
        assert response.status_code == 500
        assert "サイト取得中にエラーが発生しました" in response.json()["detail"]

def test_get_directories_success(mock_directories):
    """ディレクトリ一覧取得のテスト
    
    期待される動作:
    - ステータスコード200が返される
    - モックデータと一致するレスポンスが返される
    """
    with patch('app.handlers.sharepoint_handler.get_directories', return_value=mock_directories):
        response = client.get("/directories?site_id=test-site")
        assert response.status_code == 200
        assert response.json() == mock_directories

def test_get_directories_failure():
    """ディレクトリ一覧取得失敗のテスト
    
    期待される動作:
    - ステータスコード500が返される
    - エラーメッセージが含まれる
    """
    with patch('app.handlers.sharepoint_handler.get_directories', side_effect=Exception("SharePoint error")):
        response = client.get("/directories?site_id=test-site")
        assert response.status_code == 500
        assert "ディレクトリ取得中にエラーが発生しました" in response.json()["detail"]

def test_get_directories_missing_site_id():
    """サイトID未指定でのディレクトリ一覧取得テスト
    
    期待される動作:
    - ステータスコード422が返される
    - バリデーションエラーメッセージが含まれる
    """
    response = client.get("/directories")
    assert response.status_code == 422
    assert "site_id" in response.json()["detail"][0]["loc"]

def test_get_subdirectories_success(mock_subdirectories):
    """サブディレクトリ一覧取得のテスト
    
    期待される動作:
    - ステータスコード200が返される
    - モックデータと一致するレスポンスが返される
    """
    with patch('app.handlers.sharepoint_handler.get_subdirectories', return_value=mock_subdirectories):
        response = client.get("/subdirectories?site_id=test-site&directory_id=test-dir")
        assert response.status_code == 200
        assert response.json() == mock_subdirectories

def test_get_subdirectories_failure():
    """サブディレクトリ一覧取得失敗のテスト
    
    期待される動作:
    - ステータスコード500が返される
    - エラーメッセージが含まれる
    """
    with patch('app.handlers.sharepoint_handler.get_subdirectories', side_effect=Exception("SharePoint error")):
        response = client.get("/subdirectories?site_id=test-site&directory_id=test-dir")
        assert response.status_code == 500
        assert "サブディレクトリ取得中にエラーが発生しました" in response.json()["detail"]

def test_get_subdirectories_missing_params():
    """必須パラメータ未指定でのサブディレクトリ一覧取得テスト
    
    期待される動作:
    - ステータスコード422が返される
    - バリデーションエラーメッセージが含まれる
    """
    response = client.get("/subdirectories")
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any("site_id" in error["loc"] for error in errors)
    assert any("directory_id" in error["loc"] for error in errors)