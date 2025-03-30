import os
from dotenv import load_dotenv

class EnvironmentConfig:
    REQUIRED_VARS = [
        "AZ_SPEECH_KEY", "AZ_SPEECH_ENDPOINT", "AZ_OPENAI_KEY",
        "AZ_OPENAI_ENDPOINT", "AZ_BLOB_CONNECTION", "CLIENT_ID",
        "CLIENT_SECRET", "TENANT_ID"
    ]

    def __init__(self):
        load_dotenv()
        self._load_environment_variables()
        self._validate_environment_variables()

    def _load_environment_variables(self):
        for var in self.REQUIRED_VARS:
            setattr(self, var, os.getenv(var))
        self.AZ_CONTAINER_NAME = "container-vr-dev"

    def _validate_environment_variables(self):
        missing = [var for var in self.REQUIRED_VARS if not getattr(self, var)]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
