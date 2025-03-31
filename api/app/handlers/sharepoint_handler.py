import logging
from typing import Dict, Any

from fastapi import HTTPException, status, Request, Query

from app.infrastructure.ms_sharepoint import MsSharePointClient

logger = logging.getLogger(__name__)

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

async def get_sites(request: Request):
    client: MsSharePointClient = request.app.state.az_client_factory.create_ms_sharepoint_client()
    return await handle_sharepoint_operation("サイト取得", lambda: client.get_sites())

async def get_directories(request: Request, site_id: str = Query(...)):
    client: MsSharePointClient = request.app.state.az_client_factory.create_ms_sharepoint_client()
    return await handle_sharepoint_operation("ディレクトリ取得", lambda: client.get_folders(site_id))

async def get_subdirectories(request: Request, site_id: str = Query(...), directory_id: str = Query(...)):
    client: MsSharePointClient = request.app.state.az_client_factory.create_ms_sharepoint_client()
    return await handle_sharepoint_operation("サブディレクトリ取得", lambda: client.get_subfolders(site_id, directory_id))
