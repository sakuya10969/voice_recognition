import pytest
from unittest.mock import AsyncMock
from fastapi import HTTPException

from app.services.audio.transcribe_audio_service import TranscribeAudioService
from tests.mocks.az_client_mock import MockAzSpeechClient

class TestTranscribeAudioService:
    @pytest.fixture
    def mock_client(self):
        return MockAzSpeechClient()

    @pytest.fixture
    def service(self, mock_client):
        return TranscribeAudioService(mock_client)

    @pytest.fixture
    def test_blob_url(self):
        return "https://mock.blob/audio.wav"

    @pytest.mark.asyncio
    async def test_transcribe_success(self, service, mock_client, test_blob_url):
        """正常系: 文字起こしが成功するケース"""
        # 実行
        result = await service.transcribe(test_blob_url)

        # 検証
        assert result == "これはテスト用の文字起こしテキストです。"
        mock_client.create_transcription_job.assert_awaited_once()
        mock_client.get_transcription_status.assert_awaited()
        mock_client.get_transcription_result.assert_awaited_once()
        mock_client.get_content.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_transcribe_job_failed(self, mock_client, test_blob_url):
        """異常系: 文字起こしジョブが失敗するケース"""
        # モックの設定
        mock_client.get_transcription_status = AsyncMock(side_effect=["Running", "Failed"])
        service = TranscribeAudioService(mock_client)

        # 実行と検証
        with pytest.raises(HTTPException) as exc_info:
            await service.transcribe(test_blob_url)

        assert exc_info.value.status_code == 500
        assert "文字起こしジョブが失敗しました" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_transcribe_missing_content_url(self, mock_client, test_blob_url):
        """異常系: コンテンツURLが取得できないケース"""
        # モックの設定
        mock_client.get_transcription_result = AsyncMock(return_value={})
        service = TranscribeAudioService(mock_client)

        # 実行と検証
        with pytest.raises(HTTPException) as exc_info:
            await service.transcribe(test_blob_url)

        assert exc_info.value.status_code == 500
        assert "コンテンツURLを取得できませんでした" in exc_info.value.detail
