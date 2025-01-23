import os
import asyncio
from openai import AsyncAzureOpenAI
from dotenv import load_dotenv
import tiktoken
from fastapi import HTTPException

# 環境変数のロード
load_dotenv()

# OpenAIクライアントの初期化
client = AsyncAzureOpenAI(
    api_key=os.getenv("AZ_OPENAI_KEY"),
    azure_endpoint=os.getenv("AZ_OPENAI_ENDPOINT"),
    api_version="2024-02-01",
)

# エンコーディングの初期化
encoding = tiktoken.encoding_for_model("gpt-4o")

async def split_chunks(text: str, max_tokens: int, encoding: tiktoken.Encoding) -> list:
    """
    テキストをトークン数に基づいて分割する関数。
    """
    tokens = encoding.encode(text)
    return [
        encoding.decode(tokens[i : i + max_tokens])
        for i in range(0, len(tokens), max_tokens)
    ]

async def fetch_summary(chunk: str, client: AsyncAzureOpenAI, semaphore: asyncio.Semaphore) -> str:
    """
    各チャンクをGPTモデルに投げて要約を取得する非同期関数。
    """
    async with semaphore:
        try:
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "あなたは会議動画を分析し、議事録を作成するプロフェッショナルなアシスタントです。"
                            "動画の会話内容を正確に捉え、重要な議題、参加者の意見、具体的なアイデア、結論を詳細に記録してください。"
                            "簡潔すぎる要約は避け、内容の濃さを保ちながら、読みやすい日本語で整理してください。"
                            "また、議論の背景や具体的な数値、提案が含まれる場合は省略せず、必ず記載してください。"
                        ),
                    },
                    {
                        "role": "user",
                        "content": (
                            "以下の文章を日本語でわかりやすく要約してください。\n\n"
                            "必ず以下の点を守ってください:\n"
                            "1. 議題ごとに重要なポイント、議論の内容、結論を記載してください。\n"
                            "2. 具体的な数値や提案が含まれる場合、それを省略せずに記載してください。\n"
                            "3. 読みやすさを保ちながら、内容は十分に詳細にしてください。\n\n"
                            f"対象の文章:\n{chunk}\n\n"
                            "出力フォーマット例:\n"
                            "【会議概要】\n"
                            "[会議の全体的な概要を一文で記載]\n\n"
                            "【議題1】\n"
                            "内容: [議論の内容を詳細に記載]\n"
                            "結論: [議題の結論を記載]\n\n"
                            "【議題2】\n"
                            "内容: [議論の内容を詳細に記載]\n"
                            "結論: [議題の結論を記載]\n\n"
                            "【結論】\n"
                            "[会議全体の結論を一文で記載]"
                        ),
                    },
                ],
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"エラー: {str(e)}")


async def summarize_text(text: str) -> str:
    """
    メイン要約関数。
    テキストをチャンク分けし、非同期で要約を取得。
    各チャンクごとの要約をリスト形式で返す。
    """
    try:
        # 1チャンクあたりの最大トークン数
        max_tokens_per_chunk = 3000
        # チャンク分割
        chunks = await split_chunks(text, max_tokens_per_chunk, encoding)
        # セマフォで同時処理数を制限（非同期タスクの数を制御）
        semaphore = asyncio.Semaphore(15)
        # 各チャンクを非同期で要約取得
        summaries = await asyncio.gather(*(fetch_summary(chunk, client, semaphore) for chunk in chunks))
        return "\n".join(summaries)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to summarize text: {str(e)}")
