import logging
from typing import Any, Callable
from fastapi import APIRouter, HTTPException, status, Request, Query

from app.infrastructure.ms_sharepoint import MsSharePointClient

logger = logging.getLogger(__name__)

router = APIRouter()


def _get_sharepoint_client(request: Request) -> MsSharePointClient:
    """SharePointクライアントを取得する"""
    return request.app.state.az_client_factory.create_ms_sharepoint_client()


def _handle_sharepoint_operation(
    operation_name: str, operation: Callable
) -> dict[str, Any]:
    """SharePoint操作の共通エラーハンドリング"""
    try:
        return operation()
    except Exception as e:
        logger.error(f"SharePoint {operation_name}でエラー発生: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{operation_name}中にエラーが発生しました: {str(e)}",
        )


@router.get("/sites")
def get_sites(request: Request) -> dict[str, Any]:
    """SharePointのサイト一覧を取得する"""
    client = _get_sharepoint_client(request)
    return _handle_sharepoint_operation("サイト取得", client.get_sites)


@router.get("/directories")
def get_directories(request: Request, site_id: str = Query(...)) -> dict[str, Any]:
    """指定されたサイトのディレクトリ一覧を取得する"""
    client = _get_sharepoint_client(request)
    return _handle_sharepoint_operation(
        "ディレクトリ取得", lambda: client.get_folders(site_id)
    )


@router.get("/subdirectories")
def get_subdirectories(
    request: Request, site_id: str = Query(...), directory_id: str = Query(...)
) -> dict[str, Any]:
    """指定されたディレクトリのサブディレクトリ一覧を取得する"""
    client = _get_sharepoint_client(request)
    return _handle_sharepoint_operation(
        "サブディレクトリ取得", lambda: client.get_subfolders(site_id, directory_id)
    )
