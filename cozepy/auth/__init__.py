import abc
import random
import time
from urllib.parse import urlparse

from authlib.jose import jwt

from cozepy.model import CozeModel
from cozepy.request import Requester
from cozepy.config import COZE_COM_BASE_URL


def _random_hex(length):
    hex_characters = "0123456789abcdef"
    return "".join(random.choice(hex_characters) for _ in range(length))


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

    @property
    def verification_url(self):
        return f"{self.verification_uri}?user_code={self.user_code}"


class ApplicationOAuth(object):
    """
    App OAuth process to support obtaining token and refreshing token.
    """

    def __init__(
        self, client_id: str, client_secret: str = "", base_url: str = COZE_COM_BASE_URL
    ):
        self._client_id = client_id
        self._client_secret = client_secret
        self._base_url = base_url
        self._api_endpoint = urlparse(base_url).netloc
        self._token = ""
        self._requester = Requester()

    def jwt_auth(self, private_key: str, kid: str, ttl: int) -> OAuthToken:
        """
        Get the token by jwt with jwt auth flow.
        """
        jwt_token = self._gen_jwt(
            self._api_endpoint, private_key, self._client_id, kid, 3600
        )
        url = f"{self._base_url}/api/permission/oauth2/token"
        headers = {"Authorization": f"Bearer {jwt_token}"}
        body = {
            "duration_seconds": ttl,
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
        }
        return self._requester.request(
            "post", url, OAuthToken, headers=headers, body=body
        )

    def _gen_jwt(
        self, api_endpoint: str, private_key: str, client_id: str, kid: str, ttl: int
    ):
        now = int(time.time())
        header = {"alg": "RS256", "typ": "JWT", "kid": kid}
        payload = {
            "iss": client_id,
            "aud": api_endpoint,
            "iat": now,
            "exp": now + ttl,
            "jti": _random_hex(16),
        }
        s = jwt.encode(header, payload, private_key)
        return s.decode("utf-8")


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
        # TODO: 其他 sdk 实现
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
        kid: str,
        ttl: int = 7200,
        base_url: str = COZE_COM_BASE_URL,
    ):
        assert isinstance(client_id, str)
        assert isinstance(private_key, str)
        assert isinstance(kid, str)
        assert isinstance(ttl, int)
        assert ttl > 0
        assert isinstance(base_url, str)

        self._client_id = client_id
        self._private_key = private_key
        self._kid = kid
        self._ttl = ttl
        self._base_url = base_url
        self._token = None
        self._oauth_cli = ApplicationOAuth(self._client_id, base_url=self._base_url)

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
        self._token = self._oauth_cli.jwt_auth(self._private_key, self._kid, self._ttl)
        return self._token
