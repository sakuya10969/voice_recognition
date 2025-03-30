from fastapi import Request
from app.core.config import config
from app.infrastructure.az_blob import AzBlobClient
from app.infrastructure.az_speech import AzSpeechClient
from app.infrastructure.az_openai import AzOpenAIClient
from app.infrastructure.ms_sharepoint import MsSharePointClient

class AzureClientFactory:
    """Azure関連のクライアントを生成するファクトリークラス"""
    
    @staticmethod
    def create_blob_client() -> AzBlobClient:
        """Azure Blob Storageクライアントを生成"""
        return AzBlobClient(config.AZ_BLOB_CONNECTION, config.AZ_CONTAINER_NAME)
    
    @staticmethod
    def create_speech_client(request: Request) -> AzSpeechClient:
        """Azure Speech Servicesクライアントを生成"""
        return AzSpeechClient(
            request.app.state.session,
            config.AZ_SPEECH_KEY, 
            config.AZ_SPEECH_ENDPOINT
        )
    
    @staticmethod
    def create_openai_client() -> AzOpenAIClient:
        """Azure OpenAIクライアントを生成"""
        return AzOpenAIClient(config.AZ_OPENAI_KEY, config.AZ_OPENAI_ENDPOINT)
    
    @staticmethod
    def create_sharepoint_client() -> MsSharePointClient:
        """SharePointクライアントを生成"""
        return MsSharePointClient(
            config.CLIENT_ID,
            config.CLIENT_SECRET,
            config.TENANT_ID
        )

# FastAPI dependency injection用の関数
def get_az_blob_client() -> AzBlobClient:
    return AzureClientFactory.create_blob_client()

def get_az_speech_client(request: Request) -> AzSpeechClient:
    return AzureClientFactory.create_speech_client(request)

def get_az_openai_client() -> AzOpenAIClient:
    return AzureClientFactory.create_openai_client()

def get_sp_access() -> MsSharePointClient:
    return AzureClientFactory.create_sharepoint_client()
