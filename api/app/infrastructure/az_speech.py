import asyncio
import aiohttp
from fastapi import HTTPException
from typing import Dict, Any, Optional

class AzSpeechClient:
    """Azure Speech Servicesのクライアントクラス"""

    def __init__(self, session: aiohttp.ClientSession, az_speech_key: str, az_speech_endpoint: str):
        self._session = session
        self._endpoint = az_speech_endpoint.rstrip("/")
        self._headers = self._create_headers(az_speech_key)

    def _create_headers(self, az_speech_key: str) -> Dict[str, str]:
        return {
            "Ocp-Apim-Subscription-Key": az_speech_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Accept-Language": "ja-JP",
            "X-Japan-Force": "True",
        }

    async def close(self) -> None:
        if not self._session.closed:
            await self._session.close()

    async def create_transcription_job(self, blob_url: str, display_name: Optional[str] = None) -> str:
        body = self._create_transcription_config(blob_url, display_name)
        transcription_url = f"{self._endpoint}/speechtotext/v3.2/transcriptions"
        response_data = await self._post(transcription_url, body)
        return response_data["self"]

    def _create_transcription_config(self, blob_url: str, display_name: Optional[str]) -> Dict[str, Any]:
        return {
            "displayName": display_name or "Transcription",
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
        timeout_seconds: int = 7200,
        interval: int = 15
    ) -> str:
        """
        ジョブの完了を非同期で監視。最大timeout_seconds秒まで監視。
        intervalは待機秒数。
        """
        end_time = asyncio.get_event_loop().time() + timeout_seconds
        while True:
            status_data = await self._get(job_url)
            status = status_data.get("status")

            if status == "Succeeded":
                return status_data["links"]["files"]
            elif status in ["Failed", "Cancelled"]:
                raise HTTPException(500, f"ジョブ失敗: {status}")

            if asyncio.get_event_loop().time() > end_time:
                raise HTTPException(500, "ジョブのタイムアウト")

            await asyncio.sleep(interval)

    async def get_transcription_result(self, file_url: str) -> str:
        file_data = await self._get(file_url)
        return file_data["values"][0]["links"]["contentUrl"]

    async def get_transcription_display(self, content_url: str) -> str:
        content_data = await self._get(content_url)
        return content_data["combinedRecognizedPhrases"][0]["display"]

    async def process_full_transcription(self, blob_url: str) -> str:
        """
        1関数でジョブ作成→完了監視→結果取得までを完結させる高速パス。
        """
        job_url = await self.create_transcription_job(blob_url)
        files_url = await self.poll_transcription_status(job_url)
        result_url = await self.get_transcription_result(files_url)
        return await self.get_transcription_display(result_url)

    async def _get(self, url: str) -> Dict[str, Any]:
        return await self._make_request("GET", url)

    async def _post(self, url: str, json_body: Dict[str, Any]) -> Dict[str, Any]:
        return await self._make_request("POST", url, json_body)

    async def _make_request(self, method: str, url: str, json_body: Dict[str, Any] = None) -> Dict[str, Any]:
        try:
            async with self._session.request(method, url, headers=self._headers, json=json_body) as response:
                expected_status = 201 if method == "POST" else 200
                if response.status != expected_status:
                    error_msg = "ジョブの作成" if method == "POST" else "リクエスト"
                    raise HTTPException(
                        status_code=response.status,
                        detail=f"{error_msg}に失敗しました: {await response.text()}"
                    )
                return await response.json()
        except asyncio.TimeoutError:
            raise HTTPException(504, "Azure Speech APIへの接続がタイムアウトしました")
        except aiohttp.ClientError as e:
            raise HTTPException(502, f"HTTPエラー: {str(e)}")