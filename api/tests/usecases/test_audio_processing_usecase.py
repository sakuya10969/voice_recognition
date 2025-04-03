import pytest
from unittest.mock import Mock, AsyncMock, patch

from app.usecases.audio_processing_usecase import AudioProcessingUseCase
from app.services.task_managing_service import TaskManagingService
from app.services.audio.mp4_processing_service import MP4ProcessingService
from app.services.word_generating_service import WordGeneratingService
from ..mocks.mock_az_client import (
    MockAzSpeechClient,
    MockAzBlobClient,
    MockAzOpenAIClient,
    MockMsSharePointClient
)

class TestAudioProcessorUseCase:
    @pytest.fixture
    def mock_task_managing_service(self):
        mock_task_managing_service = Mock(spec=TaskManagingService)
        mock_task_managing_service.initialize_task = AsyncMock()
        mock_task_managing_service.complete_task = AsyncMock()
        mock_task_managing_service.fail_task = AsyncMock()
        mock_task_managing_service.transcribed_text = "これはテスト用の文字起こしテキストです。"
        mock_task_managing_service.summarized_text = "これはテスト用の要約テキストです。"
        return mock_task_managing_service

    @pytest.fixture
    def mock_mp4_processing_service(self):
        mock_mp4_processing_service = Mock(spec=MP4ProcessingService)
        mock_mp4_processing_service.process_mp4 = AsyncMock()
        return mock_mp4_processing_service

    @pytest.fixture
    def mock_word_generating_service(self):
        mock_word_generating_service = Mock(spec=WordGeneratingService)
        mock_word_generating_service.create_word_document = AsyncMock(return_value="test_word.docx")
        mock_word_generating_service.cleanup_word_file = AsyncMock()
        return mock_word_generating_service

    @pytest.fixture
    def mock_audio_processing_usecase(self, mock_task_managing_service, mock_mp4_processing_service, mock_word_generating_service):
        return AudioProcessingUseCase(
            task_managing_service=mock_task_managing_service,
            mp4_processing_service=mock_mp4_processing_service,
            word_generating_service=mock_word_generating_service,
            az_blob_client=MockAzBlobClient(),
            az_speech_client=MockAzSpeechClient(),
            az_openai_client=MockAzOpenAIClient(),
            ms_sharepoint_client=MockMsSharePointClient()
        )

    @pytest.fixture
    def test_data(self):
        return {
            "task_id": "test-task-id",
            "file_path": "test.wav",
            "site_data": {
                "site": "test-site",
                "directory": "test-directory"
            }
        }

    async def _verify_common_assertions(self, task_managing_service, task_id):
        """共通の検証ロジック"""
        task_managing_service.initialize_task.assert_awaited_once_with(task_id)
        task_managing_service.complete_task.assert_awaited_once()
        task_managing_service.fail_task.assert_not_awaited()

    @pytest.mark.asyncio
    @patch('app.usecases.audio_processing_usecase.AudioTranscriptionService')
    async def test_execute_success(self, mock_transcription_service, usecase, task_managing_service, test_data):
        # モックの設定
        mock_transcription_service.return_value.transcribe_audio = AsyncMock(
            return_value="これはテスト用の文字起こしテキストです。"
        )

        # テストの実行
        await usecase.execute(
            test_data["task_id"],
            test_data["site_data"],
            test_data["file_path"]
        )

        # 検証
        await self._verify_common_assertions(task_managing_service, test_data["task_id"])

    @pytest.mark.asyncio
    @patch('app.usecases.audio_processing_usecase.AudioTranscriptionService')
    async def test_execute_without_site_data(self, mock_transcription_service, usecase, task_managing_service, test_data):
        # モックの設定
        mock_transcription_service.return_value.transcribe_audio = AsyncMock(
            return_value="これはテスト用の文字起こしテキストです。"
        )

        # テストの実行
        await usecase.execute(
            test_data["task_id"],
            None,
            test_data["file_path"]
        )

        # 検証
        await self._verify_common_assertions(task_managing_service, test_data["task_id"])

    @pytest.mark.asyncio
    @patch('app.usecases.audio_processing_usecase.AudioTranscriptionService')
    async def test_execute_with_invalid_site_data(self, mock_transcription_service, usecase, task_managing_service, test_data):
        # モックの設定
        mock_transcription_service.return_value.transcribe_audio = AsyncMock(
            return_value="これはテスト用の文字起こしテキストです。"
        )

        # 不完全なサイトデータ
        invalid_site_data = {"site": "test-site"}

        # テストの実行
        await usecase.execute(
            test_data["task_id"],
            invalid_site_data,
            test_data["file_path"]
        )

        # 検証
        await self._verify_common_assertions(task_managing_service, test_data["task_id"])

    @pytest.mark.asyncio
    async def test_execute_with_error(self, usecase, task_managing_service, test_data):
        # エラーを発生させるようにモックを設定
        error_message = "テストエラー"
        task_managing_service.initialize_task.side_effect = Exception(error_message)

        # テストの実行と例外の検証
        with pytest.raises(Exception) as exc_info:
            await usecase.execute(
                test_data["task_id"],
                None,
                test_data["file_path"]
            )

        assert str(exc_info.value) == error_message
        task_managing_service.fail_task.assert_awaited_once_with(test_data["task_id"], error_message)
