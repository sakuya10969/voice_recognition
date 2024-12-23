from fastapi import HTTPException
import os
from openai import AsyncAzureOpenAI
from pathlib import Path
from dotenv import load_dotenv
import asyncio
import tiktoken

env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)

client = AsyncAzureOpenAI(
    api_key=os.getenv("AZ_OPENAI_KEY"),
    azure_endpoint=os.getenv("AZ_OPENAI_ENDPOINT"),
    api_version="2024-02-01",
)

encoding = tiktoken.encoding_for_model("gpt-4o")


def split_chunks(text, max_tokens, encoding):
    """テキストをトークン数に基づいて分割"""
    tokens = encoding.encode(text)
    return [
        encoding.decode(tokens[i : i + max_tokens])
        for i in range(0, len(tokens), max_tokens)
    ]


async def fetch_summary(chunk, client, semaphore):
    """各チャンクをGPTモデルに投げて要約を取得する"""
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
                            "以下の文章を日本語で要約し、その下に話者にラベルをつけた会話形式で表示してください。"
                            "すべての出力を日本語で書いてください。英語が含まれている場合は日本語に翻訳してください。\n\n"
                            f"対象の文章:{chunk}\n\n"
                            "フォーマット例:\n\n"
                            "要約:\n[ここに要約]\n\n"
                            "会話形式:\n\n"
                            "話者A: [ここに話者Aの発言]\n\n"
                            "話者B: [ここに話者Bの発言]\n\n"
                        ),
                    },
                ],
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"エラー: {e}"


async def summarize_text(text):
    """メイン要約関数"""
    encoding = tiktoken.encoding_for_model("gpt-4o")
    max_tokens_per_chunk = 3000
    chunks = split_chunks(text, max_tokens_per_chunk, encoding)
    semaphore = asyncio.Semaphore(15)

    summaries = await asyncio.gather(
        *(fetch_summary(chunk, client, semaphore) for chunk in chunks),
    )

    return "\n".join(summaries)
