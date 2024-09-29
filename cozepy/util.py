import base64
import random


def base64_encode_string(s: str) -> str:
    return base64.standard_b64encode(s.encode("utf-8")).decode("utf-8")


def random_hex(length):
    hex_characters = "0123456789abcdef"
    return "".join(random.choice(hex_characters) for _ in range(length))
