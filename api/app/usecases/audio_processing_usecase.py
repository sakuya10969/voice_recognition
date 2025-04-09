from typing import Dict, Any, Optional
from pathlib import Path
import logging

from app.services.task_managing_service import TaskManagingService
from app.services.audio.audio_processing_service import AudioProcessingService
from app.services.word_generating_service import WordGeneratingService
from app.infrastructure.az_openai import AzOpenAIClient
from app.infrastructure.ms_sharepoint import MsSharePointClient
from app.infrastructure.az_blob import AzBlobClient
from app.infrastructure.az_speech import AzSpeechClient
from app.services.audio.mp4_processing_service import MP4ProcessingService
from app.services.text_summarization_service import TextSummarizationService
from app.services.audio.audio_transcription_service import AudioTranscriptionService

logger = logging.getLogger(__name__)

class AudioProcessingUseCase:
    """音声文字起こしのユースケース"""
    
    def __init__(
        self,
        task_managing_service: TaskManagingService,
        mp4_processing_service: MP4ProcessingService,
        word_generating_service: WordGeneratingService,
        az_blob_client: AzBlobClient,
        az_speech_client: AzSpeechClient,
        az_openai_client: AzOpenAIClient,
        ms_sharepoint_client: MsSharePointClient
    ):
        self._task_managing_service = task_managing_service
        self._audio_processing_service = AudioProcessingService(
            az_speech_client=az_speech_client,
            az_blob_client=az_blob_client,
            mp4_processing_service=mp4_processing_service,
            audio_transcription_service=AudioTranscriptionService(az_speech_client)
        )
        self._text_summarization_service = TextSummarizationService(
            az_openai_client=az_openai_client,
            max_tokens=7500,
            batch_size=5
        )
        self._word_generating_service = word_generating_service
        self._ms_sharepoint_client = ms_sharepoint_client

    async def execute(
        self,
        task_id: str,
        site_data: Optional[Dict[str, Any]],
        file_path: str
    ) -> None:
        """音声文字起こしの実行"""
        try:
            await self._execute_transcription_workflow(task_id, site_data, file_path)
        except Exception as e:
            self._handle_error(task_id, e)
            raise

    async def _execute_transcription_workflow(
        self,
        task_id: str,
        site_data: Optional[Dict[str, Any]],
        file_path: str
    ) -> None:
        """文字起こしワークフローの実行"""
        self._task_managing_service.initialize_task(task_id)
        
        # 音声処理と文字起こし、要約を実行
        transcribed_text = await self._audio_processing_service.process_audio(file_path)
        summarized_text = await self._text_summarization_service.summarize_text(transcribed_text)
        self._task_managing_service.complete_task(task_id, transcribed_text, summarized_text)
        
        # SharePointへのアップロードが必要な場合のみWordファイル処理を実行
        if site_data is not None and self._is_valid_site_data(site_data):
            try:
                await self._handle_word_document(task_id, site_data)
            except Exception as e:
                logger.warning(f"Wordファイルの処理中にエラーが発生しましたが、文字起こしは正常に完了しています: {str(e)}")

    async def _handle_word_document(self, task_id: str, site_data: Dict[str, Any]) -> None:
        """Wordファイルの生成とアップロード"""
        transcribed_text = self._task_managing_service.transcribed_text[task_id]
        summarized_text = self._task_managing_service.summarized_text[task_id]
        
        if not transcribed_text or not summarized_text:
            raise ValueError("文字起こしまたは要約テキストが存在しません")

        word_file_path = await self._word_generating_service.create_word_document(
            transcribed_text,
            summarized_text
        )
        
        try:
            self._ms_sharepoint_client.upload_file(
                site_data["site"],
                site_data["directory"],
                word_file_path
            )
        finally:
            await self._word_generating_service.cleanup_word_file(word_file_path)

    def _is_valid_site_data(self, site_data: Dict[str, Any]) -> bool:
        """サイトデータの検証"""
        return all(key in site_data for key in ["site", "directory"])

    def _handle_error(self, task_id: str, error: Exception) -> None:
        """エラー処理"""
        error_message = str(error)
        logger.error(f"タスク {task_id} の処理中にエラー: {error_message}")
        self._task_managing_service.fail_task(task_id, error_message)
