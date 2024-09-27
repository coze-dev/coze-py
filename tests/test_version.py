from cozepy import VERSION
from cozepy.version import user_agent


def test_user_agent():
    res = user_agent()
    assert f"cozepy/{VERSION}" in res
    assert "python" in res
