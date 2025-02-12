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
        max_concurrent_requests: int = 15,
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

    def split_chunks(self, text: str, max_tokens: int = 3000) -> list:
        """
        テキストを段落ごとに分割し、最大トークン数を超えないようにする。
        """
        paragraphs = re.split(r"\n+", text.strip())  # 段落単位で分割
        chunks = []
        current_chunk = ""

        for paragraph in paragraphs:
            if len(self.encoding.encode(current_chunk + paragraph)) > max_tokens:
                chunks.append(current_chunk.strip())  # 既存のチャンクを保存
                current_chunk = paragraph  # 新しいチャンク開始
            else:
                current_chunk += "\n" + paragraph  # チャンクに追加

        if current_chunk:
            chunks.append(current_chunk.strip())  # 最後のチャンクを追加

        return chunks

    async def fetch_summary(self, chunk: str) -> str:
        """
        GPTモデルにチャンクを投げて要約を取得。
        """
        async with self.semaphore:
            try:
                response = await self.client.chat.completions.create(
                    model="gpt-4o",
                    max_tokens=1000,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "あなたは会議の議事録を作成するプロフェッショナルなアシスタントです。"
                                "重複した情報を省略し、重要な議題、参加者の意見、具体的なアイデア、結論を詳細に記録してください。"
                                "過去のチャンクと重複する内容がある場合、簡潔に記載し、繰り返しを避けてください。"
                            ),
                        },
                        {
                            "role": "user",
                            "content": (
                                "あなたは会議の議事録を作成するプロフェッショナルなアシスタントです。\n\n"
                                "以下の文章を要約してください。ただし、単なる短縮ではなく、できる限り詳細な情報を保持し、"
                                "議論の流れや具体的な発言を正確に記録してください。\n\n"
                                "【要件】\n"
                                "- 重要なポイントや意見を漏らさずに記録し、詳細な文脈を維持する。\n"
                                "- 単なる箇条書きではなく、読みやすく自然な文章にする。\n"
                                "- 具体的な提案・アイデア・数値・発言があれば、それを正確に残す。\n"
                                "- 重複する情報は適切に整理し、過剰な繰り返しを避ける。\n"
                                "- 会話の流れが分かるように、前後関係を意識して書く。\n"
                                "- もし明確な結論や次のアクションが示された場合、それを分かりやすくまとめる。\n\n"
                                f"対象の文章:\n{chunk}\n\n"
                                "【出力の指示】\n"
                                "- フォーマットは自由。ただし、会議の流れを分かりやすくするため、自然な文章で記述。\n"
                                "- 必要に応じて、発言者の意見や重要なポイントを適宜整理。\n"
                                "- 要約ではあるが、可能な限り詳細に。\n"
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
            results.extend(await asyncio.gather(*batch))
        return results

    async def summarize_text(self, text: str, max_tokens_per_chunk: int = 3000) -> str:
        """
        文章を要約し、最終的に統合して整理する。
        """
        try:
            # チャンクに分割
            chunks = self.split_chunks(text, max_tokens_per_chunk)
            print("分割されたチャンク:", chunks)

            # 非同期タスクを生成
            tasks = [self.fetch_summary(chunk) for chunk in chunks]
            print("処理するタスクの数:", len(tasks))

            # バッチ処理でタスクを実行
            summaries = await self.run_in_batches(tasks, batch_size=15)
            print("個別の要約:", summaries)

            # **最終統合処理**
            final_summary = await self.fetch_summary("\n".join(summaries))
            print("最終要約:", final_summary)

            return final_summary
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to summarize text: {str(e)}"
            )
