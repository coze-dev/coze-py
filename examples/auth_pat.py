"""
How to use personal access token to init Coze client.
"""

# Firstly, you need to access https://www.coze.cn/open/oauth/pats (for the coze.com environment,
# visit https://www.coze.com/open/oauth/pats).
#
# Click to add a new token. After setting the appropriate name, expiration time, and
# permissions, click OK to generate your personal access token. Please store it in a
# secure environment to prevent this personal access token from being disclosed.

import os

from cozepy import COZE_CN_BASE_URL, AsyncCoze, AsyncTokenAuth, Coze, TokenAuth

coze_api_token = os.getenv("COZE_API_TOKEN")
# The default access is api.coze.cn, but if you need to access api.coze.com,
# please use base_url to configure the api endpoint to access
coze_api_base = os.getenv("COZE_API_BASE") or COZE_CN_BASE_URL

# The Coze SDK offers the AuthToken class for constructing an Auth class based on a fixed
# access token. Meanwhile, the Coze class enables the passing in of an Auth class to build
# a coze client.
#
# Therefore, you can utilize the following code to initialize a coze client, or an asynchronous
# coze client


# Establish a synchronous coze client by using the access_token
coze = Coze(auth=TokenAuth(token=coze_api_token), base_url=coze_api_base)

# or
# Establish an asynchronous coze client by using the access_token
async_coze = AsyncCoze(auth=AsyncTokenAuth(token=coze_api_token), base_url=coze_api_base)
