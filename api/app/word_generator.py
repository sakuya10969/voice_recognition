from pathlib import Path
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt
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
    for idx, text in enumerate(summarized_text, start=1):
        document.add_heading(f"議題 {idx}", level=2)
        paragraph = document.add_paragraph(text)
        paragraph_format = paragraph.paragraph_format
        paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT  # 左揃え
        run = paragraph.runs[0]
        run.font.size = Pt(12)  # フォントサイズを12ポイントに設定

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
