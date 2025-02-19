import os
from pathlib import Path
from datetime import datetime
import tempfile
from docx import Document
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.shared import Pt
from fastapi import HTTPException

async def create_word(transcribed_text: str, summarized_text: str) -> Path:
    """議事録を作成して一時ファイルパスを返す関数（レイアウト修正版）"""
    try:
        file_name = f"議事録_{datetime.now().strftime('%Y-%m%d-%H%M')}.docx"
        temp_dir = tempfile.gettempdir()
        temp_path = Path(temp_dir) / file_name
        document = Document()
        # メインタイトル（議事録）
        title = document.add_heading("議事録", level=1)
        title.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        # [要約結果] 見出し
        document.add_heading("■ 要約結果", level=2)
        # 要約テキスト（1300文字ごとに改ページ）
        chunk_size = 1300
        summarized_chunks = [
            summarized_text[i : i + chunk_size]
            for i in range(0, len(summarized_text), chunk_size)
        ]
        for i, chunk in enumerate(summarized_chunks):
            paragraph = document.add_paragraph(chunk)
            paragraph_format = paragraph.paragraph_format
            paragraph_format.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
            paragraph.runs[0].font.size = Pt(11)  # フォントサイズを設定
            if i < len(summarized_chunks) - 1:
                paragraph.add_run("\n")  # 改行を入れてから改ページ
                document.add_page_break()
        # [文字起こし結果] 見出し
        document.add_heading("■ 文字起こし結果", level=2)
        # 文字起こしテキスト（1300文字ごとに改ページ）
        transcribed_chunks = [
            transcribed_text[i : i + chunk_size]
            for i in range(0, len(transcribed_text), chunk_size)
        ]
        for i, chunk in enumerate(transcribed_chunks):
            paragraph = document.add_paragraph(chunk)
            paragraph_format = paragraph.paragraph_format
            paragraph_format.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
            paragraph.runs[0].font.size = Pt(11)  # フォントサイズを設定
            if i < len(transcribed_chunks) - 1:
                paragraph.add_run("\n")  # 改行を入れてから改ページ
                document.add_page_break()
        # 文書を保存
        document.save(temp_path)
        return temp_path
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to create word file: {str(e)}"
        )

async def cleanup_word(file_path: str):
    """一時ファイルを削除"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cleanup file: {str(e)}")
