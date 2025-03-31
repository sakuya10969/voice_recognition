import os
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

TEST_FILE_PATH = "tests/test_data/test.mp4"

@pytest.fixture
def test_audio_file():
    """テスト用の音声ファイル"""
    if not os.path.exists(TEST_FILE_PATH):
        raise FileNotFoundError(f"Test file not found: {TEST_FILE_PATH}")
    return TEST_FILE_PATH

@pytest.fixture
def mock_task_manager():
    """タスクマネージャーのモック"""
    with patch("app.handlers.transcription_handler._create_transcription_usecase") as mock:
        yield mock

def test_transcribe_success(test_audio_file, mock_task_manager):
    """音声ファイルの文字起こし開始のテスト
    
    期待される動作:
    - ステータスコード202が返される
    - レスポンスにtask_idが含まれる
    - 処理開始メッセージが含まれる
    """
    with open(test_audio_file, "rb") as file:
        response = client.post(
            "/transcription", 
            files={"file": ("test.mp4", file, "video/mp4")}
        )
        
        assert response.status_code == 202
        response_data = response.json()
        assert "task_id" in response_data
        assert "message" in response_data
        assert response_data["message"] == "処理を開始しました"

def test_get_transcription_status_success():
    """タスクステータス取得成功のテスト
    
    期待される動作:
    - ステータスコード200が返される
    - 必要な情報がレスポンスに含まれる
    """
    task_id = "test-task-id"
    with patch("app.handlers.transcription_handler.get_transcription_status") as mock:
        mock.return_value = {
            "task_id": task_id,
            "status": "completed",
            "transcribed_text": "テスト文字起こし",
            "summarized_text": "テスト要約"
        }
        
        response = client.get(f"/transcription/{task_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["task_id"] == task_id
        assert "status" in data
        assert "transcribed_text" in data
        assert "summarized_text" in data

def test_transcribe_with_invalid_file():
    """不正なファイルでの文字起こし開始テスト
    
    期待される動作:
    - ステータスコード400が返される
    - エラーメッセージが含まれる
    """
    with open("tests/test_data/invalid.txt", "wb") as f:
        f.write(b"invalid data")
    
    with open("tests/test_data/invalid.txt", "rb") as file:
        response = client.post(
            "/transcription", 
            files={"file": ("invalid.txt", file, "text/plain")}
        )
        assert response.status_code == 400
        assert "detail" in response.json()

def test_get_transcription_status_not_found():
    """存在しないタスクIDでのステータス取得テスト
    
    期待される動作:
    - ステータスコード404が返される
    - エラーメッセージが含まれる
    """
    response = client.get("/transcription/non-existent-task")
    assert response.status_code == 404
    assert response.json()["detail"] == "タスクIDが存在しません"
