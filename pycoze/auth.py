import abc


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


class PersonalAccessToken(Auth):
    """
    The personal access token created in https://www.coze.cn/open/oauth/pats.

    :param token: the token created in coze pats website
    :type token: str
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
