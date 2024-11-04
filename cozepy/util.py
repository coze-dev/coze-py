import base64
import hashlib
import random
import sys
import wave

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


def write_pcm_to_wav_file(
    pcm_data: bytes, filepath: str, channels: int = 1, sample_width: int = 2, frame_rate: int = 24000
):
    """
    Save PCM binary data to WAV file

    :param pcm_data: PCM binary data (24kHz, 16-bit, 1 channel, little-endian)
    :param output_filename: Output WAV filename
    """

    with wave.open(filepath, "wb") as wav_file:
        # Set WAV file parameters
        wav_file.setnchannels(channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(frame_rate)

        # Write PCM data
        wav_file.writeframes(pcm_data)
