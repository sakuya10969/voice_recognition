import os
import asyncio
from openai import AsyncAzureOpenAI
from pathlib import Path
from dotenv import load_dotenv
import tiktoken

# 環境変数のロード
env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)

# OpenAIクライアントの初期化
client = AsyncAzureOpenAI(
    api_key=os.getenv("AZ_OPENAI_KEY"),
    azure_endpoint=os.getenv("AZ_OPENAI_ENDPOINT"),
    api_version="2024-02-01",
)

# エンコーディングの初期化
encoding = tiktoken.encoding_for_model("gpt-4o")


def split_chunks(text, max_tokens, encoding):
    """
    テキストをトークン数に基づいて分割する関数。

    :param text: 入力テキスト
    :param max_tokens: 各チャンクの最大トークン数
    :param encoding: トークンエンコーディング
    :return: 分割されたテキストリスト
    """
    tokens = encoding.encode(text)
    return [
        encoding.decode(tokens[i : i + max_tokens])
        for i in range(0, len(tokens), max_tokens)
    ]


async def fetch_summary(chunk, client, semaphore):
    """
    各チャンクをGPTモデルに投げて要約を取得する非同期関数。

    :param chunk: テキストチャンク
    :param client: OpenAIクライアント
    :param semaphore: 非同期セマフォ
    :return: 要約されたテキストまたはエラーメッセージ
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
            return f"エラー: {str(e)}"


async def summarize_text(text):
    """
    メイン要約関数。

    :param text: 入力テキスト
    :return: 要約結果の文字列
    """
    try:
        max_tokens_per_chunk = 3000
        chunks = split_chunks(text, max_tokens_per_chunk, encoding)
        semaphore = asyncio.Semaphore(15)  # 同時実行の制限

        # 各チャンクを非同期に処理
        summaries = await asyncio.gather(*(fetch_summary(chunk, client, semaphore) for chunk in chunks))

        return "\n".join(summaries)
    except Exception as e:
        raise RuntimeError(f"Failed to summarize text: {str(e)}")
