import msal
import requests
from functools import cache
from typing import Optional, Dict, Any
from pathlib import Path

class MsSharePointClient:
    def __init__(self, client_id: str, client_secret: str, tenant_id: str):
        """SharePointクライアントの初期化"""
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self.authority = f"https://login.microsoftonline.com/{tenant_id}"
        self.scope = ["https://graph.microsoft.com/.default"]
        self.access_token: Optional[str] = None
        self._get_access_token()

    def _get_access_token(self) -> None:
        """MSALを使用してアクセストークンを取得"""
        app = msal.ConfidentialClientApplication(
            self.client_id,
            authority=self.authority,
            client_credential=self.client_secret,
        )
        result = app.acquire_token_for_client(scopes=self.scope)
        
        if "access_token" not in result:
            raise ValueError("アクセストークンの取得に失敗しました")
        
        self.access_token = result["access_token"]

    def _validate_token(self) -> None:
        """アクセストークンの有無を確認"""
        if self.access_token is None:
            raise ValueError("アクセストークンが設定されていません")

    @cache
    def graph_api_get(self, endpoint: str) -> Optional[requests.Response]:
        """Graph APIのGETリクエストを実行"""
        self._validate_token()
        return requests.get(
            endpoint,
            headers={"Authorization": f"Bearer {self.access_token}"}
        )

    def graph_api_put(self, endpoint: str, data: Any) -> Optional[requests.Response]:
        """Graph APIのPUTリクエストを実行"""
        self._validate_token()
        return requests.put(
            url=endpoint,
            headers={"Authorization": f"Bearer {self.access_token}"},
            data=data
        )

    def get_sites(self) -> Dict:
        """SharePointのサイト一覧を取得"""
        response = self.graph_api_get("https://graph.microsoft.com/v1.0/sites")
        return response.json()

    def get_site_id(self, site_name: str) -> Optional[str]:
        """サイト名からサイトIDを取得"""
        sites = self.get_sites()
        for site in sites["value"]:
            if site["name"] == site_name:
                return site["id"]
        return None

    def get_folders(self, site_id: str, folder_id: str = "root") -> Optional[Dict]:
        """指定したサイトのフォルダ一覧を取得"""
        response = self.graph_api_get(
            f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/items/{folder_id}/children"
        )
        if response is None:
            return None

        data = response.json()
        if "value" not in data:
            return data

        data["value"] = [item for item in data["value"] if "folder" in item]
        return data

    def get_folder_id(self, site_id: str, folder_name: str, folder_id: str = "root") -> Optional[str]:
        """フォルダ名からフォルダIDを取得"""
        folders = self.get_folders(site_id, folder_id)
        if folders is None:
            return None

        for folder in folders["value"]:
            if folder["name"] == folder_name:
                return folder["id"]
        return None

    def get_folder(self, site_id: str, folder_name: str, folder_id: str = "root") -> Optional[Dict]:
        """フォルダ名からフォルダ情報を取得"""
        folders = self.get_folders(site_id, folder_id)
        if folders is None:
            return None

        for folder in folders["value"]:
            if folder["name"] == folder_name:
                return folder
        return None

    def get_folder_id_from_tree(self, site_id: str, sharepoint_directory: str, folder_id: str = "root") -> Optional[str]:
        """ディレクトリツリーの最下層フォルダIDを取得"""
        return self.get_folder_id(site_id, sharepoint_directory, folder_id)

    def get_subfolders(self, site_id: str, folder_id: str) -> Optional[Dict]:
        """指定フォルダ内のサブフォルダ一覧を取得"""
        return self.get_folders(site_id, folder_id)

    def upload_file(self, target_site_id: str, folder_id: str, file_path: Path) -> None:
        """ファイルをアップロード"""
        if not folder_id:
            raise ValueError("フォルダが見つかりません")

        url = f"https://graph.microsoft.com/v1.0/sites/{target_site_id}/drive/items/{folder_id}:/{file_path.name}:/content"
        
        with open(file_path, "rb") as f:
            self.graph_api_put(url, f)
