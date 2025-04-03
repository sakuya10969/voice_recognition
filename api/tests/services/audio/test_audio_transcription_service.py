import pytest
from unittest.mock import AsyncMock
from fastapi import HTTPException

from app.services.audio.audio_transcription_service import AudioTranscriptionService
from tests.mocks.mock_az_client import MockAzSpeechClient

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
        mock_az_speech_client.get_transcription_status.assert_awaited()
        mock_az_speech_client.get_transcription_result.assert_awaited_once()
        mock_az_speech_client.get_content.assert_awaited_once()

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
    async def test_transcribe_job_failed(
        self, 
        audio_transcription_service: AudioTranscriptionService, 
        mock_az_speech_client: MockAzSpeechClient, 
        test_blob_url: str
        ):
        """異常系: 文字起こしジョブが失敗するケース"""
        mock_az_speech_client.get_transcription_status = AsyncMock(side_effect=["Running", "Failed"])
        service = AudioTranscriptionService(mock_az_speech_client)

        with pytest.raises(HTTPException) as exc_info:
            await audio_transcription_service.transcribe_audio(test_blob_url)

        assert exc_info.value.status_code == 500
        assert "文字起こしジョブが失敗しました" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_transcribe_missing_content_url(
        self, 
        audio_transcription_service: AudioTranscriptionService, 
        mock_az_speech_client: MockAzSpeechClient, 
        test_blob_url: str
        ):
        """異常系: コンテンツURLが取得できないケース"""
        mock_az_speech_client.get_transcription_result = AsyncMock(return_value={})
        audio_transcription_service = AudioTranscriptionService(mock_az_speech_client)

        with pytest.raises(HTTPException) as exc_info:
            await audio_transcription_service.transcribe_audio(test_blob_url)

        assert exc_info.value.status_code == 500
        assert "コンテンツURLを取得できませんでした" in exc_info.value.detail
