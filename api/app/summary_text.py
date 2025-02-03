import asyncio
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
        self.semaphore = asyncio.Semaphore(
            max_concurrent_requests
        )  # 同時リクエスト数を制限

    async def split_chunks(self, text: str, max_tokens: int) -> list:
        """
        テキストをトークン数に基づいて分割。
        """
        tokens = self.encoding.encode(text)
        return [
            self.encoding.decode(tokens[i : i + max_tokens])
            for i in range(0, len(tokens), max_tokens)
        ]

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
                                "あなたは会議動画を分析し、議事録を作成するプロフェッショナルなアシスタントです。"
                                "動画の会話内容を正確に捉え、重要な議題、参加者の意見、具体的なアイデア、結論を詳細に記録してください。"
                                "簡潔すぎる要約は避け、内容の濃さを保ちながら、読みやすい日本語で整理してください。"
                            ),
                        },
                        {
                            "role": "user",
                            "content": (
                                "以下の文章を日本語でわかりやすく要約してください。\n\n"
                                "もしすでに適切なフォーマット（「【会議概要】」など）がある場合は、そのまま出力してください。\n"
                                "フォーマットがない場合は、以下の点を守ってください:\n"
                                "1. 議題の重要なポイント、内容、結論を記載してください。\n"
                                "2. 具体的な数値や提案が含まれる場合、それを省略せずに記載してください。\n"
                                "3. 読みやすさを保ちながら、内容は十分に詳細にしてください。\n\n"
                                f"対象の文章:\n{chunk}\n\n"
                                "出力フォーマット例:\n"
                                "【会議概要】\n"
                                "[会議の全体的な概要を記載]\n\n"
                                "【議題】\n"
                                "内容: [議論の内容を詳細に記載]\n"
                                "結論: [議題の結論を記載]\n\n"
                                "【結論】\n"
                                "[会議全体の結論を記載]"
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
        try:
            # テキストをチャンクに分割
            chunks = await self.split_chunks(text, max_tokens_per_chunk)
            print("分割されたチャンク:", chunks)  # チャンクのリストを表示
            # 非同期タスクを生成
            tasks = [self.fetch_summary(chunk) for chunk in chunks]
            print("処理するタスクの数:", len(tasks))
            # バッチ処理でタスクを実行
            summaries = await self.run_in_batches(tasks, batch_size=15)
            print("要約のリスト:", summaries)  # 取得された要約を表示
            return "\n".join(summaries)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to summarize text: {str(e)}")

