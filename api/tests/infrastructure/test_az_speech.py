import pytest
from unittest.mock import AsyncMock
from app.infrastructure.az_speech import AzSpeechClient
from fastapi import HTTPException
import aiohttp

@pytest.fixture
def mock_session():
    return AsyncMock(spec=aiohttp.ClientSession)

@pytest.fixture
def az_speech_client(mock_session):
    return AzSpeechClient(
        session=mock_session,
        az_speech_key="fake_key",
        az_speech_endpoint="https://dummy.speech.azure.com"
    )

@pytest.mark.asyncio
async def test_create_transcription_job(az_speech_client, mock_session):
    az_speech_client._post = AsyncMock(return_value={"self": "https://dummy.job.url"})
    result = await az_speech_client.create_transcription_job("https://blob.url/audio.wav", "TestJob")
    assert result == "https://dummy.job.url"
    az_speech_client._post.assert_awaited_once()

@pytest.mark.asyncio
async def test_poll_transcription_status_success(az_speech_client):
    az_speech_client._get = AsyncMock(side_effect=[
        {"status": "Processing"},
        {"status": "Completed", "links": {"files": "https://files.url/result"}}
    ])
    result = await az_speech_client.poll_transcription_status("https://job.url", interval=0.01)
    assert result == "https://files.url/result"

@pytest.mark.asyncio
async def test_poll_transcription_status_failure(az_speech_client):
    az_speech_client._get = AsyncMock(return_value={"status": "Failed"})
    with pytest.raises(HTTPException) as exc_info:
        await az_speech_client.poll_transcription_status("https://job.url", interval=0.01)
    assert "ジョブ失敗" in str(exc_info.value.detail)

@pytest.mark.asyncio
async def test_get_transcription_result_url(az_speech_client):
    az_speech_client._get = AsyncMock(return_value={
        "values": [{"links": {"contentUrl": "https://content.url"}}]
    })
    result = await az_speech_client.get_transcription_result_url("https://files.url")
    assert result == "https://content.url"

@pytest.mark.asyncio
async def test_get_transcription_by_speaker(az_speech_client):
    az_speech_client._get = AsyncMock(return_value={
        "recognizedPhrases": [
            {
                "speaker": 1,
                "nBest": [{"display": "こんにちは、世界"}]
            }
        ]
    })
    result = await az_speech_client.get_transcription_by_speaker("https://content.url")
    expected = "[話者1]\nこんにちは、世界"
    assert result == expected

@pytest.mark.asyncio
async def test_process_full_transcription(az_speech_client):
    az_speech_client.create_transcription_job = AsyncMock(return_value="https://job.url")
    az_speech_client.poll_transcription_status = AsyncMock(return_value="https://files.url")
    az_speech_client.get_transcription_result_url = AsyncMock(return_value="https://content.url")
    az_speech_client.get_transcription_by_speaker = AsyncMock(return_value="全文テキスト")

    result = await az_speech_client.process_full_transcription("https://blob.url/audio.wav")
    assert result == "全文テキスト"
