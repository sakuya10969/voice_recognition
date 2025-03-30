from typing import Dict, Any, Optional
import logging
from app.services.task_manager_service import TaskManager
from app.services.audio.audio_processor_service import AudioProcessorService
from app.services.word_generator_service import WordGeneratorService
from app.infrastructure.az_openai import AzOpenAIClient
from app.infrastructure.ms_sharepoint import MsSharePointClient
from app.infrastructure.az_blob import AzBlobClient
from app.infrastructure.az_speech import AzSpeechClient
from app.services.audio.mp4_processor_service import MP4ProcessorService
from api.app.services.audio.transcribe_audio_service import TranscrbeAudioService

logger = logging.getLogger(__name__)

class TranscribeAudioUseCase:
    """音声文字起こしのユースケース"""
    
    def __init__(
        self,
        task_manager: TaskManager,
        mp4_processor: MP4ProcessorService,
        word_generator: WordGeneratorService,
        az_blob_client: AzBlobClient,
        az_speech_client: AzSpeechClient,
        az_openai_client: AzOpenAIClient,
        ms_sharepoint_client: MsSharePointClient
    ):
        self.task_manager = task_manager
        self.audio_processor = AudioProcessorService(
            speech_client=az_speech_client,
            blob_client=az_blob_client,
            mp4_processor=mp4_processor,
            transcription_service=TranscrbeAudioService(az_speech_client)
        )
        self.word_generator = word_generator
        self.openai_client = az_openai_client
        self.sharepoint_client = ms_sharepoint_client

    async def execute(
        self,
        task_id: str,
        site_data: Optional[Dict[str, Any]],
        file_path: str
    ) -> None:
        """音声文字起こしの実行"""
        try:
            self.task_manager.initialize_task(task_id)
            
            await self._process_audio_transcription(task_id, file_path)
            
            if site_data:
                await self._handle_word_document(site_data)

        except Exception as e:
            logger.error(f"タスク {task_id} の処理中にエラー: {str(e)}")
            self.task_manager.fail_task(task_id, str(e))
            raise

    async def _process_audio_transcription(self, task_id: str, file_path: str) -> None:
        """音声処理と文字起こし、要約を実行"""
        transcribed_text = await self.audio_processor.process_audio(file_path)
        summarized_text = await self.openai_client.summarize_text(transcribed_text)
        self.task_manager.complete_task(task_id, transcribed_text, summarized_text)

    async def _handle_word_document(self, site_data: Dict[str, Any]) -> None:
        """Wordファイルの生成とアップロード処理"""
        if not self._validate_site_data(site_data):
            return

        word_file_path = await self.word_generator.create_word_document(
            self.task_manager.transcribed_text,
            self.task_manager.summarized_text
        )
        try:
            await self.sharepoint_client.upload_file(
                site_data["site"],
                site_data["directory"],
                word_file_path
            )
        finally:
            await self.word_generator.cleanup_word_file(word_file_path)

    def _validate_site_data(self, site_data: Dict[str, Any]) -> bool:
        """サイトデータのバリデーション"""
        return all(k in site_data for k in ["site", "directory"])
