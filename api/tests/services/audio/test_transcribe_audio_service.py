import pytest
from unittest.mock import AsyncMock
from fastapi import HTTPException

from app.services.audio.audio_transcription_service import AudioTranscriptionService
from tests.mocks.mock_az_client import MockAzSpeechClient

class TestTranscribeAudioService:
    @pytest.fixture
    def mock_az_speech_client(self):
        return MockAzSpeechClient()

    @pytest.fixture
    def service(self, mock_az_speech_client):
        return AudioTranscriptionService(mock_az_speech_client)

    @pytest.fixture
    def test_blob_url(self):
        return "https://mock.blob/audio.wav"

    @pytest.mark.asyncio
    async def test_transcribe_success(self, service, mock_az_speech_client, test_blob_url):
        """正常系: 文字起こしが成功するケース"""
        # 実行
        result = await service.transcribe_audio(test_blob_url)

        # 検証
        assert result == "これはテスト用の文字起こしテキストです。"
        mock_az_speech_client.create_transcription_job.assert_awaited_once()
        mock_az_speech_client.get_transcription_status.assert_awaited()
        mock_az_speech_client.get_transcription_result.assert_awaited_once()
        mock_az_speech_client.get_content.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_transcribe_job_failed(self, service, mock_az_speech_client, test_blob_url):
        """異常系: 文字起こしジョブが失敗するケース"""
        # モックの設定
        mock_az_speech_client.get_transcription_status = AsyncMock(side_effect=["Running", "Failed"])
        service = AudioTranscriptionService(mock_az_speech_client)

        # 実行と検証
        with pytest.raises(HTTPException) as exc_info:
            await service.transcribe_audio(test_blob_url)

        assert exc_info.value.status_code == 500
        assert "文字起こしジョブが失敗しました" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_transcribe_missing_content_url(self, service, mock_az_speech_client, test_blob_url):
        """異常系: コンテンツURLが取得できないケース"""
        # モックの設定
        mock_az_speech_client.get_transcription_result = AsyncMock(return_value={})
        service = AudioTranscriptionService(mock_az_speech_client)

        # 実行と検証
        with pytest.raises(HTTPException) as exc_info:
            await service.transcribe_audio(test_blob_url)

        assert exc_info.value.status_code == 500
        assert "コンテンツURLを取得できませんでした" in exc_info.value.detail
