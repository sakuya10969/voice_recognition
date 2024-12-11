# import httpx
# from fastapi import HTTPException
# from datetime import datetime, timezone, timedelta

# access_token = None
# token_expiry = None

# async def get_access_token(client_id: str, tenant_id: str, client_secret: str) -> str:
#     """
#     アクセストークンの取得
#     """
    
#     global access_token, token_expiry
#     now = datetime.now(timezone.utc)
#     graphapi_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"

#     if access_token and token_expiry and now < token_expiry:
#         return access_token

#     data = {
#         "client_id": client_id,
#         "client_secret": client_secret,
#         "scope": "https://graph.microsoft.com/.default",
#         "grant_type": "client_credentials",
#     }

#     async with httpx.AsyncClient() as client:
#         response = await client.post(graphapi_url, data=data)
#         if response.status_code != 200:
#             raise HTTPException(
#                 status_code=response.status_code,
#                 detail=f"アクセストークンの取得に失敗しました: {response.text}",
#             )
#         token_data = response.json()

#     access_token = token_data["access_token"]
#     expires_in = token_data["expires_in"]
#     token_expiry = now + timedelta(seconds=expires_in - 60)

#     return access_token


# async def upload_onedrive(access_token: str, drive_id: str, folder_path: str, file_name: str, file_content: bytes):
#     """
#     クライアント側でアップロードされたファイルをOneDriveにアップロード
#     """
    
#     upload_url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{folder_path}/{file_name}:/content"
#     headers = {
#         "Authorization": f"Bearer {access_token}",
#         "Content-Type": "application/octet-stream",
#     }

#     async with httpx.AsyncClient() as client:
#         response = await client.put(upload_url, headers=headers, content=file_content)
#         if response.status_code != 201:
#             raise HTTPException(
#                 status_code=response.status_code,
#                 detail=f"ファイルのアップロードに失敗しました: {response.text}",
#             )
#         file_data = response.json()
#         item_id = file_data["id"]

#     return item_id


# async def create_share_link(access_token: str, drive_id: str, item_id: str):
#     """
#     Onedriveにアップロードされたファイルの公開URLを取得
#     """
    
#     share_url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{item_id}/createLink"
#     headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
#     data = {"type": "view", "scope": "anonymous"}

#     async with httpx.AsyncClient() as client:
#         response = await client.post(share_url, headers=headers, json=data)
#         if response.status_code != 200:
#             raise HTTPException(
#                 status_code=response.status_code,
#                 detail=f"シェアリンクの作成に失敗しました: {response.text}",
#             )
#         link_data = response.json()

#     return link_data["link"]["webUrl"]


# async def handle_upload_onedrive(
#     client_id: str,
#     tenant_id: str,
#     client_secret: str,
#     drive_id: str,
#     folder_path: str,
#     file_name: str,
#     file_content: bytes,
# ) -> str:
#     access_token = await get_access_token(client_id, tenant_id, client_secret)

#     item_id = await upload_onedrive(access_token, drive_id, folder_path, file_name, file_content)

#     onedrive_url = await create_share_link(access_token, drive_id, item_id)

#     return onedrive_url
