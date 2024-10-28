"""
This example is about How to use middleware.
"""

import os

from cozepy import (
    COZE_COM_BASE_URL,
    APIEndpoint,
    Coze,
    HTTPRequest,
    HTTPResponse,
    TokenAuth,
)

# Get an access_token through personal access token or oauth.
coze_api_token = os.getenv("COZE_API_TOKEN")
# The default access is api.coze.com, but if you need to access api.coze.cn,
# please use base_url to configure the api endpoint to access
coze_api_base = os.getenv("COZE_API_BASE") or COZE_COM_BASE_URL


def log_middleware(endpoint: APIEndpoint) -> APIEndpoint:
    def wrap(request: HTTPRequest) -> HTTPResponse:
        print("before", request.method, request.url)
        return endpoint(request)

    return wrap


def middleware_of_coze():
    # Init the Coze client through the access_token.
    coze = Coze(auth=TokenAuth(token=coze_api_token), base_url=coze_api_base, middlewares=[log_middleware])

    # your work space id
    workspace_id = os.getenv("COZE_WORKSPACE_ID") or "workspace id"

    # Call API With middleware
    print(coze.bots.list(space_id=workspace_id))


def middleware_of_method():
    # Init the Coze client through the access_token.
    coze = Coze(auth=TokenAuth(token=coze_api_token), base_url=coze_api_base)

    # your work space id
    workspace_id = os.getenv("COZE_WORKSPACE_ID") or "workspace id"

    # Call API With middleware
    print(coze.bots.list(space_id=workspace_id, middlewares=[log_middleware]))


if __name__ == "__main__":
    middleware_of_coze()
    middleware_of_method()
