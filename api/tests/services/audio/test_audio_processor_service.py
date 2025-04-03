import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException

from app.services.audio.audio_processing_service import AudioProcessingService
from app.services.audio.mp4_processing_service import MP4ProcessingService
from app.services.audio.audio_transcription_service import AudioTranscriptionService
from tests.mocks.mock_az_client import MockAzSpeechClient, MockAzBlobClient

class TestAudioProcessingService:
    @pytest.fixture
    def mock_az_blob_client(self):
        return MockAzBlobClient()

    @pytest.fixture
    def mock_az_speech_client(self):
        return MockAzSpeechClient()

    @pytest.fixture
    def mock_mp4_processing_service(self):
        mock_mp4_processing_service = MagicMock(spec=MP4ProcessingService)
        mock_mp4_processing_service.process_mp4.return_value = {
            "file_name": "audio.wav",
            "file_data": b"fake-data"
        }
        return mock_mp4_processing_service

    @pytest.fixture
    def mock_audio_transcription_service(self):
        mock_audio_transcription_service = MagicMock(spec=AudioTranscriptionService)
        mock_audio_transcription_service.transcribe_audio.return_value = "これはテスト用の文字起こしテキストです。"
        return mock_audio_transcription_service

    @pytest.fixture
    def mock_audio_processing_service(
        self, 
        mock_az_speech_client, 
        mock_az_blob_client, 
        mock_mp4_processing_service, 
        mock_audio_transcription_service
        ):
        return AudioProcessingService(
            az_speech_client=mock_az_speech_client,
            az_blob_client=mock_az_blob_client,
            mp4_processing_service=mock_mp4_processing_service,
            audio_transcription_service=mock_audio_transcription_service
        )

    @pytest.mark.asyncio
    async def test_process_audio_success(
        self, 
        mock_audio_processing_service, 
        mock_az_blob_client, 
        mock_mp4_processing_service, 
        mock_audio_transcription_service
        ):
        """正常系: 音声処理が成功するケース"""
        # 実行
        result = await mock_audio_processing_service.process_audio("dummy/path/to/audio.mp4")

        # 検証
        assert result == "これはテスト用の文字起こしテキストです。"
        mock_mp4_processing_service.process_mp4.assert_awaited_once()
        mock_az_blob_client.upload_blob.assert_awaited_once()
        mock_audio_transcription_service.transcribe_audio.assert_awaited_once()
        mock_az_blob_client.delete_blob.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_process_audio_mp4_fail(
        self, 
        mock_az_speech_client, 
        mock_az_blob_client, 
        mock_mp4_processing_service, 
        mock_audio_transcription_service
        ):
        """異常系: MP4処理が失敗するケース"""
        # モックの設定
        mock_mp4_processing_service = MagicMock(spec=MP4ProcessingService)
        mock_mp4_processing_service.process_mp4.side_effect = Exception("mp4 error")
        
        service = AudioProcessingService(
            az_speech_client=mock_az_speech_client,
            az_blob_client=mock_az_blob_client,
            mp4_processing_service=mock_mp4_processing_service,
            audio_transcription_service=mock_audio_transcription_service
        )

        # 実行と検証
        with pytest.raises(HTTPException) as exc_info:
            await service.process_audio("dummy/path.mp4")
        assert "mp4 error" in exc_info.value.detail
        assert exc_info.value.status_code == 500

    @pytest.mark.asyncio
    async def test_process_audio_transcribe_fail(
        self, 
        mock_az_speech_client, 
        mock_az_blob_client, 
        mock_mp4_processing_service, 
        mock_audio_transcription_service
        ):
        """異常系: 文字起こしが失敗するケース"""
        # モックの設定
        mock_audio_transcription_service = MagicMock(spec=AudioTranscriptionService)
        mock_audio_transcription_service.transcribe_audio.side_effect = Exception("transcribe error")

        service = AudioProcessingService(
            az_speech_client=mock_az_speech_client,
            az_blob_client=mock_az_blob_client,
            mp4_processing_service=mock_mp4_processing_service,
            audio_transcription_service=mock_audio_transcription_service
        )

        # 実行と検証
        with pytest.raises(HTTPException) as exc_info:
            await service.process_audio("dummy/path.mp4")
        assert "transcribe error" in exc_info.value.detail
        assert exc_info.value.status_code == 500