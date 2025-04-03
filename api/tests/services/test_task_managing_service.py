import pytest
from unittest.mock import patch
from typing import Dict, Any
from app.services.task_managing_service import TaskManagingService
from app.models.transcription import TaskStatus

class TestTaskManagingService:
    @pytest.fixture
    def task_managing_service(self):
        """各テストで使用するTaskManagerインスタンスを提供するフィクスチャ"""
        with patch('app.services.task_managing_service.TaskManagingService._initialize_storage'):
            service = TaskManagingService()
            service.status = {}
            service.transcribed_text = {}
            service.summarized_text = {}
            return service

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

    async def _verify_task_state(
        self,
        mock_task_managing_service: TaskManagingService,
        mock_task_id: str,
        expected_status: TaskStatus,
        expected_transcribed: str | None,
        expected_summarized: str | None
    ) -> None:
        """タスクの状態を検証するヘルパーメソッド"""
        assert mock_task_managing_service.status[mock_task_id] == expected_status
        assert mock_task_managing_service.transcribed_text[mock_task_id] == expected_transcribed
        assert mock_task_managing_service.summarized_text[mock_task_id] == expected_summarized

    @pytest.mark.asyncio
    async def test_initialize_task(self, task_managing_service: TaskManagingService, mock_task_id: str):
        """initialize_taskメソッドのテスト
        
        タスクの初期化が正しく行われることを確認する
        """
        await task_managing_service.initialize_task(mock_task_id)
        
        await self._verify_task_state(
            task_managing_service,
            mock_task_id,
            TaskStatus.PROCESSING,
            None,
            None
        )

    @pytest.mark.asyncio
    async def test_complete_task(self, task_managing_service: TaskManagingService, mock_task_id: str, mock_test_data: Dict[str, Any]):
        """complete_taskメソッドのテスト
        
        タスクが正常に完了し、結果が保存されることを確認する
        """
        await task_managing_service.initialize_task(mock_task_id)
        await task_managing_service.complete_task(
            mock_task_id, 
            mock_test_data["transcribed"], 
            mock_test_data["summarized"]
        )
        
        await self._verify_task_state(
            task_managing_service,
            mock_task_id,
            TaskStatus.COMPLETED,
            mock_test_data["transcribed"],
            mock_test_data["summarized"]
        )

    @pytest.mark.asyncio
    async def test_fail_task(self, task_managing_service: TaskManagingService, mock_task_id: str, mock_test_data: Dict[str, Any]):
        """fail_taskメソッドのテスト
        
        タスクが失敗した場合のエラー処理を確認する
        """
        expected_error = f"エラー: {mock_test_data['error_message']}"
        
        await task_managing_service.initialize_task(mock_task_id)
        await task_managing_service.fail_task(mock_task_id, mock_test_data["error_message"])
        
        await self._verify_task_state(
            task_managing_service,
            mock_task_id,
            TaskStatus.FAILED,
            expected_error,
            expected_error
        )