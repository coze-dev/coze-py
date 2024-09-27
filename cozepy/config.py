import httpx

# default coze base_url is api.coze.com
COZE_COM_BASE_URL = "https://api.coze.com"
# support change to api.coze.cn
COZE_CN_BASE_URL = "https://api.coze.cn"

# default timeout is 10 minutes, with 5 seconds connect timeout
DEFAULT_TIMEOUT = httpx.Timeout(timeout=600.0, connect=5.0)
DEFAULT_CONNECTION_LIMITS = httpx.Limits(max_connections=1000, max_keepalive_connections=100)
