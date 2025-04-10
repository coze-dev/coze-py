"""
This example is about how to use the device oauth process to acquire user authorization.
"""

# Firstly, users need to access https://www.coze.cn/open/oauth/apps. For the coze.com environment,
# users need to access https://www.coze.com/open/oauth/apps to create an OAuth App of the type
# of TVs/Limited Input devices/Command line programs.
# The specific creation process can be referred to in the document:
# https://www.coze.cn/docs/developer_guides/oauth_device_code. For the coze.com environment, it can be
# accessed at https://www.coze.com/docs/developer_guides/oauth_device_code.
# After the creation is completed, the client ID can be obtained.

import os

from cozepy import COZE_CN_BASE_URL, Coze, CozePKCEAuthError, CozePKCEAuthErrorType, DeviceOAuthApp, TokenAuth  # noqa

# The default access is api.coze.cn, but if you need to access api.coze.cn,
# please use base_url to configure the api endpoint to access
coze_api_base = os.getenv("COZE_API_BASE") or COZE_CN_BASE_URL

# client ID
device_oauth_client_id = os.getenv("COZE_DEVICE_OAUTH_CLIENT_ID")

# The sdk offers the DeviceOAuthApp class to establish an authorization for PKCE OAuth.
# Firstly, it is required to initialize the DeviceOAuthApp with the client ID.


device_oauth_app = DeviceOAuthApp(client_id=device_oauth_client_id, base_url=coze_api_base)

# In the device oauth authorization process, developers need to first call the interface
# of Coze to generate the device code to obtain the user_code and device_code. Then generate
# the authorization link through the user_code, guide the user to open the link, fill in the
# user_code, and consent to the authorization. Developers need to call the interface of Coze
# to generate the token through the device_code. When the user has not authorized or rejected
# the authorization, the interface will throw an error and return a specific error code.
# After the user consents to the authorization, the interface will succeed and return the
# access_token.


# First, make a call to obtain 'get_device_code'
device_code = device_oauth_app.get_device_code()

# The returned device_code contains an authorization link. Developers need to guide users
# to open up this link.
# open device_code.verification_url
print("Please open url:", device_code.verification_url)

# The developers then need to use the device_code to poll Coze's interface to obtain the token.
# The SDK has encapsulated this part of the code in and handled the different returned error
# codes. The developers only need to invoke get_access_token.
try:
    oauth_token = device_oauth_app.get_access_token(
        device_code=device_code.device_code,
        poll=True,
    )
    print("Get access token:", oauth_token.access_token)
except CozePKCEAuthError as e:
    if e.error == CozePKCEAuthErrorType.ACCESS_DENIED:
        # The user rejected the authorization.
        # Developers need to guide the user to open the authorization link again.
        pass
    elif e.error == CozePKCEAuthErrorType.EXPIRED_TOKEN:
        # The token has expired. Developers need to guide the user to open
        # the authorization link again.
        pass
    else:
        # Other errors
        pass

    raise  # for example, re-raise the error

# use the access token to init Coze client
coze = Coze(auth=TokenAuth(oauth_token.access_token), base_url=coze_api_base)

# When the token expires, you can also refresh and re-obtain the token
# oauth_token = device_oauth_app.refresh_access_token(oauth_token.refresh_token)
