from typing_extensions import Literal


class CozeError(Exception):
    """
    base class for all coze errors
    """

    pass


class CozeAPIError(CozeError):
    """
    base class for all api errors
    """

    def __init__(self, code: int = None, msg: str = "", logid: str = None):
        self.code = code
        self.msg = msg
        self.logid = logid
        if code and code > 0:
            super().__init__(f"code: {code}, msg: {msg}, logid: {logid}")
        else:
            super().__init__(f"msg: {msg}, logid: {logid}")


class CozePKCEAuthError(CozeError):
    """
    base class for all pkce auth errors
    """

    def __init__(
        self, error: Literal["authorization_pending", "slow_down", "access_denied", "expired_token"], logid: str = None
    ):
        super().__init__(f"pkce auth error: {error}")
        self.error = error
        self.logid = logid


class CozeEventError(CozeError):
    """
    base class for all event errors
    """

    def __init__(self, field: str = "", data: str = "", logid: str = ""):
        self.field = field
        self.data = data
        self.logid = logid
        if field:
            super().__init__(f"invalid event, field: {field}, data: {data}, logid: {logid}")
        else:
            super().__init__(f"invalid event, data: {data}, logid: {logid}")
