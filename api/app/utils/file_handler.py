import os
import tempfile
from pathlib import Path
from fastapi import UploadFile
import logging

logger = logging.getLogger(__name__)

async def save_file_temporarily(file: UploadFile) -> str:
    """アップロードされたファイルを一時的に保存する"""
    try:
        suffix = Path(file.filename).suffix
        temp_file = _create_temp_file(suffix)
        await _write_file_content(file, temp_file)
        return temp_file.name
    except Exception as e:
        _handle_save_error(e)

def _create_temp_file(suffix: str) -> tempfile._TemporaryFileWrapper:
    """一時ファイルを作成する"""
    return tempfile.NamedTemporaryFile(delete=False, suffix=suffix)

async def _write_file_content(file: UploadFile, temp_file: tempfile._TemporaryFileWrapper) -> None:
    """ファイルの内容を書き込む"""
    content = await file.read()
    temp_file.write(content)

def _handle_save_error(e: Exception) -> None:
    """エラーハンドリング"""
    error_msg = f"ファイルの保存に失敗: {str(e)}"
    logger.error(error_msg)
    raise Exception(f"ファイルの保存に失敗しました: {str(e)}")