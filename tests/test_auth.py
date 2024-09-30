import time

from tests.config import (
    jwt_auth,
    jwt_oauth_app,
)


def test_jwt_oauth_app():
    token = jwt_oauth_app.get_access_token(30)
    assert token.access_token != ""
    assert token.token_type == "Bearer"
    assert token.expires_in - int(time.time()) <= 31
    assert token.refresh_token == ""


def test_jwt_auth():
    assert jwt_auth.token != ""
