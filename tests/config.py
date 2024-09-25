import os

from cozepy import ApplicationOAuth, COZE_CN_BASE_URL, JWTAuth, TokenAuth

COZE_JWT_AUTH_CLIENT_ID = os.getenv("COZE_JWT_AUTH_CLIENT_ID").strip()
COZE_JWT_AUTH_PRIVATE_KEY = os.getenv("COZE_JWT_AUTH_PRIVATE_KEY").strip()
COZE_JWT_AUTH_KEY_ID = os.getenv("COZE_JWT_AUTH_KEY_ID").strip()

COZE_TOKEN = os.getenv("COZE_TOKEN").strip()

app_oauth = ApplicationOAuth(
    COZE_JWT_AUTH_CLIENT_ID,
    base_url=COZE_CN_BASE_URL,
)

fixed_token_auth = TokenAuth(COZE_TOKEN)

jwt_auth = JWTAuth(
    COZE_JWT_AUTH_CLIENT_ID, COZE_JWT_AUTH_PRIVATE_KEY, COZE_JWT_AUTH_KEY_ID, 30, base_url=COZE_CN_BASE_URL
)
