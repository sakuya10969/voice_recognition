import msal
import aiohttp
import asyncio
from functools import lru_cache

class SharePointAccessClass:
    def __init__(self, client_id, client_secret, tenant_id):
        """
        Initialize the SharePointAccessClass
        """
        self.client_id = client_id  # アプリケーション(クライアント)ID
        self.client_secret = client_secret  # シークレット(値)
        self.tenant_id = tenant_id  # ディレクトリ(テナント)ID
        self.authority = f"https://login.microsoftonline.com/{tenant_id}"
        self.scope = ["https://graph.microsoft.com/.default"]
        self.access_token = None
        self.token_lock = asyncio.Lock()  # 非同期トークン管理用ロック

    async def get_access_token(self):
        """
        非同期で Access Token を取得する
        """
        async with self.token_lock:
            if self.access_token:
                return self.access_token  # 既存のトークンがあればそれを返す
            
            app = msal.ConfidentialClientApplication(
                self.client_id,
                authority=self.authority,
                client_credential=self.client_secret
            )
            result = app.acquire_token_for_client(scopes=self.scope)
            if "access_token" in result:
                self.access_token = result["access_token"]
                return self.access_token
            else:
                raise Exception("No access token available")

    async def graph_api_get(self, endpoint: str) -> dict:
        """
        Graph API を非同期で GET する
        """
        token = await self.get_access_token()
        async with aiohttp.ClientSession() as session:
            async with session.get(
                endpoint,
                headers={'Authorization': f'Bearer {token}'},
                timeout=10
            ) as response:
                return await response.json()

    async def graph_api_put(self, endpoint: str, data) -> dict:
        """
        Graph API を非同期で PUT する
        """
        token = await self.get_access_token()
        async with aiohttp.ClientSession() as session:
            async with session.put(
                url=endpoint,
                headers={'Authorization': f'Bearer {token}'},
                data=data,
                timeout=10
            ) as response:
                return await response.json()

    async def get_sites(self):
        """
        非同期で SharePoint のサイト一覧を取得
        """
        return await self.graph_api_get("https://graph.microsoft.com/v1.0/sites")

    async def get_site_id(self, site_name):
        """
        非同期でサイト ID を取得
        """
        sites = await self.get_sites()
        for site in sites['value']:
            if site['name'] == site_name:
                return site['id']
        return None

    async def get_folders(self, site_id, folder_id='root'):
        """
        非同期で指定サイトのフォルダ一覧を取得
        """
        return await self.graph_api_get(
            f'https://graph.microsoft.com/v1.0/sites/{site_id}/drive/items/{folder_id}/children'
        )

    async def get_folder_id(self, site_id, folder_name, folder_id='root'):
        """
        非同期でフォルダ ID を取得
        """
        folders = await self.get_folders(site_id, folder_id)
        for folder in folders['value']:
            if folder_name == folder["name"]:
                return folder['id']
        return None

    async def get_folder(self, site_id, folder_name, folder_id='root'):
        """
        非同期でフォルダ情報を取得
        """
        subfolders = await self.get_folders(site_id, folder_id)
        for folder in subfolders['value']:
            if folder_name == folder["name"]:
                return folder
        return None

    async def get_folder_id_from_tree(self, site_id, sharepoint_directory, folder_id='root'):
        """
        非同期でディレクトリツリーの最下層フォルダIDを取得
        """
        return await self.get_folder_id(site_id, sharepoint_directory, folder_id)

    async def upload_file(self, target_site_name, sharepoint_directory, object_file_path):
        """
        非同期で SharePoint にファイルをアップロード
        """
        target_site_id = await self.get_site_id(target_site_name)
        folder_id = await self.get_folder_id_from_tree(target_site_id, sharepoint_directory, 'root')

        if folder_id:
            url = f'https://graph.microsoft.com/v1.0/sites/{target_site_id}/drive/items/{folder_id}:/{object_file_path.name}:/content'
            
            async with aiohttp.ClientSession() as session:
                async with session.put(url, headers={'Authorization': f'Bearer {await self.get_access_token()}'}, data=open(object_file_path, 'rb'), timeout=10) as response:
                    return await response.json()
        else:
            return {"error": "Folder not found"}
