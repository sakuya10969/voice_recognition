from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import aiohttp
from contextlib import asynccontextmanager
import logging

from app.services.task_manager_service import TaskManager
from app.routers import transcription_router, sharepoint_router

# ロガー設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションのライフサイクル管理"""
    session = aiohttp.ClientSession()
    app.state.session = session
    app.state.task_manager = TaskManager()
    yield
    await session.close()

# FastAPIアプリケーションの設定
app = FastAPI(lifespan=lifespan)

# CORSミドルウェアの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーターの登録
app.include_router(transcription_router.router)
app.include_router(sharepoint_router.router)
