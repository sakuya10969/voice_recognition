import asyncio
import re
from openai import AsyncAzureOpenAI
import tiktoken
from fastapi import HTTPException


class AzOpenAIClient:
    def __init__(
        self,
        az_openai_key: str,
        az_openai_endpoint: str,
        api_version: str = "2024-02-01",
        max_concurrent_requests: int = 10,
    ):
        """
        OpenAI サマライズ用クラスの初期化。
        """
        self.client = AsyncAzureOpenAI(
            api_key=az_openai_key,
            azure_endpoint=az_openai_endpoint,
            api_version=api_version,
        )
        self.encoding = tiktoken.encoding_for_model("gpt-4o")
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)

    def split_chunks(self, text: str, max_tokens: int = 6000) -> list:
        """
        トークン単位で分割し、最大トークン数を超えないようにする。
        """
        tokens = self.encoding.encode(text)  # **全文を一括でエンコード**
        chunks = []
        # **max_tokens ごとにスライスして分割**
        for i in range(0, len(tokens), max_tokens):
            chunk_tokens = tokens[i : i + max_tokens]
            chunk_text = self.encoding.decode(chunk_tokens)  # **トークンを文字列に戻す**
            chunks.append(chunk_text)
        return chunks

    async def fetch_summary(self, chunk: str) -> str:
        """
        GPTモデルにチャンクを投げて要約を取得。
        """
        async with self.semaphore:
            try:
                response = await self.client.chat.completions.create(
                    model="gpt-4o",
                    max_tokens=3000,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "あなたは、会議の議事録を作成するプロフェッショナルなアシスタントです。\n\n"
                                "ユーザーが提供した音声の文字起こし結果を、わかりやすく整理し、詳細に要約してください。\n"
                                "話者を識別し、議論の流れを整理して要点を明確にしてください。\n"
                                "要約は必ず日本語で出力してください。\n"
                            ),
                        },
                        {
                            "role": "user",
                            "content": (
                                "下記の文字起こし結果から議事録を作成してください。\n"
                                "決定事項、残タスク、議事録詳細の順に並べてください。\n"
                                f"議事録詳細は比較的詳細目に書いてください。\n\n{chunk}"
                            ),
                        },
                    ],
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"エラー: {str(e)}")

    async def run_in_batches(self, tasks: list, batch_size: int = 5) -> list:
        """
        非同期タスクをバッチごとに実行。
        """
        results = []
        for i in range(0, len(tasks), batch_size):
            batch = tasks[i : i + batch_size]
            batch_results = await asyncio.gather(*batch, return_exceptions=True)
            for result in batch_results:
                if isinstance(result, Exception):
                    print(f"エラー発生: {result}")  # エラーハンドリング
                    continue
                results.append(result)
        return results

    async def summarize_text(
        self, text: str, max_tokens_per_chunk: int = 7500
    ) -> str:
        """
        文章を要約し、最終的に統合して整理する。
        フロントエンドには「要約済みの1つのテキスト」を返す。
        """
        try:
            # **チャンク分割**
            chunks = self.split_chunks(text, max_tokens_per_chunk)
            # **並列で要約を取得**
            tasks = [self.fetch_summary(chunk) for chunk in chunks]
            summaries = await self.run_in_batches(tasks, batch_size=5)
            # **要約を統合（最終要約）**
            final_summary = await self.fetch_summary("\n".join(summaries))
            return final_summary  # **フロントエンドには統合後の1つのテキストを返す**
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to summarize text: {str(e)}"
            )
