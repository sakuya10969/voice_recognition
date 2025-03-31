from typing import Optional
from fastapi import Form
from app.models.transcription import Transcription

def parse_transcription_form(
    site: Optional[str] = Form(None),
    directory: Optional[str] = Form(None)
) -> Transcription:
    """
    フォームデータからTranscriptionモデルを生成する依存性注入関数
    """
    return Transcription(
        site=site or "",
        directory=directory or ""
    )