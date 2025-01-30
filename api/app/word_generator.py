from pathlib import Path
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
import tempfile
import os
from datetime import datetime

async def create_word(summarized_text: str) -> Path:
    """議事録を作成して一時ファイルパスを返す関数"""
    # ファイル名を指定
    file_name = f"議事録_{datetime.now().strftime('%Y%m%d%H%M')}.docx"
    # 一時ディレクトリを取得し、完全なパスを作成
    temp_dir = tempfile.gettempdir()
    temp_path = Path(temp_dir) / file_name
    # ワードファイルの生成
    document = Document()
    document.add_heading("議事録", level=1)
    # **要約を1つのパラグラフとして追加**
    paragraph = document.add_paragraph(summarized_text)
    paragraph_format = paragraph.paragraph_format
    paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT  # 左揃え
    # 保存
    document.save(temp_path)
    return temp_path

async def cleanup_file(file_path: str):
    """一時ファイルを削除"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"削除成功: {file_path}")
    except Exception as e:
        print(f"削除失敗: {e}")
