import os
import time

from cozepy import ApplicationOAuth, COZE_CN_BASE_URL


def test_jwt_auth():
    client_id = os.getenv("COZE_JWT_AUTH_CLIENT_ID")
    private_key = os.getenv("COZE_JWT_AUTH_PRIVATE_KEY")
    key_id = os.getenv("COZE_JWT_AUTH_KEY_ID")

    app = ApplicationOAuth(
        client_id,
        base_url=COZE_CN_BASE_URL,
    )
    token = app.jwt_auth(private_key, key_id, 30)
    assert token.access_token != ""
    assert token.token_type == "Bearer"
    assert token.expires_in - int(time.time()) <= 31
    assert token.refresh_token == ""
