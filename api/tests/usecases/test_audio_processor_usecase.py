import pytest
from unittest.mock import Mock, AsyncMock
from app.usecases.audio_processor_usecase import AudioProcessorUseCase
from app.services.task_manager_service import TaskManager
from app.services.audio.mp4_processor_service import MP4ProcessorService
from app.services.word_generator_service import WordGeneratorService
from ..mocks.az_client_mock import (
    MockAzSpeechClient,
    MockAzBlobClient,
    MockAzOpenAIClient,
    MockMsSharePointClient
)

class TestAudioProcessorUseCase:
    @pytest.fixture
    def task_manager(self):
        manager = Mock(spec=TaskManager)
        manager.initialize_task = Mock()
        manager.complete_task = Mock()
        manager.fail_task = Mock()
        manager.transcribed_text = "これはテスト用の文字起こしテキストです。"
        manager.summarized_text = "これはテスト用の要約テキストです。"
        return manager

    @pytest.fixture
    def mp4_processor(self):
        return Mock(spec=MP4ProcessorService)

    @pytest.fixture
    def word_generator(self):
        generator = Mock(spec=WordGeneratorService)
        generator.create_word_document = AsyncMock(return_value="test_word.docx")
        generator.cleanup_word_file = AsyncMock()
        return generator

    @pytest.fixture
    def usecase(self, task_manager, mp4_processor, word_generator):
        return AudioProcessorUseCase(
            task_manager=task_manager,
            mp4_processor=mp4_processor,
            word_generator=word_generator,
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

    async def _verify_common_assertions(self, task_manager, task_id):
        """共通の検証ロジック"""
        task_manager.initialize_task.assert_called_once_with(task_id)
        task_manager.complete_task.assert_called_once()
        task_manager.fail_task.assert_not_called()

    @pytest.mark.asyncio
    async def test_execute_success(self, usecase, task_manager, test_data):
        # テストの実行
        await usecase.execute(
            test_data["task_id"],
            test_data["site_data"],
            test_data["file_path"]
        )

        # 検証
        await self._verify_common_assertions(task_manager, test_data["task_id"])

    @pytest.mark.asyncio
    async def test_execute_without_site_data(self, usecase, task_manager, test_data):
        # テストの実行
        await usecase.execute(
            test_data["task_id"],
            None,
            test_data["file_path"]
        )

        # 検証
        await self._verify_common_assertions(task_manager, test_data["task_id"])

    @pytest.mark.asyncio
    async def test_execute_with_invalid_site_data(self, usecase, task_manager, test_data):
        # 不完全なサイトデータ
        invalid_site_data = {"site": "test-site"}

        # テストの実行
        await usecase.execute(
            test_data["task_id"],
            invalid_site_data,
            test_data["file_path"]
        )

        # 検証
        await self._verify_common_assertions(task_manager, test_data["task_id"])

    @pytest.mark.asyncio
    async def test_execute_with_error(self, usecase, task_manager, test_data):
        # エラーを発生させるようにモックを設定
        error_message = "テストエラー"
        task_manager.initialize_task.side_effect = Exception(error_message)

        # テストの実行と例外の検証
        with pytest.raises(Exception) as exc_info:
            await usecase.execute(
                test_data["task_id"],
                None,
                test_data["file_path"]
            )

        assert str(exc_info.value) == error_message
        task_manager.fail_task.assert_called_once_with(test_data["task_id"], error_message)