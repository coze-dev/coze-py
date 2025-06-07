from enum import Enum
from typing import Optional


class CozeError(Exception):
    """
    base class for all coze errors
    """

    pass


class CozeAPIError(CozeError):
    def __init__(
        self, code: Optional[int] = None, msg: str = "", logid: Optional[str] = None, debug_url: Optional[str] = None
    ):
        self.code = code
        self.msg = msg
        self.logid = logid
        self.debug_url = debug_url
        if code and code > 0:
            if self.debug_url:
                super().__init__(f"code: {code}, msg: {msg}, logid: {logid}, debug_url: {self.debug_url}")
            else:
                super().__init__(f"code: {code}, msg: {msg}, logid: {logid}")
        else:
            if self.debug_url:
                super().__init__(f"msg: {msg}, logid: {logid}, debug_url: {self.debug_url}")
            else:
                super().__init__(f"msg: {msg}, logid: {logid}")


class CozePKCEAuthErrorType(str, Enum):
    AUTHORIZATION_PENDING = "authorization_pending"
    SLOW_DOWN = "slow_down"
    ACCESS_DENIED = "access_denied"
    EXPIRED_TOKEN = "expired_token"


COZE_PKCE_AUTH_ERROR_TYPE_ENUMS = set(e.value for e in CozePKCEAuthErrorType)


class CozePKCEAuthError(CozeError):
    def __init__(self, error: CozePKCEAuthErrorType, logid: Optional[str] = None):
        super().__init__(f"pkce auth error: {error.value}")
        self.error = error
        self.logid = logid


class CozeInvalidEventError(CozeError):
    def __init__(self, field: str = "", data: str = "", logid: str = ""):
        self.field = field
        self.data = data
        self.logid = logid
        if field:
            super().__init__(f"invalid event, field: {field}, data: {data}, logid: {logid}")
        else:
            super().__init__(f"invalid event, data: {data}, logid: {logid}")
