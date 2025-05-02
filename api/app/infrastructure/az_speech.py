import asyncio
import aiohttp
from fastapi import HTTPException
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

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
        """文字起こしジョブを作成する"""
        body = self._create_transcription_config(blob_url, display_name)
        transcription_url = f"{self._endpoint}/speechtotext/v3.2/transcriptions"
        response_data = await self._post(transcription_url, body)
        return response_data["self"]

    def _create_transcription_config(self, blob_url: str, display_name: Optional[str]) -> Dict[str, Any]:
        """文字起こし設定を作成する"""
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

    async def poll_transcription_status(self, job_url: str, timeout_seconds: int = 7200, interval: int = 15) -> str:
        """文字起こしジョブの状態を監視する"""
        end_time = asyncio.get_event_loop().time() + timeout_seconds
        
        while True:
            status_data = await self._get(job_url)
            status = status_data.get("status")

            if status == "Succeeded":
                return status_data["links"]["files"]
            
            if status in ["Failed", "Cancelled"]:
                raise HTTPException(500, f"ジョブ失敗: {status}")

            if asyncio.get_event_loop().time() > end_time:
                raise HTTPException(500, "ジョブのタイムアウト")

            await asyncio.sleep(interval)

    async def get_transcription_result_url(self, file_url: str) -> str:
        """文字起こし結果のURLを取得する"""
        file_data = await self._get(file_url)
        return file_data["values"][0]["links"]["contentUrl"]

    async def get_transcription_by_speaker(self, content_url: str) -> str:
        """話者ごとに文字起こし結果を整形する"""
        content_data = await self._get(content_url)
        recognized_phrases = content_data.get("recognizedPhrases", [])
        
        return self._format_transcription_by_speaker(recognized_phrases)

    def _format_transcription_by_speaker(self, recognized_phrases: list) -> str:
        """話者ごとに文字起こし結果をブロック分けする"""
        result_blocks = []
        current_speaker = None
        current_block = []

        for phrase in recognized_phrases:
            speaker = phrase.get("speaker", 0)
            text = phrase.get("nBest", [{}])[0].get("display", "")

            if speaker != current_speaker:
                if current_block:
                    result_blocks.append(
                        f"[話者{current_speaker}]\n" + "\n".join(current_block)
                    )
                current_speaker = speaker
                current_block = [text]
            else:
                current_block.append(text)

        if current_block:
            result_blocks.append(
                f"[話者{current_speaker}]\n" + "\n".join(current_block)
            )

        final_result = "\n\n".join(result_blocks)
        logger.info(f"時系列話者テキスト:\n{final_result}")
        return final_result

    async def process_full_transcription(self, blob_url: str) -> str:
        """話者識別付きで全文文字起こしを取得する"""
        job_url = await self.create_transcription_job(blob_url)
        files_url = await self.poll_transcription_status(job_url)
        result_url = await self.get_transcription_result_url(files_url)
        return await self.get_transcription_by_speaker(result_url)

    async def _get(self, url: str) -> Dict[str, Any]:
        """GETリクエストを実行する"""
        return await self._make_request("GET", url)

    async def _post(self, url: str, json_body: Dict[str, Any]) -> Dict[str, Any]:
        """POSTリクエストを実行する"""
        return await self._make_request("POST", url, json_body)

    async def _make_request(self, method: str, url: str, json_body: Dict[str, Any] = None) -> Dict[str, Any]:
        """HTTPリクエストを実行する"""
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
