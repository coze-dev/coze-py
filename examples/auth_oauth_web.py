"""
How to effectuate OpenAPI authorization through the OAuth authorization code method.
"""

# Firstly, users need to access https://www.coze.com/open/oauth/apps. For the cn environment,
# users need to access https://www.coze.cn/open/oauth/apps to create an OAuth App of the type
# of Web application.
# The specific creation process can be referred to in the document:
# https://www.coze.com/docs/developer_guides/oauth_code. For the cn environment, it can be
# accessed at https://www.coze.cn/docs/developer_guides/oauth_code.
# After the creation is completed, the client ID, client secret, and redirect link, can be
# obtained. For the client secret, users need to keep it securely to avoid leakage.

import os  # noqa

# client ID
web_oauth_client_id = os.getenv("COZE_WEB_OAUTH_CLIENT_ID")
# client secret
web_oauth_client_secret = os.getenv("COZE_WEB_OAUTH_CLIENT_SECRET")
# redirect link
web_oauth_redirect_uri = os.getenv("COZE_WEB_OAUTH_REDIRECT_URI")

# The sdk offers the WebOAuthApp class to establish an authorization for Web OAuth.
# Firstly, it is required to initialize the WebOAuthApp with the client ID and client secret.


from cozepy import Coze, TokenAuth, WebOAuthApp  # noqa

web_oauth_app = WebOAuthApp(
    client_id=web_oauth_client_id,
    client_secret=web_oauth_client_secret,
)

# The WebOAuth authorization process is to first generate a coze authorization link and
# send it to the coze user requiring authorization. Once the coze user opens the link,
# they can see the authorization consent button.

# Generate the authorization link and direct the user to open it.
url = web_oauth_app.get_oauth_url(redirect_uri=web_oauth_redirect_uri)

# After the user clicks the authorization consent button, the coze web page will redirect
# to the redirect address configured in the authorization link and carry the authorization
# code and state parameters in the address via the query string.

# Get from the query of the redirect interface: query.get('code')
code = "mock code"

# After obtaining the code after redirection, the interface to exchange the code for a
# token can be invoked to generate the coze access_token of the authorized user.
oauth_token = web_oauth_app.get_access_token(redirect_uri=web_oauth_redirect_uri, code=code)

# use the access token to init Coze client
coze = Coze(auth=TokenAuth(oauth_token.access_token))

# When the token expires, you can also refresh and re-obtain the token
oauth_token = web_oauth_app.refresh_access_token(oauth_token.refresh_token)
