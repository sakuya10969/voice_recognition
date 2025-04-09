import pytest
from typing import Dict
from app.services.task_managing_service import TaskManagingService
from app.models.transcription import TaskStatus

class TestTaskManagingService:
    @pytest.fixture
    def task_managing_service(self) -> TaskManagingService:
        """TaskManagingServiceのインスタンスを提供するフィクスチャ"""
        service = TaskManagingService()
        service.status = {}
        service.transcribed_text = {}
        service.summarized_text = {}
        return service

    @pytest.fixture
    def mock_task_id(self) -> str:
        """テスト用のタスクIDを提供するフィクスチャ"""
        return "test_task_123"

    @pytest.fixture
    def mock_test_data(self) -> Dict[str, str]:
        """テストデータを提供するフィクスチャ"""
        return {
            "transcribed_text": "テスト文字起こし",
            "summarized_text": "テスト要約",
            "error_message": "テストエラー"
        }

    def _verify_task_state(
        self,
        service: TaskManagingService,
        task_id: str,
        expected_status: TaskStatus,
        expected_transcribed_text: str | None,
        expected_summarized_text: str | None
    ) -> None:
        """タスクの状態を検証するヘルパーメソッド"""
        assert service.status[task_id] == expected_status
        assert service.transcribed_text[task_id] == expected_transcribed_text
        assert service.summarized_text[task_id] == expected_summarized_text

    def test_initialize_task(
        self,
        task_managing_service: TaskManagingService,
        mock_task_id: str
    ) -> None:
        """タスクの初期化が正しく行われることを確認する"""
        # 実行
        task_managing_service.initialize_task(mock_task_id)
        
        # 検証
        self._verify_task_state(
            task_managing_service,
            mock_task_id,
            TaskStatus.PROCESSING,
            None,
            None
        )

    def test_complete_task(
        self,
        task_managing_service: TaskManagingService,
        mock_task_id: str,
        mock_test_data: Dict[str, str]
    ) -> None:
        """タスクが正常に完了し、結果が保存されることを確認する"""
        # 準備
        task_managing_service.initialize_task(mock_task_id)
        
        # 実行
        task_managing_service.complete_task(
            mock_task_id, 
            mock_test_data["transcribed_text"], 
            mock_test_data["summarized_text"]
        )
        
        # 検証
        self._verify_task_state(
            task_managing_service,
            mock_task_id,
            TaskStatus.COMPLETED,
            mock_test_data["transcribed_text"],
            mock_test_data["summarized_text"]
        )

    def test_fail_task(
        self,
        task_managing_service: TaskManagingService,
        mock_task_id: str,
        mock_test_data: Dict[str, str]
    ) -> None:
        """タスクが失敗した場合のエラー処理を確認する"""
        # 準備
        expected_error = f"エラー: {mock_test_data['error_message']}"
        task_managing_service.initialize_task(mock_task_id)
        
        # 実行
        task_managing_service.fail_task(mock_task_id, mock_test_data["error_message"])
        
        # 検証
        self._verify_task_state(
            task_managing_service,
            mock_task_id,
            TaskStatus.FAILED,
            expected_error,
            expected_error
        )