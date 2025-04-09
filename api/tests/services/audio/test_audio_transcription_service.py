import pytest
from unittest.mock import AsyncMock
from fastapi import HTTPException

from app.services.audio.audio_transcription_service import AudioTranscriptionService
from tests.mocks.mock_az_client import MockAzSpeechClient, MockAzSpeechResponse

class TestAudioTranscriptionService:
    @pytest.fixture
    def mock_az_speech_client(self):
        """Azure Speech Clientのモックを提供するフィクスチャ"""
        return MockAzSpeechClient()

    @pytest.fixture
    def audio_transcription_service(self, mock_az_speech_client: MockAzSpeechClient):
        """テスト対象のサービスインスタンスを提供するフィクスチャ"""
        return AudioTranscriptionService(mock_az_speech_client)

    @pytest.fixture
    def test_blob_url(self):
        """テスト用のBlob URLを提供するフィクスチャ"""
        return "https://mock.blob/audio.wav"

    async def _verify_transcription_calls(self, mock_az_speech_client: MockAzSpeechClient):
        """文字起こし関連のAPI呼び出しを検証するヘルパーメソッド"""
        mock_az_speech_client.create_transcription_job.assert_awaited_once()
        mock_az_speech_client.poll_transcription_status.assert_awaited_once()
        mock_az_speech_client.get_transcription_result.assert_awaited_once()
        mock_az_speech_client.get_transcription_display.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_transcribe_success(
        self, 
        audio_transcription_service: AudioTranscriptionService, 
        mock_az_speech_client: MockAzSpeechClient, 
        test_blob_url: str
    ):
        """正常系: 文字起こしが成功するケース"""
        result = await audio_transcription_service.transcribe_audio(test_blob_url)

        assert result == "これはテスト用の文字起こしテキストです。"
        await self._verify_transcription_calls(mock_az_speech_client)

    @pytest.mark.asyncio
    async def test_transcribe_failure(
        self, 
        audio_transcription_service: AudioTranscriptionService, 
        mock_az_speech_client: MockAzSpeechClient, 
        test_blob_url: str
    ):
        """異常系: 文字起こし処理が失敗するケース"""
        mock_az_speech_client.create_transcription_job = AsyncMock(side_effect=Exception("API Error"))

        with pytest.raises(HTTPException) as exc_info:
            await audio_transcription_service.transcribe_audio(test_blob_url)

        assert exc_info.value.status_code == 500
        assert "文字起こしに失敗しました" in exc_info.value.detail
        mock_az_speech_client.create_transcription_job.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_transcribe_with_custom_response(
        self, 
        test_blob_url: str
    ):
        """正常系: カスタムレスポンスを使用した文字起こし"""
        custom_response = MockAzSpeechResponse(
            display_text="カスタムテキスト"
        )
        mock_client = MockAzSpeechClient(custom_response)
        service = AudioTranscriptionService(mock_client)

        result = await service.transcribe_audio(test_blob_url)

        assert result == "カスタムテキスト"
        mock_client.create_transcription_job.assert_awaited_once()
        mock_client.poll_transcription_status.assert_awaited_once()
        mock_client.get_transcription_result.assert_awaited_once()
        mock_client.get_transcription_display.assert_awaited_once()
