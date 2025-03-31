import asyncio
import aiohttp
from fastapi import HTTPException
from typing import Dict, Any

class AzSpeechClient:
    """Azure Speech Servicesのクライアントクラス"""

    def __init__(self, session: aiohttp.ClientSession, az_speech_key: str, az_speech_endpoint: str):
        self._session = session
        self._endpoint = az_speech_endpoint
        self._headers = self._create_headers(az_speech_key)

    def _create_headers(self, az_speech_key: str) -> Dict[str, str]:
        """HTTPヘッダーを作成する"""
        return {
            "Ocp-Apim-Subscription-Key": az_speech_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Accept-Language": "ja-JP",
            "X-Japan-Force": "True",
        }

    async def close(self) -> None:
        """セッションをクローズする"""
        if not self._session.closed:
            await self._session.close()

    async def create_transcription_job(self, blob_url: str) -> str:
        """文字起こしジョブを作成する"""
        body = self._create_transcription_config(blob_url)
        transcription_url = f"{self._endpoint}/speechtotext/v3.2/transcriptions"
        response_data = await self._post(transcription_url, body)
        return response_data["self"]

    def _create_transcription_config(self, blob_url: str) -> Dict[str, Any]:
        """文字起こし設定を作成する"""
        return {
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

    async def poll_transcription_status(
        self, 
        job_url: str, 
        max_attempts: int = 240, 
        initial_interval: int = 30
    ) -> str:
        """文字起こしジョブのステータスを確認する"""
        interval = initial_interval
        for _ in range(max_attempts):
            status_data = await self._get(job_url)
            
            if status := status_data["status"]:
                if status == "Succeeded":
                    return status_data["links"]["files"]
                if status in ["Failed", "Cancelled"]:
                    raise HTTPException(500, f"ジョブ失敗: {status}")
            
            await asyncio.sleep(interval)
            interval = min(interval * 2, 60)
        
        raise HTTPException(500, "ジョブのタイムアウト (2時間超過)")

    async def get_transcription_result(self, file_url: str) -> str:
        """文字起こし結果のURLを取得する"""
        files_data = await self._get(file_url)
        return files_data["values"][0]["links"]["contentUrl"]

    async def get_transcription_display(self, content_url: str) -> str:
        """文字起こしの表示用テキストを取得する"""
        content_data = await self._get(content_url)
        return content_data["combinedRecognizedPhrases"][0]["display"]

    async def _get(self, url: str) -> Dict[str, Any]:
        """GETリクエストを実行する"""
        return await self._make_request("GET", url)

    async def _post(self, url: str, json_body: Dict[str, Any]) -> Dict[str, Any]:
        """POSTリクエストを実行する"""
        return await self._make_request("POST", url, json_body)

    async def _make_request(self, method: str, url: str, json_body: Dict[str, Any] = None) -> Dict[str, Any]:
        """HTTPリクエストを実行する"""
        async with self._session.request(method, url, headers=self._headers, json=json_body) as response:
            expected_status = 201 if method == "POST" else 200
            if response.status != expected_status:
                error_msg = "ジョブの作成" if method == "POST" else "リクエスト"
                raise HTTPException(
                    status_code=response.status,
                    detail=f"{error_msg}に失敗しました: {await response.text()}"
                )
            return await response.json()