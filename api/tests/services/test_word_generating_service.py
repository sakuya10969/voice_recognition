import pytest
import os
from docx import Document
from typing import Dict
from unittest.mock import  patch

from app.services.word_generating_service import WordGeneratingService

class TestWordGeneratingService:
    @pytest.fixture
    def word_generating_service(self) -> WordGeneratingService:
        """WordGeneratorServiceのインスタンスを提供するフィクスチャ"""
        return WordGeneratingService()

    @pytest.fixture
    def mock_sample_texts(self) -> Dict[str, str]:
        """テスト用のサンプルテキストを提供するフィクスチャ"""
        return {
            'transcribed': 'これはテスト用の文字起こしテキストです。',
            'summarized': 'これはテスト用の要約テキストです。'
        }

    @pytest.fixture
    def mock_temp_file(self) -> str:
        """テスト用の一時ファイルパスを提供するフィクスチャ"""
        return "test_output.docx"

    async def _verify_document_structure(self, doc: Document, mock_sample_texts: Dict[str, str]) -> None:
        """Word文書の構造を検証するヘルパーメソッド"""
        # タイトルの検証
        assert doc.paragraphs[0].text == '文字起こしと要約'
        
        # セクションとコンテンツの検証
        sections = {
            '要約': mock_sample_texts['summarized'],
            '文字起こし': mock_sample_texts['transcribed']
        }
        
        current_section = None
        for para in doc.paragraphs[1:]:  # タイトルをスキップ
            if para.text in sections:
                current_section = para.text
            elif para.text and current_section:
                assert para.text == sections[current_section]

    @pytest.mark.asyncio
    async def test_create_word_document_success(
        self, 
        word_generating_service: WordGeneratingService, 
        mock_sample_texts: Dict[str, str],
        mock_temp_file: str
    ) -> None:
        """正常系: Word文書生成が成功するケース"""
        with patch('app.services.word_generating_service.WordGeneratingService._generate_temp_file_path', return_value=mock_temp_file):
            # 実行
            file_path = await word_generating_service.create_word_document(
                mock_sample_texts['transcribed'],
                mock_sample_texts['summarized']
            )

            try:
                # 検証
                assert os.path.exists(file_path)
                doc = Document(file_path)
                await self._verify_document_structure(doc, mock_sample_texts)
            finally:
                # クリーンアップ
                await word_generating_service.cleanup_word_file(file_path)

    @pytest.mark.asyncio
    async def test_cleanup_word_file_success(
        self, 
        word_generating_service: WordGeneratingService, 
        mock_sample_texts: Dict[str, str],
        mock_temp_file: str
    ) -> None:
        """正常系: ファイルクリーンアップが成功するケース"""
        with patch('app.services.word_generating_service.WordGeneratingService._generate_temp_file_path', return_value=mock_temp_file):
            # 準備
            file_path = await word_generating_service.create_word_document(
                mock_sample_texts['transcribed'],
                mock_sample_texts['summarized']
            )
            assert os.path.exists(file_path)
            
            # 実行
            await word_generating_service.cleanup_word_file(file_path)
            
            # 検証
            assert not os.path.exists(file_path)

    @pytest.mark.asyncio
    async def test_create_word_document_error(self, mock_word_generating_service: WordGeneratingService) -> None:
        """異常系: Word文書生成が失敗するケース"""
        with pytest.raises(ValueError, match="Word文書の生成に失敗"):
            await mock_word_generating_service.create_word_document(None, None)

    @pytest.mark.asyncio
    async def test_cleanup_nonexistent_file(self, mock_word_generating_service: WordGeneratingService) -> None:
        """異常系: 存在しないファイルのクリーンアップ"""
        # 実行と検証
        await mock_word_generating_service.cleanup_word_file("/path/to/nonexistent/file.docx")
        # エラーが発生しないことを確認