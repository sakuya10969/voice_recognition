import pytest

from api.app.services.task_managing_service import TaskManager
from app.models.transcription import TaskStatus

class TestTaskManager:
    @pytest.fixture
    def task_manager(self):
        """各テストで使用するTaskManagerインスタンスを提供するフィクスチャ"""
        return TaskManager()

    @pytest.fixture
    def task_id(self):
        """テスト用のタスクID"""
        return "test_task_123"

    @pytest.fixture
    def test_data(self):
        """テストデータを提供するフィクスチャ"""
        return {
            "transcribed": "テスト文字起こし",
            "summarized": "テスト要約",
            "error_message": "テストエラー"
        }

    def test_initialize_task(self, task_manager, task_id):
        """initialize_taskメソッドのテスト
        
        タスクの初期化が正しく行われることを確認する
        """
        task_manager.initialize_task(task_id)
        
        assert task_manager.status[task_id] == TaskStatus.PROCESSING
        assert task_manager.transcribed_text[task_id] is None
        assert task_manager.summarized_text[task_id] is None

    def test_complete_task(self, task_manager, task_id, test_data):
        """complete_taskメソッドのテスト
        
        タスクが正常に完了し、結果が保存されることを確認する
        """
        task_manager.initialize_task(task_id)
        task_manager.complete_task(
            task_id, 
            test_data["transcribed"], 
            test_data["summarized"]
        )
        
        assert task_manager.status[task_id] == TaskStatus.COMPLETED
        assert task_manager.transcribed_text[task_id] == test_data["transcribed"]
        assert task_manager.summarized_text[task_id] == test_data["summarized"]

    def test_fail_task(self, task_manager, task_id, test_data):
        """fail_taskメソッドのテスト
        
        タスクが失敗した場合のエラー処理を確認する
        """
        expected_error = f"エラー: {test_data['error_message']}"
        
        task_manager.initialize_task(task_id)
        task_manager.fail_task(task_id, test_data["error_message"])
        
        assert task_manager.status[task_id] == TaskStatus.FAILED
        assert task_manager.transcribed_text[task_id] == expected_error
        assert task_manager.summarized_text[task_id] == expected_error