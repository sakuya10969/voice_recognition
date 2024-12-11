import aiohttp
import asyncio


async def create_transcription_job(blob_url, headers, az_speech_endpoint):
    """ジョブを作成する"""
    body = {
        "displayName": "Transcription",
        "locale": "ja-jp",
        "contentUrls": [blob_url],
        "properties": {
            "punctuationMode": "DictatedAndAutomatic",
        },
    }
    transcription_url = f"{az_speech_endpoint}/speechtotext/v3.2/transcriptions"
    async with aiohttp.ClientSession() as session:
        async with session.post(
            transcription_url, headers=headers, json=body
        ) as response:
            if response.status != 201:
                raise Exception(f"ジョブの作成に失敗しました: {await response.text()}")
            return (await response.json())["self"]


async def poll_transcription_status(job_url, headers, max_attempts=30, interval=10):
    """ジョブの進行状況をチェックする"""
    async with aiohttp.ClientSession() as session:
        for _ in range(max_attempts):
            await asyncio.sleep(interval)
            async with session.get(job_url, headers=headers) as response:
                status_data = await response.json()
                if status_data["status"] == "Succeeded":
                    return status_data["links"]["files"]
                elif status_data["status"] in ["Failed", "Cancelled"]:
                    raise Exception(f"ジョブの進行に失敗しました: {status_data['status']}")
        raise Exception("Job timed out")


async def get_transcription_result(file_url, headers):
    """ジョブの結果から contentUrl を取得する"""
    async with aiohttp.ClientSession() as session:
        async with session.get(file_url, headers=headers) as response:
            if response.status != 200:
                raise Exception(f"結果の取得に失敗しました: {await response.text()}")
            files_data = await response.json()
            return files_data["values"][0]["links"]["contentUrl"]


async def fetch_transcription_display(content_url):
    """contentUrl にアクセスして display を取得する"""
    async with aiohttp.ClientSession() as session:
        async with session.get(content_url) as response:
            if response.status != 200:
                raise Exception(f"Error fetching contentUrl: {await response.text()}")
            content_data = await response.json()
            return content_data["combinedRecognizedPhrases"][0]["display"]


async def transcribe_audio(blob_url, az_speech_key, az_speech_endpoint):
    """メイン処理"""
    headers = {
        "Ocp-Apim-Subscription-Key": az_speech_key,
        "Content-Type": "application/json",
    }

    # ジョブ作成
    job_url = await create_transcription_job(blob_url, headers, az_speech_endpoint)
    # ジョブ進行確認
    file_url = await poll_transcription_status(job_url, headers)
    # contentUrl を取得
    content_url = await get_transcription_result(file_url, headers)
    # display を取得
    return await fetch_transcription_display(content_url)
