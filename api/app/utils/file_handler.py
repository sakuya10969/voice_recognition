import os
import tempfile
from pathlib import Path
from fastapi import UploadFile
import logging

logger = logging.getLogger(__name__)

async def save_file_temporarily(file: UploadFile) -> str:
    """アップロードされたファイルを一時的に保存する"""
    try:
        # 一時ディレクトリの作成
        temp_dir = Path(tempfile.gettempdir()) / "voice_recognition"
        temp_dir.mkdir(exist_ok=True)
        
        # 一時ファイルのパスを生成
        temp_file_path = temp_dir / file.filename
        
        # ファイルの保存
        content = await file.read()
        with open(temp_file_path, "wb") as f:
            f.write(content)
            
        logger.info(f"一時ファイルを保存: {temp_file_path}")
        return str(temp_file_path)
        
    except Exception as e:
        logger.error(f"ファイルの保存に失敗: {str(e)}")
        raise Exception(f"ファイルの保存に失敗しました: {str(e)}") 