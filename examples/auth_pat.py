"""
This is an example where a personal access token is generated from the coze web page,
then stored in the environment variable, and the coze client is initialized through
the personal access token.
"""

# Firstly, you need to access https://www.coze.com/open/oauth/pats (for the cn environment,
# visit https://www.coze.cn/open/oauth/pats). Click to add a new token. After setting the
# appropriate name, expiration time, and permissions, click OK to generate your personal
# access token. Please store it in a secure environment to prevent this personal access
# token from being disclosed.

import os  # noqa

coze_api_token = os.getenv("COZE_API_TOKEN")

# The Coze SDK offers the AuthToken class for constructing an Auth class based on a fixed
# access token. Meanwhile, the Coze class enables the passing in of an Auth class to build
# a coze client.
#
# Therefore, you can utilize the following code to initialize a coze client, or an asynchronous
# coze client

from cozepy import AsyncCoze, Coze, TokenAuth  # noqa

# Establish a synchronous coze client by using the access_token
coze = Coze(auth=TokenAuth(token=coze_api_token))

# or
# Establish an asynchronous coze client by using the access_token
async_coze = AsyncCoze(auth=TokenAuth(token=coze_api_token))
