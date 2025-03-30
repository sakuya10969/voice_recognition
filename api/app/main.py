from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import aiohttp
from contextlib import asynccontextmanager
import logging

from app.core.config import get_config
from app.dependencies.az_client_factory import AzClientFactory
from app.services.task_manager_service import TaskManager
from app.routers import transcription_router, sharepoint_router

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションのライフサイクル管理"""
    session = aiohttp.ClientSession()
    try:
        app.state.config = get_config()
        app.state.session = session
        app.state.task_manager = TaskManager()
        app.state.az_client_factory = AzClientFactory(
            config=app.state.config,
            session=session
        )
        yield
    finally:
        await session.close()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(transcription_router.router)
app.include_router(sharepoint_router.router)
