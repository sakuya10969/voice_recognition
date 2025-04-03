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
    status: str = "Completed"

@dataclass
class MockAzBlobResponse(MockResponse):
    """Blob Storageのモックレスポンス"""
    blob_url: str = "https://mock.storage.blob"
    audio_url: str = "https://mock.storage.blob/audio.wav"
    file_data: bytes = b"mock audio data"

@dataclass
class MockAzOpenAIResponse(MockResponse):
    """OpenAIのモックレスポンス"""
    summary: str = "これはテスト用の要約テキストです。"
    tokens: int = 100
    model: str = "gpt-4"

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
        self.get_transcription_status = AsyncMock(return_value=self._response.status)
        self.get_transcription_result = AsyncMock(
            return_value={"contentUrls": {"contentUrl": self._response.content_url}}
        )
        self.get_content = AsyncMock(
            return_value={"displayText": self._response.display_text}
        )
        self.cancel_transcription = AsyncMock(return_value=True)
        self.list_transcriptions = AsyncMock(return_value=[])

class MockAzBlobClient(BaseMockClient):
    """Blob Storageのモッククライアント"""
    def __init__(self, response: Optional[MockAzBlobResponse] = None):
        super().__init__(response or MockAzBlobResponse())

    def _setup_mock_methods(self) -> None:
        self.upload_blob = AsyncMock(return_value=self._response.blob_url)
        self.delete_blob = AsyncMock(return_value=True)
        self.download_blob = AsyncMock(return_value=self._response.file_data)
        self.list_blobs = AsyncMock(return_value=[])
        self.get_blob_properties = AsyncMock(return_value={"size": 1024})
        self.copy_blob = AsyncMock(return_value=True)

class MockAzOpenAIClient(BaseMockClient):
    """OpenAIのモッククライアント"""
    def __init__(self, response: Optional[MockAzOpenAIResponse] = None):
        super().__init__(response or MockAzOpenAIResponse())

    def _setup_mock_methods(self) -> None:
        self.get_summary = AsyncMock(return_value=self._response.summary)
        self.summarize_text = AsyncMock(return_value=self._response.summary)
        self.count_tokens = AsyncMock(return_value=self._response.tokens)
        self.get_available_models = AsyncMock(return_value=["gpt-4", "gpt-3.5-turbo"])
        self.validate_api_key = AsyncMock(return_value=True)

class MockMsSharePointClient(BaseMockClient):
    """SharePointのモッククライアント"""
    def __init__(self):
        super().__init__(MockResponse())

    def _setup_mock_methods(self) -> None:
        self.upload_file = AsyncMock(return_value=True)
        self.get_file = AsyncMock(return_value=b"mock file content")
        self.delete_file = AsyncMock(return_value=True)
        self.list_files = AsyncMock(return_value=[])
        self.create_folder = AsyncMock(return_value=True)
        self.get_file_metadata = AsyncMock(return_value={"size": 1024, "modified": "2024-01-01"})
        self.move_file = AsyncMock(return_value=True)
        self.copy_file = AsyncMock(return_value=True)
        self.get_file_permissions = AsyncMock(return_value=[])
        self.set_file_permissions = AsyncMock(return_value=True)
