import time

from tests.config import (
    app_oauth,
    COZE_JWT_AUTH_KEY_ID,
    COZE_JWT_AUTH_PRIVATE_KEY,
    jwt_auth,
)


def test_jwt_app_oauth():
    token = app_oauth.jwt_auth(COZE_JWT_AUTH_PRIVATE_KEY, COZE_JWT_AUTH_KEY_ID, 30)
    assert token.access_token != ""
    assert token.token_type == "Bearer"
    assert token.expires_in - int(time.time()) <= 31
    assert token.refresh_token == ""


def test_jwt_auth():
    assert jwt_auth.token != ""
