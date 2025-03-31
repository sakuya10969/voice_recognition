from unittest.mock import AsyncMock
from dataclasses import dataclass
from typing import Optional

@dataclass
class MockResponse:
    """モックレスポンスの基底クラス"""
    pass

@dataclass 
class MockAzSpeechResponse(MockResponse):
    """Speech Serviceのモックレスポンス"""
    job_id: str = "mock-job-id"
    content_url: str = "https://mock.content.url/transcript.json"
    display_text: str = "これはテスト用の文字起こしテキストです。"

@dataclass
class MockAzBlobResponse(MockResponse):
    """Blob Storageのモックレスポンス"""
    blob_url: str = "https://mock.storage.blob"
    audio_url: str = "https://mock.storage.blob/audio.wav"

@dataclass
class MockAzOpenAIResponse(MockResponse):
    """OpenAIのモックレスポンス"""
    summary: str = "これはテスト用の要約テキストです。"

class BaseMockClient:
    """モッククライアントの基底クラス"""
    def __init__(self, response: MockResponse):
        self._response = response
        self._setup_mock_methods()

    def _setup_mock_methods(self) -> None:
        """モックメソッドの初期化 - サブクラスで実装"""
        pass

class MockAzSpeechClient(BaseMockClient):
    """Speech Serviceのモッククライアント"""
    def __init__(self, response: Optional[MockAzSpeechResponse] = None):
        super().__init__(response or MockAzSpeechResponse())

    def _setup_mock_methods(self) -> None:
        self.create_transcription_job = AsyncMock(return_value=self._response.job_id)
        self.get_transcription_status = AsyncMock(side_effect=["Running", "Succeeded"])
        self.get_transcription_result = AsyncMock(
            return_value={"contentUrls": {"contentUrl": self._response.content_url}}
        )
        self.get_content = AsyncMock(
            return_value={"displayText": self._response.display_text}
        )

class MockAzBlobClient(BaseMockClient):
    """Blob Storageのモッククライアント"""
    def __init__(self, response: Optional[MockAzBlobResponse] = None):
        super().__init__(response or MockAzBlobResponse())

    def _setup_mock_methods(self) -> None:
        self.upload_blob = AsyncMock(return_value=self._response.blob_url)
        self.get_blob_url = AsyncMock(return_value=self._response.audio_url)
        self.delete_blob = AsyncMock(return_value=True)

class MockAzOpenAIClient(BaseMockClient):
    """OpenAIのモッククライアント"""
    def __init__(self, response: Optional[MockAzOpenAIResponse] = None):
        super().__init__(response or MockAzOpenAIResponse())
    def _setup_mock_methods(self) -> None:
        self.get_summary = AsyncMock(return_value=self._response.summary)
        self.summarize_text = AsyncMock(return_value=self._response.summary)

class MockMsSharePointClient(BaseMockClient):
    """SharePointのモッククライアント"""
    def __init__(self):
        super().__init__(MockResponse())

    def _setup_mock_methods(self) -> None:
        self.upload_file = AsyncMock(return_value=True)
        self.get_file = AsyncMock(return_value=b"mock file content")
        self.delete_file = AsyncMock(return_value=True)
