import platform
import sys
from functools import lru_cache

VERSION = "0.5.0"


@lru_cache(maxsize=1)
def user_agent():
    python_version = ".".join(map(str, sys.version_info[:2]))

    os_name = platform.system().lower()
    if os_name == "darwin":
        os_name = "macos"

    if os_name == "macos":
        os_version = platform.mac_ver()[0]
    elif os_name == "windows":
        os_version = platform.win32_ver()[0]
    elif os_name == "linux":
        try:
            import distro

            os_version = distro.version(pretty=False, best=True)
        except ImportError:
            os_version = platform.release()
    else:
        os_version = platform.release()

    return f"cozepy/{VERSION} python/{python_version} {os_name}/{os_version}".lower()
