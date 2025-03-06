import asyncio
import aiohttp
from fastapi import HTTPException

class AzTranscriptionClient:
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

    async def close(self):
        await self.session.close()

    async def create_transcription_job(self, blob_url: str) -> str:
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
        print(body)
        transcription_url = f"{self.az_speech_endpoint}/speechtotext/v3.2/transcriptions"
        async with self.session.post(
            transcription_url, headers=self.headers, json=body
        ) as response:
            if response.status != 201:
                raise HTTPException(
                    status_code=response.status,
                    detail=f"ジョブの作成に失敗しました: {await response.text()}",
                )
            return (await response.json())["self"]

    async def poll_transcription_status(
    self, job_url: str, max_attempts=240, initial_interval=30
) -> str:
        interval = initial_interval
        for _ in range(max_attempts):
            async with self.session.get(job_url, headers=self.headers) as response:
                if response.status != 200:
                    raise HTTPException(response.status, f"ステータス取得失敗: {await response.text()}")
                status_data = await response.json()

                if status_data["status"] == "Succeeded":
                    return status_data["links"]["files"]
                if status_data["status"] in ["Failed", "Cancelled"]:
                    raise HTTPException(500, f"ジョブ失敗: {status_data['status']}")

            await asyncio.sleep(interval)
            interval = min(interval * 2, 60)  # 最大60秒

        raise HTTPException(500, "ジョブのタイムアウト (2時間超過)")

    async def get_transcription_result(self, file_url: str) -> str:
        async with self.session.get(file_url, headers=self.headers) as response:
            if response.status != 200:
                raise HTTPException(
                    status_code=response.status,
                    detail=f"結果の取得に失敗しました: {await response.text()}",
                )
            files_data = await response.json()
            return files_data["values"][0]["links"]["contentUrl"]

    async def fetch_transcription_display(self, content_url: str) -> str:
        async with self.session.get(content_url) as response:
            if response.status != 200:
                raise HTTPException(
                    status_code=response.status,
                    detail=f"contentUrl の取得に失敗しました: {await response.text()}",
                )
            content_data = await response.json()
            return content_data["combinedRecognizedPhrases"][0]["display"]

    async def transcribe_audio(self, blob_url: str) -> str:
        if self.session.closed:
            self.session = aiohttp.ClientSession()
        job_url = await self.create_transcription_job(blob_url)
        file_url = await self.poll_transcription_status(job_url)
        content_url = await self.get_transcription_result(file_url)
        return await self.fetch_transcription_display(content_url)
