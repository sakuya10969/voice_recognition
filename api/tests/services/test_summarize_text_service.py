import pytest
from unittest.mock import patch

from app.services.summarize_text_service import SummarizeTextService
from tests.mocks.mock_az_client import MockAzOpenAIClient

class TestSummarizeTextService:
    @pytest.fixture
    def mock_az__openai_client(self):
        return MockAzOpenAIClient()

    @pytest.fixture
    def service(self, mock_az_openai_client):
        return SummarizeTextService(
            az_openai_client=mock_az_openai_client,
            max_tokens=1000,
            batch_size=2
        )

    @pytest.fixture
    def mock_prompt(self):
        return [{"role": "user", "content": "要約して"}]

    @pytest.mark.asyncio
    @patch('app.utils.chunk_splitter.split_token')
    @patch('app.utils.create_prompt.create_prompt')
    async def test_summarize_single_chunk(self, mock_create_prompt, mock_split_token, service, mock_az_openai_client, mock_prompt):
        """単一チャンクの要約テスト"""
        test_text = "テストテキスト"
        mock_split_token.return_value = ["チャンク1"]
        mock_create_prompt.return_value = mock_prompt

        result = await service.summarize_text(test_text)

        mock_split_token.assert_called_once_with(test_text, max_tokens=1000)
        assert mock_az_openai_client.get_summary.call_count == 2
        assert isinstance(result, str)

    @pytest.mark.asyncio
    @patch('app.utils.chunk_splitter.split_token')
    @patch('app.utils.create_prompt.create_prompt')
    async def test_summarize_multiple_chunks(self, mock_create_prompt, mock_split_token, service, mock_az_openai_client, mock_prompt):
        """複数チャンクの要約テスト"""
        test_text = "テストテキスト" * 100
        mock_split_token.return_value = ["チャンク1", "チャンク2", "チャンク3"]
        mock_create_prompt.return_value = mock_prompt

        result = await service.summarize_text(test_text)

        mock_split_token.assert_called_once_with(test_text, max_tokens=1000)
        assert mock_az_openai_client.get_summary.call_count == 4
        assert isinstance(result, str)

    @pytest.mark.asyncio
    @patch('app.utils.chunk_splitter.split_token')
    async def test_empty_text_raises_error(self, mock_split_token, service):
        """空のテキスト入力時のエラーテスト"""
        mock_split_token.return_value = []
        
        with pytest.raises(ValueError, match="入力テキストが空です"):
            await service.summarize_text("")

    @pytest.mark.asyncio
    @patch('app.utils.chunk_splitter.split_token')
    @patch('app.utils.create_prompt.create_prompt')
    async def test_batch_processing(self, mock_create_prompt, mock_split_token, service, mock_az_openai_client, mock_prompt):
        """バッチ処理のテスト"""
        test_text = "テストテキスト" * 100
        mock_split_token.return_value = ["チャンク1", "チャンク2", "チャンク3", "チャンク4"]
        mock_create_prompt.return_value = mock_prompt

        await service.summarize_text(test_text)

        assert mock_az_openai_client.get_summary.call_count == 5
        mock_split_token.assert_called_once_with(test_text, max_tokens=1000)

    @pytest.mark.asyncio
    @patch('app.utils.chunk_splitter.split_token')
    @patch('app.utils.create_prompt.create_prompt')
    async def test_error_handling_in_batch(self, mock_create_prompt, mock_split_token, service, mock_prompt):
        """バッチ処理中のエラーハンドリングテスト"""
        test_text = "テストテキスト" * 100
        mock_split_token.return_value = ["チャンク1", "チャンク2"]
        mock_create_prompt.return_value = mock_prompt
        
        service._az_openai_client.get_summary.side_effect = Exception("API error")

        with pytest.raises(Exception, match="API error"):
            await service.summarize_text(test_text)
