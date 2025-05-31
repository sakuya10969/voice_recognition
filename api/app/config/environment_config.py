import os
from dotenv import load_dotenv

load_dotenv()

class EnvironmentConfig:
    def __init__(self):
        # 必須環境変数リスト
        required_vars = [
            "AZ_SPEECH_KEY",
            "AZ_SPEECH_ENDPOINT",
            "AZ_OPENAI_KEY",
            "AZ_OPENAI_ENDPOINT",
            "AZ_BLOB_CONNECTION",
            "CLIENT_ID",
            "CLIENT_SECRET",
            "TENANT_ID",
        ]
        missing = [var for var in required_vars if not os.getenv(var)]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

        # すべての環境変数を属性としてセット
        for var in required_vars:
            setattr(self, var, os.getenv(var))
        # 固定値も属性としてセット
        self.AZ_CONTAINER_NAME = "container-vr-dev"
