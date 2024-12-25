from typing import Optional

from cozepy.auth import Auth
from cozepy.files import FileTypes, _try_fix_file
from cozepy.model import CozeModel
from cozepy.request import Requester
from cozepy.util import remove_url_trailing_slash


class CreateTranslationResp(CozeModel):
    # The text of translation
    text: str


class TranslationsClient(object):
    def __init__(self, base_url: str, auth: Auth, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._auth = auth
        self._requester = requester

    def create(
        self,
        *,
        file: FileTypes,
        **kwargs,
    ) -> CreateTranslationResp:
        """
        create translation

        :param file: The file to be translated.
        :return: create translation result
        """
        url = f"{self._base_url}/v1/audio/translations"
        headers: Optional[dict] = kwargs.get("headers")
        files = {"file": _try_fix_file(file)}
        return self._requester.request(
            "post", url, stream=False, cast=CreateTranslationResp, headers=headers, files=files
        )


class AsyncTranslationsClient(object):
    """
    Room service async client.
    """

    def __init__(self, base_url: str, auth: Auth, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._auth = auth
        self._requester = requester

    async def create(
        self,
        *,
        file: FileTypes,
        **kwargs,
    ) -> CreateTranslationResp:
        """
        create translation

        :param file: The file to be translated.
        :return: create translation result
        """
        url = f"{self._base_url}/v1/audio/translations"
        files = {"file": _try_fix_file(file)}
        headers: Optional[dict] = kwargs.get("headers")
        return await self._requester.arequest(
            "post", url, stream=False, cast=CreateTranslationResp, headers=headers, files=files
        )
