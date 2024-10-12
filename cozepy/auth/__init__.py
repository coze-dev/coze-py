import abc
import time
from typing import List, Optional
from urllib.parse import quote_plus, urlparse

from authlib.jose import jwt  # type: ignore
from typing_extensions import Literal

from cozepy.config import COZE_CN_BASE_URL, COZE_COM_BASE_URL
from cozepy.exception import CozePKCEAuthError, CozePKCEAuthErrorType
from cozepy.model import CozeModel
from cozepy.request import Requester
from cozepy.util import gen_s256_code_challenge, random_hex


class OAuthToken(CozeModel):
    # The requested access token. The app can use this token to authenticate to the Coze resource.
    access_token: str
    # How long the access token is valid, in seconds (UNIX timestamp)
    expires_in: int
    # An OAuth 2.0 refresh token. The app can use this token to acquire other access tokens after the current access token expires. Refresh tokens are long-lived.
    refresh_token: str = ""
    # fixed: Bearer
    token_type: str = ""


class DeviceAuthCode(CozeModel):
    # device code
    device_code: str
    # The user code
    user_code: str
    # The verification uri
    verification_uri: str
    # The interval of the polling request
    interval: int = 5
    # The expiration time of the device code
    expires_in: int
    verification_url: Optional[str] = None


class ScopeAccountPermission(CozeModel):
    permission_list: List[str]


class ScopeAttributeConstraintConnectorBotChatAttribute(CozeModel):
    bot_id_list: List[str]


class ScopeAttributeConstraint(CozeModel):
    connector_bot_chat_attribute: ScopeAttributeConstraintConnectorBotChatAttribute


class Scope(CozeModel):
    account_permission: Optional[ScopeAccountPermission] = None
    attribute_constraint: Optional[ScopeAttributeConstraint] = None

    @staticmethod
    def build_bot_chat(bot_id_list: List[str], permission_list: Optional[List[str]] = None) -> "Scope":
        if not permission_list:
            permission_list = ["Connector.botChat"]
        return Scope(
            account_permission=ScopeAccountPermission(permission_list=permission_list),
            attribute_constraint=ScopeAttributeConstraint(
                connector_bot_chat_attribute=ScopeAttributeConstraintConnectorBotChatAttribute(bot_id_list=bot_id_list)
            )
            if bot_id_list
            else None,
        )


class OAuthApp(object):
    def __init__(self, client_id: str, base_url: str, www_base_url: str):
        self._client_id = client_id
        self._base_url = base_url
        self._api_endpoint = urlparse(base_url).netloc
        self._www_base_url = www_base_url
        self._requester = Requester()

    def _get_oauth_url(
        self,
        redirect_uri: str,
        code_challenge: Optional[str] = None,
        code_challenge_method: Optional[str] = None,
        state: str = "",
        workspace_id: Optional[str] = None,
    ):
        params = {
            "response_type": "code",
            "client_id": self._client_id,
            "redirect_uri": redirect_uri,
            "state": state,
        }
        if code_challenge:
            params["code_challenge"] = code_challenge
        if code_challenge_method:
            params["code_challenge_method"] = code_challenge_method

        uri = f"{self._get_www_base_url}/api/permission/oauth2/authorize"
        if workspace_id:
            uri = f"{self._get_www_base_url}/api/permission/oauth2/workspace_id/{workspace_id}/authorize"
        return uri + "?" + "&".join([f"{k}={quote_plus(v)}" for k, v in params.items()])

    def _refresh_access_token(self, refresh_token: str, secret: str = "") -> OAuthToken:
        url = f"{self._base_url}/api/permission/oauth2/token"
        headers = {"Authorization": f"Bearer {secret}"} if secret else {}
        body = {
            "grant_type": "refresh_token",
            "client_id": self._client_id,
            "refresh_token": refresh_token,
        }
        return self._requester.request("post", url, False, OAuthToken, headers=headers, body=body)

    async def _arefresh_access_token(self, refresh_token: str, secret: str = "") -> OAuthToken:
        url = f"{self._base_url}/api/permission/oauth2/token"
        headers = {"Authorization": f"Bearer {secret}"} if secret else {}
        body = {
            "grant_type": "refresh_token",
            "client_id": self._client_id,
            "refresh_token": refresh_token,
        }
        return await self._requester.arequest("post", url, False, OAuthToken, headers=headers, body=body)

    @property
    def _get_www_base_url(self) -> str:
        if self._www_base_url:
            return self._www_base_url
        if self._base_url in [COZE_CN_BASE_URL, COZE_COM_BASE_URL]:
            return self._base_url.replace("api", "www")
        return self._base_url


class WebOAuthApp(OAuthApp):
    """
    Normal OAuth App.
    """

    def __init__(self, client_id: str, client_secret: str, base_url: str = COZE_COM_BASE_URL, www_base_url: str = ""):
        """
        :param client_id:
        :param client_secret:
        :param base_url:
        """
        self._client_id = client_id
        self._client_secret = client_secret
        self._base_url = base_url
        self._api_endpoint = urlparse(base_url).netloc
        self._token = ""
        super().__init__(client_id, base_url, www_base_url=www_base_url)

    def get_oauth_url(
        self,
        redirect_uri: str,
        state: str = "",
        workspace_id: Optional[str] = None,
    ):
        """
        Get the pkce flow authorized url.

        :param redirect_uri: The redirect_uri of your app, where authentication responses can be sent and received by
        your app. It must exactly match one of the redirect URIs you registered in the OAuth Apps.
        :param state: A value included in the request that is also returned in the token response. It can be a string
        of any hash value.
        :param workspace_id:
        :return:
        """
        return self._get_oauth_url(
            redirect_uri,
            state=state,
            workspace_id=workspace_id,
        )

    def get_access_token(
        self,
        redirect_uri: str,
        code: str,
    ) -> OAuthToken:
        """
        Get the token by jwt with jwt auth flow.
        """
        url = f"{self._base_url}/api/permission/oauth2/token"
        headers = {"Authorization": f"Bearer {self._client_secret}"}
        body = {
            "client_id": self._client_id,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
        }
        return self._requester.request("post", url, False, OAuthToken, headers=headers, body=body)

    def refresh_access_token(self, refresh_token: str) -> OAuthToken:
        return self._refresh_access_token(refresh_token, self._client_secret)


class AsyncWebOAuthApp(OAuthApp):
    """
    Normal OAuth App.
    """

    def __init__(self, client_id: str, client_secret: str, base_url: str = COZE_COM_BASE_URL, www_base_url: str = ""):
        """
        :param client_id:
        :param client_secret:
        :param base_url:
        """
        self._client_id = client_id
        self._client_secret = client_secret
        self._base_url = base_url
        self._api_endpoint = urlparse(base_url).netloc
        self._token = ""
        super().__init__(client_id, base_url, www_base_url=www_base_url)

    def get_oauth_url(
        self,
        redirect_uri: str,
        state: str = "",
        workspace_id: Optional[str] = None,
    ):
        """
        Get the pkce flow authorized url.

        :param redirect_uri: The redirect_uri of your app, where authentication responses can be sent and received by
        your app. It must exactly match one of the redirect URIs you registered in the OAuth Apps.
        :param state: A value included in the request that is also returned in the token response. It can be a string
        of any hash value.
        :param workspace_id:
        :return:
        """
        return self._get_oauth_url(
            redirect_uri,
            state=state,
            workspace_id=workspace_id,
        )

    async def get_access_token(
        self,
        redirect_uri: str,
        code: str,
    ) -> OAuthToken:
        """
        Get the token by jwt with jwt auth flow.
        """
        url = f"{self._base_url}/api/permission/oauth2/token"
        headers = {"Authorization": f"Bearer {self._client_secret}"}
        body = {
            "client_id": self._client_id,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
        }
        return await self._requester.arequest("post", url, False, OAuthToken, headers=headers, body=body)

    async def refresh_access_token(self, refresh_token: str) -> OAuthToken:
        return await self._arefresh_access_token(refresh_token, self._client_secret)


class JWTOAuthApp(OAuthApp):
    """
    JWT OAuth App.
    """

    def __init__(self, client_id: str, private_key: str, public_key_id: str, base_url: str = COZE_COM_BASE_URL):
        """
        :param client_id:
        :param private_key:
        :param public_key_id:
        :param base_url:
        """
        self._client_id = client_id
        self._base_url = base_url
        self._api_endpoint = urlparse(base_url).netloc
        self._token = ""
        self._private_key = private_key
        self._public_key_id = public_key_id
        super().__init__(client_id, base_url, www_base_url="")

    def get_access_token(self, ttl: int = 900, scope: Optional[Scope] = None) -> OAuthToken:
        """
        Get the token by jwt with jwt auth flow.

        :param ttl: The validity period of the AccessToken you apply for is in seconds.
        The default value is 900 seconds and the maximum value you can set is 86399 seconds,
        which is 24 hours.
        :param scope:
        """
        jwt_token = self._gen_jwt(3600)
        url = f"{self._base_url}/api/permission/oauth2/token"
        headers = {"Authorization": f"Bearer {jwt_token}"}
        body = {
            "duration_seconds": ttl,
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "scope": scope.model_dump() if scope else None,
        }
        return self._requester.request("post", url, False, OAuthToken, headers=headers, body=body)

    def _gen_jwt(self, ttl: int):
        now = int(time.time())
        header = {"alg": "RS256", "typ": "JWT", "kid": self._public_key_id}
        payload = {
            "iss": self._client_id,
            "aud": self._api_endpoint,
            "iat": now,
            "exp": now + ttl,
            "jti": random_hex(16),
        }
        s = jwt.encode(header, payload, self._private_key)
        return s.decode("utf-8")


class AsyncJWTOAuthApp(OAuthApp):
    """
    JWT OAuth App.
    """

    def __init__(self, client_id: str, private_key: str, public_key_id: str, base_url: str = COZE_COM_BASE_URL):
        """
        :param client_id:
        :param private_key:
        :param public_key_id:
        :param base_url:
        """
        self._client_id = client_id
        self._base_url = base_url
        self._api_endpoint = urlparse(base_url).netloc
        self._token = ""
        self._private_key = private_key
        self._public_key_id = public_key_id
        super().__init__(client_id, base_url, www_base_url="")

    async def get_access_token(self, ttl: int, scope: Optional[Scope] = None) -> OAuthToken:
        """
        Get the token by jwt with jwt auth flow.
        """
        jwt_token = self._gen_jwt(3600)
        url = f"{self._base_url}/api/permission/oauth2/token"
        headers = {"Authorization": f"Bearer {jwt_token}"}
        body = {
            "duration_seconds": ttl,
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "scope": scope.model_dump() if scope else None,
        }
        return await self._requester.arequest("post", url, False, OAuthToken, headers=headers, body=body)

    def _gen_jwt(self, ttl: int):
        now = int(time.time())
        header = {"alg": "RS256", "typ": "JWT", "kid": self._public_key_id}
        payload = {
            "iss": self._client_id,
            "aud": self._api_endpoint,
            "iat": now,
            "exp": now + ttl,
            "jti": random_hex(16),
        }
        s = jwt.encode(header, payload, self._private_key)
        return s.decode("utf-8")


class PKCEOAuthApp(OAuthApp):
    """
    PKCE OAuth App.
    """

    def __init__(self, client_id: str, base_url: str = COZE_COM_BASE_URL, www_base_url: str = ""):
        self._token = ""
        self._requester = Requester()
        super().__init__(
            client_id,
            base_url,
            www_base_url,
        )

    def get_oauth_url(
        self,
        redirect_uri: str,
        code_verifier: str,
        code_challenge_method: Literal["plain", "S256"] = "plain",
        state: str = "",
        workspace_id: Optional[str] = None,
    ):
        """
        Get the pkce flow authorized url.

        :param redirect_uri: The redirect_uri of your app, where authentication responses can be sent and received by
        your app. It must exactly match one of the redirect URIs you registered in the OAuth Apps.
        :param code_verifier:
        :param code_challenge_method:
        :param state: A value included in the request that is also returned in the token response. It can be a string
        of any hash value.
        :param workspace_id:
        :return:
        """
        code_challenge = code_verifier if code_challenge_method == "plain" else gen_s256_code_challenge(code_verifier)

        return self._get_oauth_url(
            redirect_uri,
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method,
            state=state,
            workspace_id=workspace_id,
        )

    def get_access_token(self, redirect_uri: str, code: str, code_verifier: str) -> OAuthToken:
        """
        Get the token with pkce auth flow.

        :param redirect_uri:
        :param code_verifier:
        :param code:
        :return:
        """
        url = f"{self._base_url}/api/permission/oauth2/token"
        body = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": self._client_id,
            "redirect_uri": redirect_uri,
            "code_verifier": code_verifier,
        }
        return self._requester.request("post", url, False, OAuthToken, body=body)

    def refresh_access_token(self, refresh_token: str) -> OAuthToken:
        return self._refresh_access_token(refresh_token)


class AsyncPKCEOAuthApp(OAuthApp):
    """
    PKCE OAuth App.
    """

    def __init__(self, client_id: str, base_url: str = COZE_COM_BASE_URL, www_base_url: str = ""):
        self._token = ""
        self._requester = Requester()
        super().__init__(
            client_id,
            base_url,
            www_base_url,
        )

    def get_oauth_url(
        self,
        redirect_uri: str,
        code_verifier: str,
        code_challenge_method: Literal["plain", "S256"] = "plain",
        state: str = "",
        workspace_id: Optional[str] = None,
    ):
        """
        Get the pkce flow authorized url.

        :param redirect_uri: The redirect_uri of your app, where authentication responses can be sent and received by
        your app. It must exactly match one of the redirect URIs you registered in the OAuth Apps.
        :param code_verifier:
        :param code_challenge_method:
        :param state: A value included in the request that is also returned in the token response. It can be a string
        of any hash value.
        :param workspace_id:
        :return:
        """
        code_challenge = code_verifier if code_challenge_method == "plain" else gen_s256_code_challenge(code_verifier)

        return self._get_oauth_url(
            redirect_uri,
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method,
            state=state,
            workspace_id=workspace_id,
        )

    async def get_access_token(self, redirect_uri: str, code: str, code_verifier: str) -> OAuthToken:
        """
        Get the token with pkce auth flow.

        :param redirect_uri:
        :param code_verifier:
        :param code:
        :return:
        """
        url = f"{self._base_url}/api/permission/oauth2/token"
        body = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": self._client_id,
            "redirect_uri": redirect_uri,
            "code_verifier": code_verifier,
        }
        return await self._requester.arequest("post", url, False, OAuthToken, body=body)

    async def refresh_access_token(self, refresh_token: str) -> OAuthToken:
        return await self._arefresh_access_token(refresh_token)


class DeviceOAuthApp(OAuthApp):
    """
    Device OAuth App.
    """

    def __init__(self, client_id: str, base_url: str = COZE_COM_BASE_URL, www_base_url: str = ""):
        self._token = ""
        self._requester = Requester()
        super().__init__(
            client_id,
            base_url,
            www_base_url,
        )

    def get_device_code(
        self,
        workspace_id: Optional[str] = None,
    ) -> DeviceAuthCode:
        """
        Get the pkce flow authorized url.

        :param workspace_id:
        :return:
        """

        uri = f"{self._base_url}/api/permission/oauth2/device/code"
        if workspace_id:
            uri = f"{self._base_url}/api/permission/oauth2/workspace_id/{workspace_id}/device/code"
        body = {
            "client_id": self._client_id,
        }
        headers = {
            "Content-Type": "application/json",
        }
        res = self._requester.request("post", uri, False, DeviceAuthCode, headers=headers, body=body)
        res.verification_url = f"{res.verification_uri}?user_code={res.user_code}"
        return res

    def get_access_token(self, device_code: str, poll: bool = False) -> OAuthToken:
        """
        Get the token with pkce auth flow.

        :param device_code:
        :param poll: whether to poll for the token
        :return:
        """
        if not poll:
            return self._get_access_token(device_code)

        interval = 5
        while True:
            try:
                return self._get_access_token(device_code)
            except CozePKCEAuthError as e:
                if e.error == CozePKCEAuthErrorType.AUTHORIZATION_PENDING:
                    time.sleep(interval)
                    continue
                elif e.error == CozePKCEAuthErrorType.SLOW_DOWN:
                    if interval < 30:
                        interval += 5
                    time.sleep(interval)
                    continue
                else:
                    raise

    def _get_access_token(self, device_code: str, poll: bool = False) -> OAuthToken:
        """
        Get the token with pkce auth flow.

        :param device_code:
        :param poll: whether to poll for the token
        :return:
        """
        url = f"{self._base_url}/api/permission/oauth2/token"
        body = {
            "client_id": self._client_id,
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            "device_code": device_code,
        }
        return self._requester.request("post", url, False, OAuthToken, body=body)

    def refresh_access_token(self, refresh_token: str) -> OAuthToken:
        return self._refresh_access_token(refresh_token)


class AsyncDeviceOAuthApp(OAuthApp):
    """
    Device OAuth App.
    """

    def __init__(self, client_id: str, base_url: str = COZE_COM_BASE_URL, www_base_url: str = ""):
        self._token = ""
        self._requester = Requester()
        super().__init__(
            client_id,
            base_url,
            www_base_url,
        )

    async def get_device_code(self, workspace_id: Optional[str] = None) -> DeviceAuthCode:
        """
        Get the pkce flow authorized url.

        :param workspace_id:
        :return:
        """

        uri = f"{self._base_url}/api/permission/oauth2/device/code"
        if workspace_id:
            uri = f"{self._base_url}/api/permission/oauth2/workspace_id/{workspace_id}/device/code"
        body = {
            "client_id": self._client_id,
        }
        headers = {
            "Content-Type": "application/json",
        }
        res = await self._requester.arequest("post", uri, False, DeviceAuthCode, headers=headers, body=body)
        res.verification_url = f"{res.verification_uri}?user_code={res.user_code}"
        return res

    async def get_access_token(self, device_code: str, poll: bool = False) -> OAuthToken:
        """
        Get the token with pkce auth flow.

        :param device_code:
        :param poll: whether to poll for the token
        :return:
        """
        if not poll:
            return await self._get_access_token(device_code)

        interval = 5
        while True:
            try:
                return await self._get_access_token(device_code)
            except CozePKCEAuthError as e:
                if e.error == CozePKCEAuthErrorType.AUTHORIZATION_PENDING:
                    time.sleep(interval)
                    continue
                elif e.error == CozePKCEAuthErrorType.SLOW_DOWN:
                    if interval < 30:
                        interval += 5
                    time.sleep(interval)
                    continue
                else:
                    raise

    async def _get_access_token(self, device_code: str, poll: bool = False) -> OAuthToken:
        """
        Get the token with pkce auth flow.

        :param device_code:
        :param poll: whether to poll for the token
        :return:
        """
        url = f"{self._base_url}/api/permission/oauth2/token"
        body = {
            "client_id": self._client_id,
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            "device_code": device_code,
        }
        return await self._requester.arequest("post", url, False, OAuthToken, body=body)

    async def refresh_access_token(self, refresh_token: str) -> OAuthToken:
        return await self._arefresh_access_token(refresh_token)


class Auth(abc.ABC):
    """
    This class is the base class for all authorization types.

    It provides the abstract methods for getting the token type and token.
    """

    @property
    @abc.abstractmethod
    def token_type(self) -> str:
        """
        The authorization type used in the http request header.

        eg: Bearer, Basic, etc.

        :return: token type
        """

    @property
    @abc.abstractmethod
    def token(self) -> str:
        """
        The token used in the http request header.

        :return: token
        """

    def authentication(self, headers: dict) -> None:
        """
        Construct the authorization header in the http headers.

        :param headers: http headers
        :return: None
        """
        headers["Authorization"] = f"{self.token_type} {self.token}"


class TokenAuth(Auth):
    """
    The fixed access token auth flow.
    """

    def __init__(self, token: str):
        assert isinstance(token, str)
        assert len(token) > 0
        self._token = token

    @property
    def token_type(self) -> str:
        return "Bearer"

    @property
    def token(self) -> str:
        return self._token


class JWTAuth(Auth):
    """
    The JWT auth flow.
    """

    def __init__(
        self,
        client_id: str,
        private_key: str,
        public_key_id: str,
        ttl: int = 7200,
        base_url: str = COZE_COM_BASE_URL,
    ):
        assert isinstance(client_id, str)
        assert isinstance(private_key, str)
        assert isinstance(public_key_id, str)
        assert isinstance(ttl, int)
        assert ttl > 0
        assert isinstance(base_url, str)

        self._client_id = client_id
        self._ttl = ttl
        self._base_url = base_url
        self._token = None
        self._oauth_cli = JWTOAuthApp(self._client_id, private_key, public_key_id, base_url=self._base_url)

    @property
    def token_type(self) -> str:
        return "Bearer"

    @property
    def token(self) -> str:
        token = self._generate_token()
        return token.access_token

    def _generate_token(self):
        if self._token is not None and int(time.time()) < self._token.expires_in:
            return self._token
        self._token = self._oauth_cli.get_access_token(self._ttl)
        return self._token
