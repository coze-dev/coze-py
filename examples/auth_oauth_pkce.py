"""
How to effectuate OpenAPI authorization through the OAuth Proof Key for Code Exchange method.
"""

# PKCE stands for Proof Key for Code Exchange, and it's an extension to the OAuth 2.0 authorization
# code flow designed to enhance security for public clients, such as mobile and single-page
# applications.

# Firstly, users need to access https://www.coze.cn/open/oauth/apps. For the coze.com environment,
# users need to access https://www.coze.com/open/oauth/apps to create an OAuth App of the type
# of Mobile/PC/Single-page application.
# The specific creation process can be referred to in the document:
# https://www.coze.cn/docs/developer_guides/oauth_pkce. For the coze.com environment, it can be
# accessed at https://www.coze.com/docs/developer_guides/oauth_pkce.
# After the creation is completed, the client ID can be obtained.

import os

from cozepy import COZE_CN_BASE_URL, Coze, PKCEOAuthApp, TokenAuth

# The default access is api.coze.cn, but if you need to access api.coze.com,
# please use base_url to configure the api endpoint to access
coze_api_base = os.getenv("COZE_API_BASE") or COZE_CN_BASE_URL

# client ID
pkce_oauth_client_id = os.getenv("COZE_PKCE_OAUTH_CLIENT_ID")
# redirect link
web_oauth_redirect_uri = os.getenv("COZE_WEB_OAUTH_REDIRECT_URI")

# The sdk offers the PKCEOAuthApp class to establish an authorization for PKCE OAuth.
# Firstly, it is required to initialize the PKCEOAuthApp with the client ID.


pkce_oauth_app = PKCEOAuthApp(client_id=pkce_oauth_client_id, base_url=coze_api_base)

# In the pkce oauth process, first, need to select a suitable code_challenge_method.
# Coze supports two types: plain and s256. Then, based on the selected code_challenge_method
# type, hash the code_verifier into the code_challenge. Finally, based on the callback address,
# code_challenge, and code_challenge_method, an authorization link can be generated.


# In the SDK, we have wrapped up the code_challenge process of PKCE. Developers only need
# to select the code_challenge_method.
code_verifier = "random code verifier"
url = pkce_oauth_app.get_oauth_url(
    redirect_uri=web_oauth_redirect_uri, code_verifier=code_verifier, code_challenge_method="S256"
)

# Developers should lead users to open up this authorization link. When the user
# consents to the authorization, Coze will redirect with the code to the callback address
# configured by the developer, and the developer can obtain this code.


# Get from the query of the redirect interface: query.get('code')
code = "mock code"

# After obtaining the code after redirection, the interface to exchange the code for a
# token can be invoked to generate the coze access_token of the authorized user.
oauth_token = pkce_oauth_app.get_access_token(
    redirect_uri=web_oauth_redirect_uri, code=code, code_verifier=code_verifier
)

# use the access token to init Coze client
coze = Coze(auth=TokenAuth(oauth_token.access_token), base_url=coze_api_base)

# When the token expires, you can also refresh and re-obtain the token
oauth_token = pkce_oauth_app.refresh_access_token(oauth_token.refresh_token)
