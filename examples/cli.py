import logging
import os
import time
from functools import lru_cache
from typing import Optional

from cozepy import COZE_CN_BASE_URL, Coze, DeviceOAuthApp, OAuthToken, TokenAuth
from cozepy.log import setup_logging

setup_logging(logging.ERROR)


class DeviceAuth(object):
    """设备授权认证类"""

    def __init__(self):
        # 初始化客户端ID和API基础URL
        self._client_id = "57294420732781205987760324720643.app.coze"
        self._api_base = COZE_CN_BASE_URL
        # 创建设备OAuth应用实例
        self._oauth_app = DeviceOAuthApp(client_id=self._client_id, base_url=self._api_base)
        self._token: Optional[OAuthToken] = None

    @property
    def token(self) -> Optional[OAuthToken]:
        """获取有效的token

        按以下顺序尝试获取token:
        1. 使用内存中缓存的token
        2. 从文件加载token
        3. 重新获取新token
        """
        # 检查内存中的token
        if self._token and self._is_token_valid(self._token):
            return self._token

        # 尝试从文件加载token
        if file_token := self._load_token():
            if self._is_token_valid(file_token):
                self._token = file_token
                return self._token
            # token过期但有refresh_token,尝试刷新
            if refreshed_token := self._refresh_token(file_token):
                self._token = refreshed_token
                self._save_token(refreshed_token)
                return self._token

        # 重新获取新token
        if new_token := self._get_token():
            self._token = new_token
            self._save_token(new_token)
            return self._token

        return None

    def client(self, workspace_id: Optional[str] = None) -> Coze:
        """创建Coze客户端"""
        if not (token := self.token):
            raise Exception("No valid token found")
        return Coze(auth=TokenAuth(token=token.access_token), base_url=self._api_base)

    def _is_token_valid(self, token: OAuthToken) -> bool:
        """检查token是否有效"""
        return token.expires_in + 30 > int(time.time())

    def _refresh_token(self, token: OAuthToken) -> Optional[OAuthToken]:
        """刷新token"""
        if not token.refresh_token:
            return None
        try:
            return self._oauth_app.refresh_token(token.refresh_token)
        except Exception:
            return None

    def _load_token(self) -> Optional[OAuthToken]:
        """从文件加载token"""
        cache_key = self._cache_key()
        if not os.path.exists(cache_key):
            return None
        try:
            with open(cache_key, "r") as f:
                return OAuthToken.model_validate_json(f.read())
        except Exception:
            return None

    def _save_token(self, token: OAuthToken) -> None:
        """保存token到文件"""
        cache_key = self._cache_key()
        with open(cache_key, "w") as f:
            f.write(token.model_dump_json())

    def _get_token(self) -> Optional[OAuthToken]:
        """获取新token"""
        try:
            device_code = self._oauth_app.get_device_code()
            print("Please open url:", device_code.verification_url)
            return self._oauth_app.get_access_token(device_code.device_code, poll=True)
        except Exception:
            return None

    @lru_cache(maxsize=1)
    def _cache_key(self) -> str:
        """获取token缓存文件路径"""
        dir = ".cache"
        if not os.path.exists(dir):
            os.makedirs(dir)
        return f"{dir}/coze_token_{self._client_id}.json"


class CozeCli(object):
    """Coze命令行接口类"""

    def __init__(self):
        self._auth = DeviceAuth()

    def list_workspaces(self):
        """列出所有工作空间"""
        return self._auth.client().workspaces.list()


def main():
    cli = CozeCli()
    print(cli.list_workspaces())


if __name__ == "__main__":
    main()
