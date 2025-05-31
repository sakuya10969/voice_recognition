import asyncio
from typing import List

from app.infrastructure.az_openai import AzOpenAIClient
from app.utils.token_chunking import split_token
from app.utils.prompt_generating import generate_prompt


class TextSummarizationService:
    """テキストを要約するサービス"""
    def __init__(
        self,
        az_openai_client: AzOpenAIClient,
        max_tokens: int = 7500,
        batch_size: int = 5,
    ):
        self._az_openai_client = az_openai_client
        self.max_tokens = max_tokens
        self.batch_size = batch_size

    async def summarize_text(self, text: str) -> str:
        """
        テキストを要約する。チャンク分割、バッチ要約、最終要約まで一気通貫で行う。
        """
        chunks = self._split_text_chunks(text)
        chunk_summaries = await self._summarize_chunks_in_batches(chunks)
        return await self._summarize_final(chunk_summaries)

    def _split_text_chunks(self, text: str) -> List[str]:
        """テキストをトークン数に基づいてチャンクに分割する"""
        chunks = split_token(text, max_tokens=self.max_tokens)
        if not chunks:
            raise ValueError("入力テキストが空です")
        return chunks

    async def _summarize_chunks_in_batches(self, chunks: List[str]) -> List[str]:
        """チャンクごとにプロンプトを生成し、バッチで要約する"""
        prompts = [generate_prompt(chunk) for chunk in chunks]
        summaries: List[str] = []
        for i in range(0, len(prompts), self.batch_size):
            batch = prompts[i : i + self.batch_size]
            tasks = [self._az_openai_client.get_summary(prompt) for prompt in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            summaries.extend([r for r in results if isinstance(r, str)])
        return summaries

    async def _summarize_final(self, chunk_summaries: List[str]) -> str:
        """チャンク要約をまとめて最終要約を生成"""
        combined_text = "\n".join(chunk_summaries)
        final_prompt = generate_prompt(combined_text)
        return await self._az_openai_client.get_summary(final_prompt)
