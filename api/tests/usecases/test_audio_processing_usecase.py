import pytest
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any

from app.usecases.audio_processing_usecase import AudioProcessingUseCase
from app.services.task_managing_service import TaskManagingService
from app.services.audio.mp4_processing_service import MP4ProcessingService
from app.services.word_generating_service import WordGeneratingService
from app.services.audio.audio_transcription_service import AudioTranscriptionService
from ..mocks.mock_az_client import (
    MockAzSpeechClient,
    MockAzBlobClient,
    MockAzOpenAIClient,
    MockMsSharePointClient
)

class TestAudioProcessorUseCase:
    @pytest.fixture
    def task_managing_service(self) -> TaskManagingService:
        """タスク管理サービスのモックを提供するフィクスチャ"""
        service = Mock(spec=TaskManagingService)
        service.initialize_task = Mock()
        service.complete_task = Mock()
        service.fail_task = Mock()
        service.transcribed_text = {
        "test-task-id": "これはテスト用の文字起こしテキストです。"
        }
        service.summarized_text = {
            "test-task-id": "これはテスト用の要約テキストです。"
        }
        return service

    @pytest.fixture
    def mp4_processing_service(self) -> MP4ProcessingService:
        """MP4処理サービスのモックを提供するフィクスチャ"""
        service = Mock(spec=MP4ProcessingService)
        service.process_mp4 = AsyncMock()
        return service

    @pytest.fixture
    def word_generating_service(self) -> WordGeneratingService:
        """Word文書生成サービスのモックを提供するフィクスチャ"""
        service = Mock(spec=WordGeneratingService)
        service.create_word_document = AsyncMock(return_value="test_word.docx")
        service.cleanup_word_file = AsyncMock()
        return service

    @pytest.fixture
    def mock_audio_processing_usecase(
        self,
        task_managing_service: TaskManagingService,
        mp4_processing_service: MP4ProcessingService,
        word_generating_service: WordGeneratingService
    ) -> AudioProcessingUseCase:
        """テスト対象のユースケースインスタンスを提供するフィクスチャ"""
        return AudioProcessingUseCase(
            task_managing_service=task_managing_service,
            mp4_processing_service=mp4_processing_service,
            word_generating_service=word_generating_service,
            az_blob_client=MockAzBlobClient(),
            az_speech_client=MockAzSpeechClient(),
            az_openai_client=MockAzOpenAIClient(),
            ms_sharepoint_client=MockMsSharePointClient()
        )

    @pytest.fixture
    def test_data(self) -> Dict[str, Any]:
        """テストデータを提供するフィクスチャ"""
        return {
            "task_id": "test-task-id",
            "file_path": "test.wav",
            "site_data": {
                "site": "test-site",
                "directory": "test-directory"
            }
        }

    async def _verify_common_assertions(self, task_managing_service: Mock, task_id: str) -> None:
        """共通の検証ロジックを実行するヘルパーメソッド"""
        task_managing_service.initialize_task.assert_called_once_with(task_id)
        task_managing_service.complete_task.assert_called_once()
        task_managing_service.fail_task.assert_not_called()

    @pytest.mark.asyncio
    @patch('app.usecases.audio_processing_usecase.AudioTranscriptionService')
    async def test_execute_success(
        self,
        audio_transcription_service: AudioTranscriptionService,
        mock_audio_processing_usecase: AudioProcessingUseCase,
        task_managing_service: TaskManagingService,
        test_data: Dict[str, Any]
    ) -> None:
        """正常系: サイトデータが完全な場合のテスト"""
        audio_transcription_service.return_value.transcribe_audio = AsyncMock(
            return_value="これはテスト用の文字起こしテキストです。"
        )

        await mock_audio_processing_usecase.execute(
            test_data["task_id"],
            test_data["site_data"],
            test_data["file_path"]
        )

        await self._verify_common_assertions(task_managing_service, test_data["task_id"])

    @pytest.mark.asyncio
    @patch('app.usecases.audio_processing_usecase.AudioTranscriptionService')
    async def test_execute_without_site_data(
        self,
        audio_transcription_service: AudioTranscriptionService,
        mock_audio_processing_usecase: AudioProcessingUseCase,
        task_managing_service: TaskManagingService,
        test_data: Dict[str, Any]
    ) -> None:
        """正常系: サイトデータがNoneの場合のテスト"""
        audio_transcription_service.return_value.transcribe_audio = AsyncMock(
            return_value="これはテスト用の文字起こしテキストです。"
        )

        await mock_audio_processing_usecase.execute(
            test_data["task_id"],
            None,
            test_data["file_path"]
        )

        await self._verify_common_assertions(task_managing_service, test_data["task_id"])

    @pytest.mark.asyncio
    @patch('app.usecases.audio_processing_usecase.AudioTranscriptionService')
    async def test_execute_with_invalid_site_data(
        self,
        audio_transcription_service: AudioTranscriptionService,
        mock_audio_processing_usecase: AudioProcessingUseCase,
        task_managing_service: TaskManagingService,
        test_data: Dict[str, Any]
    ) -> None:
        """正常系: サイトデータが不完全な場合のテスト"""
        audio_transcription_service.return_value.transcribe_audio = AsyncMock(
            return_value="これはテスト用の文字起こしテキストです。"
        )

        invalid_site_data = {"site": "test-site"}

        await mock_audio_processing_usecase.execute(
            test_data["task_id"],
            invalid_site_data,
            test_data["file_path"]
        )

        await self._verify_common_assertions(task_managing_service, test_data["task_id"])

    @pytest.mark.asyncio
    async def test_execute_with_error(
        self,
        mock_audio_processing_usecase: AudioProcessingUseCase,
        task_managing_service: TaskManagingService,
        test_data: Dict[str, Any]
    ) -> None:
        """異常系: エラーが発生した場合のテスト"""
        error_message = "テストエラー"
        task_managing_service.initialize_task.side_effect = Exception(error_message)

        with pytest.raises(Exception) as exc_info:
            await mock_audio_processing_usecase.execute(
                test_data["task_id"],
                None,
                test_data["file_path"]
            )

        assert str(exc_info.value) == error_message
        task_managing_service.fail_task.assert_called_once_with(test_data["task_id"], error_message)
