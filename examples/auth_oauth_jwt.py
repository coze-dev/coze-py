"""
This example is about how to use the service jwt oauth process to acquire user authorization.
"""

# Firstly, users need to access https://www.coze.com/open/oauth/apps. For the cn environment,
# users need to access https://www.coze.cn/open/oauth/apps to create an OAuth App of the type
# of Service application.
# The specific creation process can be referred to in the document:
# https://www.coze.com/docs/developer_guides/oauth_jwt. For the cn environment, it can be
# accessed at https://www.coze.cn/docs/developer_guides/oauth_jwt.
# After the creation is completed, three parameters, namely the client ID, private key,
# and public key id, can be obtained. For the client secret and public key id, users need to
# keep it securely to avoid leakage.

import os  # noqa

# client ID
jwt_oauth_client_id = os.getenv("COZE_JWT_OAUTH_CLIENT_ID")
# private key
jwt_oauth_private_key = os.getenv("COZE_JWT_OAUTH_PRIVATE_KEY")
# public key id
jwt_oauth_public_key_id = os.getenv("COZE_JWT_OAUTH_PUBLIC_KEY_ID")

# The sdk offers the JWTOAuthApp class to establish an authorization for Service OAuth.
# Firstly, it is required to initialize the JWTOAuthApp.


from cozepy import Coze, TokenAuth, JWTOAuthApp  # noqa

jwt_oauth_app = JWTOAuthApp(
    client_id=jwt_oauth_client_id,
    private_key=jwt_oauth_private_key,
    public_key_id=jwt_oauth_public_key_id,
)

# The jwt oauth type requires using private to be able to issue a jwt token, and through
# the jwt token, apply for an access_token from the coze service. The sdk encapsulates
# this procedure, and only needs to use get_access_token to obtain the access_token under
# the jwt oauth process.

# Generate the authorization token
oauth_token = jwt_oauth_app.get_access_token(ttl=3600)

# use the access token to init Coze client
coze = Coze(auth=TokenAuth(oauth_token.access_token))

# The jwt oauth process does not support refreshing tokens. When the token expires,
# just directly call get_access_token to generate a new token.
