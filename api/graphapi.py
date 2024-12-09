import httpx
from fastapi import HTTPException
import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta

env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)

access_token = None
token_expiry = None

async def get_access_token(client_id: str, tenant_id: str, client_secret: str) -> str:
    global access_token, token_expiry
    now = datetime.now(timezone.utc)
    graphapi_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"

    if access_token and token_expiry and now < token_expiry:
        return access_token

    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "https://graph.microsoft.com/.default",
        "grant_type": "client_credentials",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(graphapi_url, data=data)
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"アクセストークンの取得に失敗しました: {response.text}",
            )
        token_data = response.json()

    access_token = token_data.get("access_token")
    expires_in = token_data.get("expires_in")
    token_expiry = now + timedelta(seconds=expires_in - 60)

    return access_token


async def upload_sharepoint(access_token: str, site_id: str, folder_path: str, file_name: str, file_content: bytes):
    upload_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root:/{folder_path}/{file_name}:/content"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/octet-stream",
    }

    async with httpx.AsyncClient() as client:
        response = await client.put(upload_url, headers=headers, content=file_content)
        if response.status_code != 201:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"ファイルのアップロードに失敗しました: {response.text}",
            )
        file_data = response.json()
        item_id = file_data["id"]

    return item_id


async def create_share_link(access_token: str, site_id: str, item_id: str):
    share_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/items/{item_id}/createLink"
    headers = {"Authorization": f"Bearer {access_token}"}
    data = {"type": "view", "scope": "anonymous"}

    async with httpx.AsyncClient() as client:
        response = await client.post(share_url, headers=headers, json=data)
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"シェアリンクの作成に失敗しました: {response.text}",
            )
        link_data = response.json()

    return link_data["link"]["webUrl"]
