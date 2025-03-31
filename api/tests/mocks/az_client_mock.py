from unittest.mock import AsyncMock

class MockAzSpeechClient:
    """Azure Speech Serviceのモッククライアント"""
    def __init__(self):
        self.create_transcription_job = AsyncMock(return_value="mock-job-id")
        self.get_transcription_status = AsyncMock(side_effect=["Running", "Succeeded"])
        self.get_transcription_result = AsyncMock(return_value={
            "contentUrls": {
                "contentUrl": "https://mock.content.url/transcript.json"
            }
        })
        self.get_content = AsyncMock(return_value={
            "displayText": "これはテスト用の文字起こしテキストです。"
        })

class MockAzBlobClient:
    """Azure Blob Storageのモッククライアント"""
    def __init__(self):
        self.upload_blob = AsyncMock(return_value="https://mock.storage.blob")
        self.get_blob_url = AsyncMock(return_value="https://mock.storage.blob/audio.wav")
        self.delete_blob = AsyncMock(return_value=True)

class MockAzOpenAIClient:
    """Azure OpenAIのモッククライアント"""
    def __init__(self):
        self.summarize_text = AsyncMock(return_value="これはテスト用の要約テキストです。")
        self.analyze_text = AsyncMock(return_value={
            "sentiment": "positive",
            "key_points": ["ポイント1", "ポイント2"]
        })

class MockMsSharePointClient:
    """SharePointのモッククライアント"""
    def __init__(self):
        self.upload_file = AsyncMock(return_value=True)
        self.get_file = AsyncMock(return_value=b"mock file content")
        self.delete_file = AsyncMock(return_value=True)
