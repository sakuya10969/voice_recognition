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
            connection_string=self.config.AZ_BLOB_CONNECTION,
            container_name=self.config.AZ_CONTAINER_NAME
        )

    def create_az_speech_client(self) -> AzSpeechClient:
        return AzSpeechClient(
            session=self.session,
            key=self.config.AZ_SPEECH_KEY,
            endpoint=self.config.AZ_SPEECH_ENDPOINT
        )

    def create_az_openai_client(self) -> AzOpenAIClient:
        return AzOpenAIClient(
            key=self.config.AZ_OPENAI_KEY,
            endpoint=self.config.AZ_OPENAI_ENDPOINT
        )

    def create_ms_sharepoint_client(self) -> MsSharePointClient:
        return MsSharePointClient(
            client_id=self.config.CLIENT_ID,
            client_secret=self.config.CLIENT_SECRET,
            tenant_id=self.config.TENANT_ID,
            session=self.session
        )
