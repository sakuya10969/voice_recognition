from openai import AsyncAzureOpenAI
from fastapi import HTTPException
import asyncio
from typing import List, Dict, Any

class AzOpenAIClient:
    def __init__(
        self,
        az_openai_key: str,
        az_openai_endpoint: str,
        api_version: str = "2024-02-01",
        max_concurrent: int = 10
    ):
        """Azure OpenAI クライアントの初期化"""
        self.client = AsyncAzureOpenAI(
            api_key=az_openai_key,
            azure_endpoint=az_openai_endpoint,
            api_version=api_version,
        )
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def get_summary(self, prompt_messages: List[Dict[str, Any]]) -> str:
        """要約を取得する"""
        async with self.semaphore:
            try:
                response = await self.client.chat.completions.create(
                    model="gpt-4o",
                    max_tokens=3000,
                    messages=prompt_messages,
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"OpenAIエラー: {str(e)}"
                )
