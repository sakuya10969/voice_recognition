from app.infrastructure.az_blob import AzBlobClient
from app.infrastructure.az_speech import AzSpeechClient
from app.infrastructure.az_openai import AzOpenAIClient
from app.infrastructure.ms_sharepoint import MsSharePointClient
from app.config.environment_config import EnvironmentConfig
from aiohttp import ClientSession

class AzClientFactory:
    def __init__(self, config: EnvironmentConfig, session: ClientSession):
        self.config = config
        self.session = session

    def create_az_blob_client(self) -> AzBlobClient:
        return AzBlobClient(
            az_blob_connection=self.config.AZ_BLOB_CONNECTION,
            az_container_name=self.config.AZ_CONTAINER_NAME
        )

    def create_az_speech_client(self) -> AzSpeechClient:
        return AzSpeechClient(
            session=self.session,
            az_speech_key=self.config.AZ_SPEECH_KEY,
            az_speech_endpoint=self.config.AZ_SPEECH_ENDPOINT
        )

    def create_az_openai_client(self) -> AzOpenAIClient:
        return AzOpenAIClient(
            az_openai_key=self.config.AZ_OPENAI_KEY,
            az_openai_endpoint=self.config.AZ_OPENAI_ENDPOINT
        )

    def create_ms_sharepoint_client(self) -> MsSharePointClient:
        return MsSharePointClient(
            client_id=self.config.CLIENT_ID,
            client_secret=self.config.CLIENT_SECRET,
            tenant_id=self.config.TENANT_ID,
        )
