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

    def split_chunks(self, text: str, max_tokens: int = 7500) -> list:
        """
        テキストをトークン数で分割し、最大トークン数を超えないようにする。
        """
        words = text.split()
        chunks = []
        current_chunk = []
        current_tokens = 0
        for word in words:
            word_tokens = len(self.encoding.encode(word))

            if current_tokens + word_tokens > max_tokens:
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_tokens = word_tokens
            else:
                current_chunk.append(word)
                current_tokens += word_tokens
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        return chunks

    async def fetch_summary(self, chunk: str) -> str:
        """
        GPTモデルにチャンクを投げて要約を取得。
        """
        async with self.semaphore:
            try:
                response = await self.client.chat.completions.create(
                    model="gpt-4o",
                    max_tokens=4000,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "あなたは、会議の議事録を作成するプロフェッショナルなアシスタントです。\n\n"
                                "あなたの役割は、ユーザーが提供した音声の文字起こし結果を適切に要約し、"
                                "わかりやすく整理された文章を生成することです。\n\n"
                                "以下のフォーマットで出力してください。\n"
                                "[文字起こし結果]\n"
                                f"{chunk}\n"
                                "[要約結果]\n"
                                "- （要約された内容）\n"
                                "- （補足情報があれば適宜記載）\n"
                            ),
                        },
                        {
                            "role": "user",
                            "content": (
                                f"以下の文章を要約してください。\n\n{chunk}\n\n"
                                "以下のフォーマットで出力してください。\n\n"
                                "[文字起こし結果]\n"
                                f"{chunk}\n\n"
                                "[要約結果]\n"
                                "-（要約された内容）\n"
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
