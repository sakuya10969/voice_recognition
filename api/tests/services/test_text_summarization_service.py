import pytest
from unittest.mock import patch, AsyncMock

from app.services.text_summarization_service import TextSummarizationService
from tests.mocks.mock_az_client import MockAzOpenAIClient

class TestTextSummarizationService:
    @pytest.fixture
    def mock_az_openai_client(self):
        """OpenAIクライアントのモックを提供するフィクスチャ"""
        mock_az_openai_client = MockAzOpenAIClient()
        mock_az_openai_client.get_summary = AsyncMock(return_value="要約結果")
        return mock_az_openai_client

    @pytest.fixture
    def mock_text_summarization_service(self, mock_az_openai_client):
        """テスト対象のサービスインスタンスを提供するフィクスチャ"""
        return TextSummarizationService(
            az_openai_client=mock_az_openai_client,
            max_tokens=1000,
            batch_size=2
        )

    @pytest.fixture
    def mock_prompt(self):
        """テスト用のプロンプトを提供するフィクスチャ"""
        return [{"role": "user", "content": "要約して"}]

    @pytest.fixture
    def mock_chunks(self):
        """テスト用のチャンクデータを提供するフィクスチャ"""
        return {
            "single": ["チャンク1"],
            "multiple": ["チャンク1", "チャンク2", "チャンク3"],
            "batch": ["チャンク1", "チャンク2", "チャンク3", "チャンク4"]
        }

    async def _verify_summary_call_count(self, mock_text_summarization_service, expected_count):
        """要約APIの呼び出し回数を検証するヘルパーメソッド"""
        assert mock_text_summarization_service._az_openai_client.get_summary.call_count == expected_count

    @pytest.mark.asyncio
    @patch('app.utils.chunk_splitter.split_token')
    @patch('app.utils.create_prompt.create_prompt')
    async def test_summarize_single_chunk(
        self, 
        mock_create_prompt, 
        mock_split_token, 
        mock_text_summarization_service, 
        mock_az_openai_client, 
        mock_prompt, mock_chunks
        ):
        """単一チャンクの要約テスト"""
        test_text = "テストテキスト"
        mock_split_token.return_value = mock_chunks["single"]
        mock_create_prompt.return_value = mock_prompt

        result = await mock_text_summarization_service.summarize_text(test_text)

        mock_split_token.assert_called_once_with(test_text, max_tokens=1000)
        await self._verify_summary_call_count(mock_text_summarization_service, 2)
        assert isinstance(result, str)

    @pytest.mark.asyncio
    @patch('app.utils.chunk_splitter.split_token')
    @patch('app.utils.create_prompt.create_prompt')
    async def test_summarize_multiple_chunks(
        self, 
        mock_create_prompt, 
        mock_split_token,
        mock_text_summarization_service, 
        mock_az_openai_client,
        mock_prompt, mock_chunks
        ):
        """複数チャンクの要約テスト"""
        test_text = "テストテキスト" * 100
        mock_split_token.return_value = mock_chunks["multiple"]
        mock_create_prompt.return_value = mock_prompt

        result = await mock_text_summarization_service.summarize_text(test_text)

        mock_split_token.assert_called_once_with(test_text, max_tokens=1000)
        await self._verify_summary_call_count(mock_text_summarization_service, 4)
        assert isinstance(result, str)

    @pytest.mark.asyncio
    @patch('app.utils.chunk_splitter.split_token')
    async def test_empty_text_raises_error(self, mock_split_token, mock_text_summarization_service):
        """空のテキスト入力時のエラーテスト"""
        mock_split_token.return_value = []
        
        with pytest.raises(ValueError, match="入力テキストが空です"):
            await mock_text_summarization_service.summarize_text("")

    @pytest.mark.asyncio
    @patch('app.utils.chunk_splitter.split_token')
    @patch('app.utils.create_prompt.create_prompt')
    async def test_batch_processing(
        self, 
        mock_create_prompt, 
        mock_split_token,
        mock_text_summarization_service, 
        mock_az_openai_client,
        mock_prompt, 
        mock_chunks
        ):
        """バッチ処理のテスト"""
        test_text = "テストテキスト" * 100
        mock_split_token.return_value = mock_chunks["batch"]
        mock_create_prompt.return_value = mock_prompt

        await mock_text_summarization_service.summarize_text(test_text)

        await self._verify_summary_call_count(mock_text_summarization_service, 5)
        mock_split_token.assert_called_once_with(test_text, max_tokens=1000)

    @pytest.mark.asyncio
    @patch('app.utils.chunk_splitter.split_token')
    @patch('app.utils.create_prompt.create_prompt')
    async def test_error_handling_in_batch(
        self, 
        mock_create_prompt, 
        mock_split_token,
        mock_text_summarization_service, 
        mock_prompt,
        mock_chunks
        ):
        """バッチ処理中のエラーハンドリングテスト"""
        test_text = "テストテキスト" * 100
        mock_split_token.return_value = mock_chunks["single"]
        mock_create_prompt.return_value = mock_prompt
        
        mock_text_summarization_service._az_openai_client.get_summary.side_effect = Exception("API error")

        with pytest.raises(Exception, match="API error"):
            await mock_text_summarization_service.summarize_text(test_text)
