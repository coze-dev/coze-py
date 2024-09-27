import os

from cozepy import COZE_CN_BASE_URL, ApplicationOAuth, JWTAuth, TokenAuth

COZE_JWT_AUTH_CLIENT_ID = os.getenv("COZE_JWT_AUTH_CLIENT_ID").strip()
COZE_JWT_AUTH_PRIVATE_KEY = os.getenv("COZE_JWT_AUTH_PRIVATE_KEY").strip()
COZE_JWT_AUTH_KEY_ID = os.getenv("COZE_JWT_AUTH_KEY_ID").strip()
if COZE_JWT_AUTH_PRIVATE_KEY == "" and os.getenv("COZE_JWT_AUTH_PRIVATE_KEY_FILE").strip() != "":
    with open(os.getenv("COZE_JWT_AUTH_PRIVATE_KEY_FILE").strip(), "r") as f:
        COZE_JWT_AUTH_PRIVATE_KEY = f.read()

COZE_TOKEN = os.getenv("COZE_TOKEN").strip()

app_oauth = ApplicationOAuth(
    COZE_JWT_AUTH_CLIENT_ID,
    base_url=COZE_CN_BASE_URL,
)

fixed_token_auth = TokenAuth(COZE_TOKEN)

jwt_auth = JWTAuth(
    COZE_JWT_AUTH_CLIENT_ID,
    COZE_JWT_AUTH_PRIVATE_KEY,
    COZE_JWT_AUTH_KEY_ID,
    30,
    base_url=COZE_CN_BASE_URL,
)
