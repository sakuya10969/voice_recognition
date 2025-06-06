from fastapi import FastAPI
import aiohttp
from contextlib import asynccontextmanager
import logging

from app.config.get_config import get_config
from app.infrastructure.az_client_factory import AzClientFactory
from app.services.task_managing_service import TaskManagingService
from app.middlewares.cors_middleware import configure_cors
from app.middlewares.logging_middleware import configure_logging
from app.routers import audio_processing_router
from app.routers import sharepoint_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションのライフサイクル管理"""
    session = aiohttp.ClientSession()
    try:
        app.state.config = get_config()
        app.state.session = session
        app.state.task_managing_service = TaskManagingService()
        app.state.az_client_factory = AzClientFactory(
            config=app.state.config, session=session
        )
        yield
    finally:
        await session.close()


app = FastAPI(lifespan=lifespan)

# ミドルウェアの設定
configure_logging(app)
configure_cors(app)

app.include_router(audio_processing_router.router)
app.include_router(sharepoint_router.router)
