import base64
import hashlib
import random
import sys

if sys.version_info < (3, 10):

    async def anext(iterator, default=None):
        try:
            return await iterator.__anext__()
        except StopAsyncIteration:
            if default is not None:
                return default
            raise
else:
    from builtins import anext

    _ = anext


def base64_encode_string(s: str) -> str:
    return base64.standard_b64encode(s.encode("utf-8")).decode("utf-8")


def random_hex(length):
    hex_characters = "0123456789abcdef"
    return "".join(random.choice(hex_characters) for _ in range(length))


def gen_s256_code_challenge(code_verifier):
    # 1. SHA256(ASCII(code_verifier))
    sha256_hash = hashlib.sha256(code_verifier.encode("ascii")).digest()
    # 2. BASE64URL-ENCODE
    code_challenge = base64.urlsafe_b64encode(sha256_hash).decode("ascii")
    # 3. remove =
    code_challenge = code_challenge.rstrip("=")
    return code_challenge
