import asyncio
import aiohttp
from fastapi import HTTPException
from typing import Dict, Any

class AzSpeechClient:
    def __init__(self, session: aiohttp.ClientSession, az_speech_key: str, az_speech_endpoint: str):
        self.headers = {
            "Ocp-Apim-Subscription-Key": az_speech_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Accept-Language": "ja-JP",
            "X-Japan-Force": "True",
        }
        self.az_speech_endpoint = az_speech_endpoint
        self.session = session

    async def close(self) -> None:
        """セッションをクローズする"""
        if not self.session.closed:
            await self.session.close()

    async def get(self, url: str) -> Dict[str, Any]:
        """GETリクエストを実行する"""
        return await self._make_request("GET", url)

    async def post(self, url: str, json_body: Dict[str, Any]) -> Dict[str, Any]:
        """POSTリクエストを実行する"""
        return await self._make_request("POST", url, json_body)

    async def _make_request(self, method: str, url: str, json_body: Dict[str, Any] = None) -> Dict[str, Any]:
        """HTTPリクエストを実行する"""
        async with self.session.request(method, url, headers=self.headers, json=json_body) as response:
            expected_status = 201 if method == "POST" else 200
            if response.status != expected_status:
                error_msg = "ジョブの作成" if method == "POST" else "リクエスト"
                raise HTTPException(
                    status_code=response.status,
                    detail=f"{error_msg}に失敗しました: {await response.text()}"
                )
            return await response.json()

    async def create_transcription_job(self, blob_url: str) -> str:
        """文字起こしジョブを作成する"""
        body = {
            "displayName": "Transcription",
            "locale": "ja-JP",
            "contentUrls": [blob_url],
            "properties": {
                "audioLocale": "ja-JP",
                "defaultLanguageCode": "ja-JP",
                "diarizationEnabled": True,
                "punctuationMode": "DictatedAndAutomatic",
                "wordLevelTimestampsEnabled": True,
            },
        }
        transcription_url = f"{self.az_speech_endpoint}/speechtotext/v3.2/transcriptions"
        response_data = await self.post(transcription_url, body)
        return response_data["self"]

    async def poll_transcription_status(
        self, 
        job_url: str, 
        max_attempts: int = 240, 
        initial_interval: int = 30
    ) -> str:
        """文字起こしジョブのステータスを確認する"""
        interval = initial_interval
        for _ in range(max_attempts):
            status_data = await self.get(job_url)
            
            match status_data["status"]:
                case "Succeeded":
                    return status_data["links"]["files"]
                case "Failed" | "Cancelled":
                    raise HTTPException(500, f"ジョブ失敗: {status_data['status']}")
            
            await asyncio.sleep(interval)
            interval = min(interval * 2, 60)
        
        raise HTTPException(500, "ジョブのタイムアウト (2時間超過)")

    async def get_transcription_result(self, file_url: str) -> str:
        """文字起こし結果のURLを取得する"""
        files_data = await self.get(file_url)
        return files_data["values"][0]["links"]["contentUrl"]

    async def fetch_transcription_display(self, content_url: str) -> str:
        """文字起こしの表示用テキストを取得する"""
        content_data = await self.get(content_url)
        return content_data["combinedRecognizedPhrases"][0]["display"]