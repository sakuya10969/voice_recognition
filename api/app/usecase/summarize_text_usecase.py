import asyncio
from typing import List
from fastapi import HTTPException
from infrastructure.az_openai import AzOpenAIClient
from utils.chunk_splitter import split_token
from utils.create_prompt import create_prompt

class SummarizeTextUseCase:
    def __init__(self, summarizer: AzOpenAIClient):
        self.summarizer = summarizer
        self.max_tokens = 7500
        self.batch_size = 5

    async def execute(self, text: str) -> str:
        try:
            # テキストをチャンクに分割
            chunks = split_token(text, max_tokens=self.max_tokens)
            if not chunks:
                raise ValueError("入力テキストが空です")

            # 各チャンクの要約を並列処理
            chunk_summaries = await self._summarize_chunks(chunks)
            if not chunk_summaries:
                raise ValueError("要約の生成に失敗しました")

            # 最終要約の生成
            return await self._create_final_summary(chunk_summaries)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"テキスト要約中にエラーが発生しました: {str(e)}"
            )

    async def _summarize_chunks(self, chunks: List[str]) -> List[str]:
        prompts = [create_prompt(chunk) for chunk in chunks]
        return await self._run_in_batches(prompts)

    async def _create_final_summary(self, summaries: List[str]) -> str:
        combined_text = "\n".join(summaries)
        final_prompt = create_prompt(combined_text)
        return await self.summarizer.fetch_summary(final_prompt)

    async def _run_in_batches(self, prompts: List[List[dict]]) -> List[str]:
        summaries = []
        for i in range(0, len(prompts), self.batch_size):
            batch = prompts[i:i + self.batch_size]
            tasks = [self.summarizer.fetch_summary(prompt) for prompt in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            valid_results = [r for r in results if isinstance(r, str)]
            if valid_results:
                summaries.extend(valid_results)
            
        return summaries
