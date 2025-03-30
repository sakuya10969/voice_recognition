from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from typing import Dict, Any
import logging
from app.infrastructure.ms_sharepoint import MsSharePointClient
from api.app.dependencies.az_client_factory import get_ms_sharepoint_client

router = APIRouter()
logger = logging.getLogger(__name__)

class SharePointRouter:
    """SharePoint関連のルーティングを管理するクラス"""

    @staticmethod
    async def handle_sharepoint_operation(operation_name: str, operation: callable) -> Dict[str, Any]:
        """SharePoint操作の共通エラーハンドリング"""
        try:
            return await operation()
        except Exception as e:
            logger.error(f"SharePoint {operation_name}でエラー発生: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"{operation_name}中にエラーが発生しました: {str(e)}"
            )

@router.get("/sites")
async def get_sites(request: Request):
    """サイト一覧を取得"""
    ms_sharepoint_client: MsSharePointClient = request.app.state.az_client_factory.create_ms_sharepoint_client()
    async def get_sites_operation():
        return ms_sharepoint_client.get_sites()
    return await SharePointRouter.handle_sharepoint_operation("サイト取得", get_sites_operation)

@router.get("/directories")
async def get_directories(
    request: Request,
    site_id: str = Query(...)
):
    """指定されたサイトのディレクトリ一覧を取得"""
    ms_sharepoint_client: MsSharePointClient = request.app.state.az_client_factory.create_ms_sharepoint_client()
    async def get_directories_operation():
        return ms_sharepoint_client.get_folders(site_id)
    return await SharePointRouter.handle_sharepoint_operation("ディレクトリ取得", get_directories_operation)

@router.get("/subdirectories")
async def get_subdirectories(
    request: Request,
    site_id: str = Query(...),
    directory_id: str = Query(...)
):
    """指定されたディレクトリのサブディレクトリ一覧を取得"""
    ms_sharepoint_client: MsSharePointClient = request.app.state.az_client_factory.create_ms_sharepoint_client()
    async def get_subdirectories_operation():
        return ms_sharepoint_client.get_subfolders(site_id, directory_id)
    return await SharePointRouter.handle_sharepoint_operation("サブディレクトリ取得", get_subdirectories_operation)
