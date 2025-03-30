from typing import Dict, Any, Optional
import logging
from app.services.task_manager_service import TaskManager
from app.services.audio.audio_service import AudioService
from app.services.document.word_generator_service import WordGeneratorService
from app.infrastructure.az_openai import AzOpenAIClient
from app.infrastructure.ms_sharepoint import MsSharePointClient

logger = logging.getLogger(__name__)

class TranscribeAudioUseCase:
    """音声文字起こしのユースケース"""
    
    def __init__(
        self,
        task_manager: TaskManager,
        audio_service: AudioService,
        word_generator: WordGeneratorService,
        openai_client: AzOpenAIClient,
        sharepoint_client: MsSharePointClient
    ):
        self.task_manager = task_manager
        self.audio_service = audio_service
        self.word_generator = word_generator
        self.openai_client = openai_client
        self.sharepoint_client = sharepoint_client

    async def execute(
        self,
        task_id: str,
        site_data: Optional[Dict[str, Any]],
        file_path: str
    ) -> None:
        """音声文字起こしの実行"""
        try:
            # タスクの初期化
            self.task_manager.initialize_task(task_id)
            
            # 音声ファイルの処理
            audio_data = await self.audio_service.process_audio_file(file_path)
            if not audio_data or "blob_url" not in audio_data:
                raise ValueError("音声ファイルの処理に失敗しました")

            # 文字起こしと要約
            transcribed_text = await self.audio_service.transcribe_audio(audio_data["blob_url"])
            summarized_text = await self.openai_client.summarize_text(transcribed_text)

            # SharePoint処理
            await self._handle_sharepoint_upload(
                site_data,
                transcribed_text,
                summarized_text
            )

            # タスク完了処理
            self.task_manager.complete_task(task_id, transcribed_text, summarized_text)
            await self.audio_service._blob_client.delete_blob(audio_data["file_name"])

        except Exception as e:
            self._handle_error(task_id, e)
            raise

    async def _handle_sharepoint_upload(
        self,
        site_data: Optional[Dict[str, Any]],
        transcribed_text: str,
        summarized_text: str
    ) -> None:
        """SharePointへのアップロード処理"""
        if site_data and all(k in site_data for k in ["site", "directory"]):
            word_file_path = await self.word_generator.create_word_document(
                transcribed_text,
                summarized_text
            )
            try:
                await self.sharepoint_client.upload_file(
                    site_data["site"],
                    site_data["directory"],
                    word_file_path,
                )
            finally:
                await self.word_generator.cleanup_word_file(word_file_path)

    def _handle_error(self, task_id: str, error: Exception) -> None:
        """エラー処理"""
        self.task_manager.fail_task(task_id, str(error))
        logger.error(f"タスク {task_id} の処理中にエラー: {str(error)}")
