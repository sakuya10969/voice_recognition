from typing import Dict, Optional
from app.models.transcription import TaskStatus

class TaskManagingService:
    """
    タスクの状態と文字起こし・要約結果を管理するアプリケーションサービス
    """
    def __init__(self):
        self.status: Dict[str, TaskStatus] = {}
        self.transcribed_text: Dict[str, Optional[str]] = {}
        self.summarized_text: Dict[str, Optional[str]] = {}

    def initialize_task(self, task_id: str) -> None:
        """新規タスクを初期化する"""
        self.status[task_id] = TaskStatus.PROCESSING
        self.transcribed_text[task_id] = None
        self.summarized_text[task_id] = None

    def complete_task(self, task_id: str, transcribed: str, summarized: str) -> None:
        """タスクを完了状態にし、結果を保存する"""
        self.status[task_id] = TaskStatus.COMPLETED
        self.transcribed_text[task_id] = transcribed
        self.summarized_text[task_id] = summarized

    def fail_task(self, task_id: str, error_message: str) -> None:
        """タスクを失敗状態にし、エラーメッセージを保存する"""
        self.status[task_id] = TaskStatus.FAILED
        error_text = f"エラー: {error_message}"
        self.transcribed_text[task_id] = error_text
        self.summarized_text[task_id] = error_text