import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.infrastructure.az_openai import AzOpenAIClient
from fastapi import HTTPException

@pytest.fixture
def openai_client():
    return AzOpenAIClient(
        az_openai_key="fake_key",
        az_openai_endpoint="https://dummy.openai.azure.com"
    )

@pytest.mark.asyncio
async def test_get_summary_success(openai_client):
    # モックレスポンス作成
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = " これは要約結果です。 "

    # モック差し替え
    openai_client.client.chat.completions.create = AsyncMock(return_value=mock_response)

    prompt_messages = [{"role": "user", "content": "これはテストです"}]
    result = await openai_client.get_summary(prompt_messages)

    assert result == "これは要約結果です。"
    openai_client.client.chat.completions.create.assert_awaited_once()

@pytest.mark.asyncio
async def test_get_summary_failure(openai_client):
    openai_client.client.chat.completions.create = AsyncMock(side_effect=Exception("API Failure"))

    prompt_messages = [{"role": "user", "content": "エラーを出す"}]

    with pytest.raises(HTTPException) as exc_info:
        await openai_client.get_summary(prompt_messages)

    assert exc_info.value.status_code == 500
    assert "OpenAIエラー: API Failure" in str(exc_info.value.detail)
