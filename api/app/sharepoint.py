import requests
import os
import time
from dotenv import load_dotenv
from fastapi import HTTPException
import aiohttp

from app.word_generator import create_word, cleanup_file

# .envをロード
load_dotenv(dotenv_path="../.env")

# 環境変数を取得
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
tenant_id = os.getenv("TENANT_ID")

# トークンキャッシュ
token_cache = {"access_token": None, "expires_at": 0}

def get_access_token():
    global token_cache
    # キャッシュが有効ならそれを使う
    if token_cache["access_token"] and token_cache["expires_at"] > time.time():
        return token_cache["access_token"]

    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "https://graph.microsoft.com/.default",
    }

    try:
        response = requests.post(url, headers=headers, data=data, timeout=10)
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data["access_token"]
            expires_in = token_data.get("expires_in", 3600)  # デフォルト3600秒
            token_cache = {
                "access_token": access_token,
                "expires_at": time.time()
                + expires_in
                - 300,  # 余裕を持たせて5分前に更新
            }
            return access_token
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to get access token: {response.text}",
            )
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"HTTP Request failed: {str(e)}")


async def upload_sharepoint(project_name: str, summary_text: str):
    """SharePointにWordファイルをアップロード"""
    access_token = get_access_token()
    sharepoint_url = "https://example.sharepoint.com/sites/your_site/_api/web/GetFolderByServerRelativeUrl('your_folder')/Files/add(url='filename.docx', overwrite=true)"
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
    file_path = create_word(project_name, summary_text)
    file_name = os.path.basename(file_path)
    
    try:
        with open(file_path, "rb") as file_data:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    sharepoint_url, headers=headers, data=file_data
                ) as response:
                    if response.status == 201:
                        print(f"アップロード成功: {file_name}")
                    else:
                        print(f"アップロード失敗: {await response.text()}")
                    response.raise_for_status()
    except Exception as e:
        print(f"SharePointアップロード中にエラー発生: {e}")
    finally:
        # 一時ファイル削除
        await cleanup_file(file_path)
