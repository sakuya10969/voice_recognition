import pytest
import os
from docx import Document

from app.services.word_generating_service import WordGeneratingService

class TestWordGeneratingService:
    @pytest.fixture
    def mock_word_generating_service(self):
        """WordGeneratorServiceのインスタンスを提供するフィクスチャ"""
        return WordGeneratingService()

    @pytest.fixture
    def mock_sample_texts(self):
        """テスト用のサンプルテキストを提供するフィクスチャ"""
        return {
            'transcribed': 'これはテスト用の文字起こしテキストです。',
            'summarized': 'これはテスト用の要約テキストです。'
        }

    @pytest.mark.asyncio
    async def test_create_word_document_success(self, mock_word_generating_service, mock_sample_texts):
        """正常系: Word文書生成が成功するケース"""
        # 実行
        file_path = await mock_word_generating_service.create_word_document(
            mock_sample_texts['transcribed'],
            mock_sample_texts['summarized']
        )

        try:
            # 検証
            assert os.path.exists(file_path)
            doc = Document(file_path)
            
            # 文書構造の検証
            self._verify_document_structure(doc, mock_sample_texts)
        finally:
            # クリーンアップ
            await mock_word_generating_service.cleanup_word_file(file_path)

    def _verify_document_structure(self, doc: Document, mock_sample_texts: dict):
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
    async def test_cleanup_word_file_success(self, mock_word_generating_service, mock_sample_texts):
        """正常系: ファイルクリーンアップが成功するケース"""
        # 準備
        file_path = await mock_word_generating_service.create_word_document(
            mock_sample_texts['transcribed'],
            mock_sample_texts['summarized']
        )
        assert os.path.exists(file_path)
        
        # 実行
        await mock_word_generating_service.cleanup_word_file(file_path)
        
        # 検証
        assert not os.path.exists(file_path)

    @pytest.mark.asyncio
    async def test_create_word_document_error(self, mock_word_generating_service):
        """異常系: Word文書生成が失敗するケース"""
        with pytest.raises(Exception) as exc_info:
            await mock_word_generating_service.create_word_document(None, None)
        assert "Word文書の生成に失敗" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_cleanup_nonexistent_file(self, mock_word_generating_service):
        """異常系: 存在しないファイルのクリーンアップ"""
        # 実行と検証
        await mock_word_generating_service.cleanup_word_file("/path/to/nonexistent/file.docx")
        # エラーが発生しないことを確認