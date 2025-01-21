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
                        "content": "あなたは親切で丁寧なアシスタントです。",
                    },
                    {
                        "role": "user",
                        "content": (
                            "以下の文章を日本語で要約し、その下に話者にラベルをつけた会話形式で表示してください。\n\n"
                            "できる限りわかりやすく丁寧に要約してください。"
                            f"対象の文章:{chunk}\n\n"
                            "フォーマット例:\n\n"
                            "要約:\n\n[ここに要約]\n\n"
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
    """
    try:
        max_tokens_per_chunk = 3000
        chunks = await split_chunks(text, max_tokens_per_chunk, encoding)
        semaphore = asyncio.Semaphore(15)  # 同時実行の制限

        # 各チャンクを非同期に処理
        summaries = await asyncio.gather(
            *(fetch_summary(chunk, client, semaphore) for chunk in chunks)
        )

        return "\n".join(summaries)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to summarize text: {str(e)}"
        )
