from app.word_generator import create_word, cleanup_file
from app.sharepoint import get_access_token, upload_file

def upload_sharepoint(summary_text: str):
    file_path = create_word(summary_text)
    access_token = get_access_token()
    result = upload_file(access_token, file_path)
