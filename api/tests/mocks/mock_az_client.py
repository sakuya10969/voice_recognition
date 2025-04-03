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
    status: str = "Succeeded"
    files_url: str = "https://mock.files.url"

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

@dataclass
class MockMsSharePointResponse(MockResponse):
    """SharePointのモックレスポンス"""
    site_id: str = "mock-site-id"
    folder_id: str = "mock-folder-id"
    access_token: str = "mock-access-token"
    sites_data: dict = None
    folders_data: dict = None

    def __post_init__(self):
        if self.sites_data is None:
            self.sites_data = {
                "value": [
                    {"name": "TestSite", "id": self.site_id}
                ]
            }
        if self.folders_data is None:
            self.folders_data = {
                "value": [
                    {
                        "name": "TestFolder",
                        "id": self.folder_id,
                        "folder": {}
                    }
                ]
            }

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
        self.poll_transcription_status = AsyncMock(return_value=self._response.files_url)
        self.get_transcription_result = AsyncMock(return_value=self._response.content_url)
        self.get_transcription_display = AsyncMock(return_value=self._response.display_text)
        self._get = AsyncMock(return_value={
            "status": self._response.status,
            "links": {
                "files": self._response.files_url
            },
            "values": [{
                "links": {
                    "contentUrl": self._response.content_url
                }
            }],
            "combinedRecognizedPhrases": [{
                "display": self._response.display_text
            }]
        })
        self._post = AsyncMock(return_value={"self": self._response.job_id})
        self.close = AsyncMock()

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
    def __init__(self, response: Optional[MockMsSharePointResponse] = None):
        super().__init__(response or MockMsSharePointResponse())

    def _setup_mock_methods(self) -> None:
        self._get_access_token = AsyncMock()
        self.graph_api_get = AsyncMock(return_value=type(
            "Response", (), {
                "json": lambda: self._response.sites_data if "sites" in self._get_current_mock_call_args() 
                else self._response.folders_data
            }
        ))
        self.graph_api_put = AsyncMock(return_value=type(
            "Response", (), {"status_code": 200}
        ))
        self.get_sites = AsyncMock(return_value=self._response.sites_data)
        self.get_site_id = AsyncMock(return_value=self._response.site_id)
        self.get_folders = AsyncMock(return_value=self._response.folders_data)
        self.get_folder_id = AsyncMock(return_value=self._response.folder_id)
        self.get_folder = AsyncMock(return_value=self._response.folders_data["value"][0])
        self.get_folder_id_from_tree = AsyncMock(return_value=self._response.folder_id)
        self.get_subfolders = AsyncMock(return_value=self._response.folders_data)
        self.upload_file = AsyncMock()

    def _get_current_mock_call_args(self):
        """現在のモックコールの引数を取得するヘルパーメソッド"""
        return self.graph_api_get.call_args[0][0] if self.graph_api_get.call_args else ""