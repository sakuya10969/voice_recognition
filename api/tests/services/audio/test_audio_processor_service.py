import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException
from app.services.audio.audio_processor_service import AudioProcessorService
from app.services.audio.mp4_processor_service import MP4ProcessorService
from app.services.audio.transcribe_audio_service import TranscribeAudioService
from tests.mocks.az_client_mock import MockAzSpeechClient, MockAzBlobClient

class TestAudioProcessorService:
    @pytest.fixture
    def mock_az_blob_client(self):
        return MockAzBlobClient()

    @pytest.fixture
    def mock_az_speech_client(self):
        return MockAzSpeechClient()

    @pytest.fixture
    def mock_mp4_processor(self):
        processor = MagicMock(spec=MP4ProcessorService)
        processor.process_mp4.return_value = {
            "file_name": "audio.wav",
            "file_data": b"fake-data"
        }
        return processor

    @pytest.fixture
    def mock_transcribe_service(self):
        service = MagicMock(spec=TranscribeAudioService)
        service.transcribe.return_value = "これはテスト用の文字起こしテキストです。"
        return service

    @pytest.fixture
    def service(self, mock_az_speech_client, mock_az_blob_client, mock_mp4_processor, mock_transcribe_service):
        return AudioProcessorService(
            az_speech_client=mock_az_speech_client,
            az_blob_client=mock_az_blob_client,
            mp4_processor=mock_mp4_processor,
            transcription_service=mock_transcribe_service
        )

    @pytest.mark.asyncio
    async def test_process_audio_success(self, service, mock_az_blob_client, mock_mp4_processor, mock_transcribe_service):
        """正常系: 音声処理が成功するケース"""
        # 実行
        result = await service.process_audio("dummy/path/to/audio.mp4")

        # 検証
        assert result == "これはテスト用の文字起こしテキストです。"
        mock_mp4_processor.process_mp4.assert_awaited_once()
        mock_az_blob_client.upload_blob.assert_awaited_once()
        mock_transcribe_service.transcribe.assert_awaited_once()
        mock_az_blob_client.delete_blob.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_process_audio_mp4_fail(self, mock_az_speech_client, mock_az_blob_client, mock_mp4_processor, mock_transcribe_service):
        """異常系: MP4処理が失敗するケース"""
        # モックの設定
        mock_mp4_processor = MagicMock(spec=MP4ProcessorService)
        mock_mp4_processor.process_mp4.side_effect = Exception("mp4 error")
        
        service = AudioProcessorService(
            az_speech_client=mock_az_speech_client,
            az_blob_client=mock_az_blob_client,
            mp4_processor=mock_mp4_processor,
            transcription_service=mock_transcribe_service
        )

        # 実行と検証
        with pytest.raises(HTTPException) as exc_info:
            await service.process_audio("dummy/path.mp4")
        assert "mp4 error" in exc_info.value.detail
        assert exc_info.value.status_code == 500

    @pytest.mark.asyncio
    async def test_process_audio_transcribe_fail(self, mock_speech_client, mock_blob_client, mock_mp4_processor):
        """異常系: 文字起こしが失敗するケース"""
        # モックの設定
        mock_transcribe_service = MagicMock(spec=TranscribeAudioService)
        mock_transcribe_service.transcribe.side_effect = Exception("transcribe error")

        service = AudioProcessorService(
            az_speech_client=mock_speech_client,
            az_blob_client=mock_blob_client,
            mp4_processor=mock_mp4_processor,
            transcription_service=mock_transcribe_service
        )

        # 実行と検証
        with pytest.raises(HTTPException) as exc_info:
            await service.process_audio("dummy/path.mp4")
        assert "transcribe error" in exc_info.value.detail
        assert exc_info.value.status_code == 500