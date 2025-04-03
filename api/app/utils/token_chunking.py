import tiktoken
from typing import List

def split_token(text: str, max_tokens: int) -> List[str]:
    """
    テキストをトークン単位で分割し、指定された最大トークン数以下のチャンクに分割。
    """
    if not text:
        return []

    encoding = tiktoken.encoding_for_model("gpt-4o")
    tokens = encoding.encode(text)
    
    # トークンを文字列チャンクに変換
    chunks = []
    for i in range(0, len(tokens), max_tokens):
        chunk_tokens = tokens[i:i + max_tokens]
        chunk_text = encoding.decode(chunk_tokens)
        chunks.append(chunk_text)
        
    return chunks
