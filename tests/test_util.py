from cozepy.util import base64_encode_string


def test_base64_encode_string():
    assert "aGk=" == base64_encode_string("hi")
