import pytest
from unittest.mock import patch, AsyncMock
from typing import Dict, List

from app.services.text_summarization_service import TextSummarizationService
from tests.mocks.mock_az_client import MockAzOpenAIClient

class TestTextSummarizationService:
    @pytest.fixture
    def mock_az_openai_client(self) -> MockAzOpenAIClient:
        """OpenAIクライアントのモックを提供するフィクスチャ"""
        client = MockAzOpenAIClient()
        client.get_summary = AsyncMock(return_value="要約結果")
        return client

    @pytest.fixture
    def text_summarization_service(self, mock_az_openai_client: MockAzOpenAIClient) -> TextSummarizationService:
        """テスト対象のサービスインスタンスを提供するフィクスチャ"""
        return TextSummarizationService(
            az_openai_client=mock_az_openai_client,
            max_tokens=1000,
            batch_size=2
        )

    @pytest.fixture
    def test_prompt(self) -> List[Dict[str, str]]:
        """テスト用のプロンプトを提供するフィクスチャ"""
        return [{"role": "user", "content": "要約して"}]

    @pytest.fixture
    def test_chunks(self) -> Dict[str, List[str]]:
        """テスト用のチャンクデータを提供するフィクスチャ"""
        return {
            "single": ["チャンク1"],
            "multiple": ["チャンク1", "チャンク2", "チャンク3"],
            "batch": ["チャンク1", "チャンク2", "チャンク3", "チャンク4"]
        }

    async def _verify_api_calls(
        self,
        text_summarization_service: TextSummarizationService,
        expected_call_count: int,
        expected_text: str,
        expected_max_tokens: int
    ) -> None:
        """API呼び出しの検証を行うヘルパーメソッド"""
        assert text_summarization_service._az_openai_client.get_summary.call_count == expected_call_count
        text_summarization_service._az_openai_client.get_summary.assert_awaited()

    @pytest.mark.asyncio
    @patch('app.utils.chunk_splitter.split_token')
    @patch('app.utils.create_prompt.create_prompt')
    async def test_summarize_single_chunk(
        self,
        mock_generate_prompt: AsyncMock,
        mock_split_token: AsyncMock,
        text_summarization_service: TextSummarizationService,
        test_prompt: List[Dict[str, str]],
        test_chunks: Dict[str, List[str]]
    ) -> None:
        """単一チャンクの要約テスト"""
        test_text = "テストテキスト"
        mock_split_token.return_value = test_chunks["single"]
        mock_generate_prompt.return_value = test_prompt

        result = await text_summarization_service.summarize_text(test_text)

        mock_split_token.assert_called_once_with(test_text, max_tokens=1000)
        await self._verify_api_calls(text_summarization_service, 2, test_text, 1000)
        assert isinstance(result, str)

    @pytest.mark.asyncio
    @patch('app.utils.chunk_splitter.split_token')
    @patch('app.utils.create_prompt.create_prompt')
    async def test_summarize_multiple_chunks(
        self,
        mock_generate_prompt: AsyncMock,
        mock_split_token: AsyncMock,
        text_summarization_service: TextSummarizationService,
        test_prompt: List[Dict[str, str]],
        test_chunks: Dict[str, List[str]]
    ) -> None:
        """複数チャンクの要約テスト"""
        test_text = "テストテキスト" * 100
        mock_split_token.return_value = test_chunks["multiple"]
        mock_generate_prompt.return_value = test_prompt

        result = await text_summarization_service.summarize_text(test_text)

        mock_split_token.assert_called_once_with(test_text, max_tokens=1000)
        await self._verify_api_calls(text_summarization_service, 4, test_text, 1000)
        assert isinstance(result, str)

    @pytest.mark.asyncio
    @patch('app.utils.chunk_splitter.split_token')
    async def test_empty_text_raises_error(
        self,
        mock_split_token: AsyncMock,
        text_summarization_service: TextSummarizationService
    ) -> None:
        """空のテキスト入力時のエラーテスト"""
        mock_split_token.return_value = []
        
        with pytest.raises(ValueError, match="入力テキストが空です"):
            await text_summarization_service.summarize_text("")

    @pytest.mark.asyncio
    @patch('app.utils.chunk_splitter.split_token')
    @patch('app.utils.create_prompt.create_prompt')
    async def test_batch_processing(
        self,
        mock_generate_prompt: AsyncMock,
        mock_split_token: AsyncMock,
        text_summarization_service: TextSummarizationService,
        test_prompt: List[Dict[str, str]],
        test_chunks: Dict[str, List[str]]
    ) -> None:
        """バッチ処理のテスト"""
        test_text = "テストテキスト" * 100
        mock_split_token.return_value = test_chunks["batch"]
        mock_generate_prompt.return_value = test_prompt

        await text_summarization_service.summarize_text(test_text)

        await self._verify_api_calls(text_summarization_service, 5, test_text, 1000)
        mock_split_token.assert_called_once_with(test_text, max_tokens=1000)

    @pytest.mark.asyncio
    @patch('app.utils.chunk_splitter.split_token')
    @patch('app.utils.create_prompt.create_prompt')
    async def test_error_handling_in_batch(
        self,
        mock_create_prompt: AsyncMock,
        mock_split_token: AsyncMock,
        text_summarization_service: TextSummarizationService,
        test_prompt: List[Dict[str, str]],
        test_chunks: Dict[str, List[str]]
    ) -> None:
        """バッチ処理中のエラーハンドリングテスト"""
        test_text = "テストテキスト" * 100
        mock_split_token.return_value = test_chunks["single"]
        mock_create_prompt.return_value = test_prompt
        
        text_summarization_service._az_openai_client.get_summary.side_effect = Exception("API error")

        with pytest.raises(Exception, match="API error"):
            await text_summarization_service.summarize_text(test_text)
