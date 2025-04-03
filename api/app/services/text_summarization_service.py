import asyncio
from typing import List

from app.infrastructure.az_openai import AzOpenAIClient
from app.utils.token_chunking import split_token
from app.utils.prompt_generating import generate_prompt

class TextSummarizationService:
    def __init__(self, az_openai_client: AzOpenAIClient, max_tokens: int = 7500, batch_size: int = 5):
        self._az_openai_client = az_openai_client
        self.max_tokens = max_tokens
        self.batch_size = batch_size

    async def summarize_text(self, text: str) -> str:
        """テキストを要約する"""
        chunks = self._split_text_chunks(text)
        chunk_summaries = await self._summarize_chunks(chunks)
        return await self._create_final_summary(chunk_summaries)

    def _split_text_chunks(self, text: str) -> List[str]:
        """テキストをトークン数に基づいてチャンクに分割する"""
        chunks = split_token(text, max_tokens=self.max_tokens)
        if not chunks:
            raise ValueError("入力テキストが空です")
        return chunks

    async def _summarize_chunks(self, chunks: List[str]) -> List[str]:
        """各チャンクを要約する"""
        prompts = [generate_prompt(chunk) for chunk in chunks]
        return await self._process_batches(prompts)

    async def _process_batches(self, prompts: List[List[dict]]) -> List[str]:
        """プロンプトをバッチ処理で要約する"""
        summaries = []
        for i in range(0, len(prompts), self.batch_size):
            batch = prompts[i:i + self.batch_size]
            batch_summaries = await self._process_batch(batch)
            summaries.extend(batch_summaries)
        return summaries

    async def _process_batch(self, batch: List[List[dict]]) -> List[str]:
        """バッチ単位で要約を実行する"""
        tasks = [self._az_openai_client.get_summary(prompt) for prompt in batch]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [r for r in results if isinstance(r, str)]

    async def _create_final_summary(self, chunk_summaries: List[str]) -> str:
        """チャンク要約を結合して最終的な要約を生成する"""
        combined_text = "\n".join(chunk_summaries)
        final_prompt = generate_prompt(combined_text)
        return await self._az_openai_client.get_summary(final_prompt)
