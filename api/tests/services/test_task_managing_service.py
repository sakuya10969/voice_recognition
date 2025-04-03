import pytest
from unittest.mock import patch

from app.services.task_managing_service import TaskManagingService
from app.models.transcription import TaskStatus

class TestTaskManagingService:
    @pytest.fixture
    def mock_task_managing_service(self):
        """各テストで使用するTaskManagerインスタンスを提供するフィクスチャ"""
        with patch('app.services.task_managing_service.TaskManagingService._initialize_storage'):
            mock_task_managing_service = TaskManagingService()
            mock_task_managing_service.status = {}
            mock_task_managing_service.transcribed_text = {}
            mock_task_managing_service.summarized_text = {}
            return mock_task_managing_service

    @pytest.fixture
    def mock_task_id(self):
        """テスト用のタスクID"""
        return "test_task_123"

    @pytest.fixture
    def mock_test_data(self):
        """テストデータを提供するフィクスチャ"""
        return {
            "transcribed": "テスト文字起こし",
            "summarized": "テスト要約",
            "error_message": "テストエラー"
        }

    def test_initialize_task(self, mock_task_managing_service, mock_task_id):
        """initialize_taskメソッドのテスト
        
        タスクの初期化が正しく行われることを確認する
        """
        mock_task_managing_service.initialize_task(mock_task_id)
        
        assert mock_task_managing_service.status[mock_task_id] == TaskStatus.PROCESSING
        assert mock_task_managing_service.transcribed_text[mock_task_id] is None
        assert mock_task_managing_service.summarized_text[mock_task_id] is None

    def test_complete_task(self, mock_task_managing_service, mock_task_id, mock_test_data):
        """complete_taskメソッドのテスト
        
        タスクが正常に完了し、結果が保存されることを確認する
        """
        mock_task_managing_service.initialize_task(mock_task_id)
        mock_task_managing_service.complete_task(
            mock_task_id, 
            mock_test_data["transcribed"], 
            mock_test_data["summarized"]
        )
        
        assert mock_task_managing_service.status[mock_task_id] == TaskStatus.COMPLETED
        assert mock_task_managing_service.transcribed_text[mock_task_id] == mock_test_data["transcribed"]
        assert mock_task_managing_service.summarized_text[mock_task_id] == mock_test_data["summarized"]

    def test_fail_task(self, mock_task_managing_service, mock_task_id, mock_test_data):
        """fail_taskメソッドのテスト
        
        タスクが失敗した場合のエラー処理を確認する
        """
        expected_error = f"エラー: {mock_test_data['error_message']}"
        
        mock_task_managing_service.initialize_task(mock_task_id)
        mock_task_managing_service.fail_task(mock_task_id, mock_test_data["error_message"])
        
        assert mock_task_managing_service.status[mock_task_id] == TaskStatus.FAILED
        assert mock_task_managing_service.transcribed_text[mock_task_id] == expected_error
        assert mock_task_managing_service.summarized_text[mock_task_id] == expected_error