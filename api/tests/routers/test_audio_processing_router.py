import os
import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
from typing import Dict, Any

from app.main import app

client = TestClient(app)

TEST_FILE_PATH = "tests/test_data/test.mp4"
INVALID_FILE_PATH = "tests/test_data/invalid.txt"

class TestAudioProcessingRouter:
    """音声処理ルーターのテストクラス"""

    @pytest.fixture
    def test_audio_file(self) -> str:
        """テスト用の音声ファイルを提供するフィクスチャ"""
        if not os.path.exists(TEST_FILE_PATH):
            raise FileNotFoundError(f"Test file not found: {TEST_FILE_PATH}")
        return TEST_FILE_PATH

    @pytest.fixture
    def mock_transcription_status(self) -> Dict[str, Any]:
        """タスクステータスのモックデータを提供するフィクスチャ"""
        return {
            "task_id": "test-task-id",
            "status": "completed",
            "transcribed_text": "テスト文字起こし",
            "summarized_text": "テスト要約"
        }

    def test_transcribe_success(self, test_audio_file: str) -> None:
        """音声ファイルの文字起こし開始のテスト"""
        with patch("app.handlers.audio_processing_handler._create_transcription_usecase") as mock:
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

    def test_get_transcription_status_success(self, mock_transcription_status: Dict[str, Any]) -> None:
        """タスクステータス取得成功のテスト"""
        with patch("app.handlers.audio_processing_handler.get_transcription_status") as mock:
            mock.return_value = mock_transcription_status
            
            response = client.get(f"/transcription/{mock_transcription_status['task_id']}")
            assert response.status_code == 200
            
            data = response.json()
            assert data["task_id"] == mock_transcription_status["task_id"]
            assert "status" in data
            assert "transcribed_text" in data
            assert "summarized_text" in data

    def test_transcribe_with_invalid_file(self) -> None:
        """不正なファイルでの文字起こし開始テスト"""
        with open(INVALID_FILE_PATH, "wb") as f:
            f.write(b"invalid data")
        
        with open(INVALID_FILE_PATH, "rb") as file:
            response = client.post(
                "/transcription", 
                files={"file": ("invalid.txt", file, "text/plain")}
            )
            assert response.status_code == 400
            assert "detail" in response.json()

    def test_get_transcription_status_not_found(self) -> None:
        """存在しないタスクIDでのステータス取得テスト"""
        response = client.get("/transcription/non-existent-task")
        assert response.status_code == 404
        assert response.json()["detail"] == "タスクIDが存在しません"
