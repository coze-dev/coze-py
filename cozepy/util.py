import base64
import hashlib
import inspect
import random
import sys
import wave
from enum import Enum
from typing import Any

from pydantic import BaseModel

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


def remove_url_trailing_slash(base_url: str) -> str:
    if base_url:
        return base_url.rstrip("/")
    return base_url


def http_base_url_to_ws(base_url: str) -> str:
    if not base_url:
        raise ValueError("base_url cannot be empty")
    if not base_url.startswith("https://"):
        raise ValueError("base_url must start with 'https://'")
    base_url = base_url.replace("https://", "wss://")

    if "api-" in base_url:
        return base_url.replace("api-", "ws-")
    return base_url.replace("api.", "ws.")


def remove_none_values(d: dict) -> dict:
    return {k: v for k, v in d.items() if v is not None}


def dump_exclude_none(d: Any) -> Any:
    if d is None:
        return d
    elif isinstance(d, BaseModel):
        return dump_exclude_none(d.model_dump(exclude_none=True))
    elif isinstance(d, Enum):
        return d.value
    elif isinstance(d, dict):
        return {k: dump_exclude_none(v) for k, v in d.items() if v is not None}
    elif isinstance(d, list):
        return [dump_exclude_none(v) for v in d if v is not None]
    else:
        return d


def write_pcm_to_wav_file(
    pcm_data: bytes, filepath: str, channels: int = 1, sample_width: int = 2, frame_rate: int = 24000
):
    """
    Save PCM binary data to WAV file

    :param pcm_data: PCM binary data (24kHz, 16-bit, 1 channel, little-endian)
    :param filepath: Output WAV filename
    """

    with wave.open(filepath, "wb") as wav_file:
        # Set WAV file parameters
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(frame_rate)

        # Write PCM data
        wav_file.writeframes(pcm_data)


def get_methods(cls, prefix="on"):
    """
    Get all methods of `cls` with prefix `prefix`
    """
    method_list = []
    for name in dir(cls):
        if not name.startswith(prefix):
            continue

        attr = getattr(cls, name)
        if inspect.ismethod(attr) or inspect.isfunction(attr):
            sig = inspect.signature(attr)
            params = list(sig.parameters.values())

            if inspect.ismethod(attr) and not isinstance(attr, staticmethod):
                params = params[1:]  # 去掉self/cls

            method_list.append(
                {
                    "function": attr,
                    "parameters": params,
                    "type": "staticmethod"
                    if isinstance(attr, staticmethod)
                    else "classmethod"
                    if inspect.ismethod(attr)
                    else "instancemethod",
                }
            )
    return method_list


def get_model_default(model: type, field_name: str):
    """
    Get default value of a field from `model` which is subclass of BaseModel
    """
    if issubclass(model, BaseModel):
        field = model.model_fields.get(field_name)
        if not field:
            return None

        if field.default_factory is not None:
            return field.default_factory()  # type: ignore

        return field.default if field.default is not None else None
    return None
