from typing import List, Optional, Union

from cozepy import AudioFormat
from cozepy.auth import Auth
from cozepy.model import AsyncNumberPaged, CozeModel, HTTPRequest, NumberPaged, NumberPagedResponse
from cozepy.request import Requester
from cozepy.util import remove_url_trailing_slash


class Voice(CozeModel):
    # The id of voice
    voice_id: str

    # The name of voice
    name: str

    # If is system voice
    is_system_voice: bool

    # Language code
    language_code: str

    # Language name
    language_name: str

    # Preview text for the voice
    preview_text: str

    # Preview audio URL for the voice
    preview_audio: str

    # Number of remaining training times available for current voice
    available_training_times: int

    # Voice creation timestamp
    create_time: int

    # Voice last update timestamp
    update_time: int


class _PrivateListVoiceData(CozeModel, NumberPagedResponse[Voice]):
    voice_list: List[Voice]
    has_more: bool

    def get_total(self) -> Optional[int]:
        return None

    def get_has_more(self) -> Optional[bool]:
        return self.has_more

    def get_items(self) -> List[Voice]:
        return self.voice_list


class VoicesClient(object):
    def __init__(self, base_url: str, auth: Auth, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._auth = auth
        self._requester = requester

    def clone(
        self,
        *,
        voice_name: str,
        file: Union[str],
        audio_format: AudioFormat,
        language: Optional[str] = None,
        voice_id: Optional[str] = None,
        preview_text: Optional[str] = None,
        text: Optional[str] = None,
        **kwargs,
    ) -> Voice:
        """
        Clone the user's voice, and use the cloned voice to create voice speech
        Each Volcano account is assigned a voice by default. A voice can be cloned 10 times,
        and repeated cloning of the same voice will overwrite it.

        :param voice_name: The name of the cloned voice, cannot be empty, and the length is greater than 6.
        :param file: Audio Files.
        :param audio_format: Only "wav", "mp3", "ogg", "m4a", "aac", "pcm" formats are supported.
        :param language: Only supports "zh", "en" "ja" "es" "id" "pt" languages.
        :param voice_id: If it is passed in, it will be trained on the original voice, covering the previously
        trained voice.
        :param preview_text: If a text is passed in, a preview audio will be generated based on the text.
         Otherwise, the default text "你好，我是你的专属AI克隆声音，希望未来可以一起好好相处哦".
        :param text: Users can recite the text, and the service will compare the audio with the text.
         If the difference is too large, an error will be returned.
        :return: Voice of the cloned.
        """
        url = f"{self._base_url}/v1/audio/voices/clone"
        headers: Optional[dict] = kwargs.get("headers")
        body = {
            "voice_name": voice_name,
            "audio_format": audio_format,
            "language": language,
            "voice_id": voice_id,
            "preview_text": preview_text,
            "text": text,
        }
        files = {"file": file}

        return self._requester.request("post", url, False, Voice, headers=headers, body=body, files=files)

    def list(
        self,
        *,
        filter_system_voice: bool = False,
        page_num: int = 1,
        page_size: int = 100,
    ) -> NumberPaged[Voice]:
        """
        Get available voices, including system voices + user cloned voices
        Tips: Voices cloned under each Volcano account can be reused within the team

        :param filter_system_voice: If True, system voices will not be returned.
        :param page_num: The page number for paginated queries. Default is 1, meaning the data return starts from the
        first page.
        :param page_size: The size of pagination. Default is 100, meaning that 100 data entries are returned per page.
        :return: list of Voice
        """
        url = f"{self._base_url}/v1/audio/voices"

        def request_maker(i_page_num: int, i_page_size: int) -> HTTPRequest:
            return self._requester.make_request(
                "GET",
                url,
                params={
                    "filter_system_voice": filter_system_voice,
                    "page_num": i_page_num,
                    "page_size": i_page_size,
                },
                cast=_PrivateListVoiceData,
                is_async=False,
                stream=False,
            )

        return NumberPaged(
            page_num=page_num,
            page_size=page_size,
            requestor=self._requester,
            request_maker=request_maker,
        )


class AsyncVoicesClient(object):
    def __init__(self, base_url: str, auth: Auth, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._auth = auth
        self._requester = requester

    async def clone(
        self,
        *,
        voice_name: str,
        file: Union[str],
        audio_format: AudioFormat,
        language: Optional[str] = None,
        voice_id: Optional[str] = None,
        preview_text: Optional[str] = None,
        text: Optional[str] = None,
        **kwargs,
    ) -> Voice:
        """
        Clone the user's voice, and use the cloned voice to create voice speech
        Each Volcano account is assigned a voice by default. A voice can be cloned 10 times,
        and repeated cloning of the same voice will overwrite it.

        :param voice_name: The name of the cloned voice, cannot be empty, and the length is greater than 6.
        :param file: Audio Files.
        :param audio_format: Only "wav", "mp3", "ogg", "m4a", "aac", "pcm" formats are supported.
        :param language: Only supports "zh", "en" "ja" "es" "id" "pt" languages.
        :param voice_id: If it is passed in, it will be trained on the original voice, covering the previously
        trained voice.
        :param preview_text: If a text is passed in, a preview audio will be generated based on the text.
         Otherwise, the default text "你好，我是你的专属AI克隆声音，希望未来可以一起好好相处哦".
        :param text: Users can recite the text, and the service will compare the audio with the text.
         If the difference is too large, an error will be returned.
        :return: Voice of the cloned.
        """
        url = f"{self._base_url}/v1/audio/voices/clone"
        headers: Optional[dict] = kwargs.get("headers")
        body = {
            "voice_name": voice_name,
            "audio_format": audio_format,
            "language": language,
            "voice_id": voice_id,
            "preview_text": preview_text,
            "text": text,
        }
        files = {"file": file}

        return await self._requester.arequest("post", url, False, Voice, headers=headers, body=body, files=files)

    async def list(
        self,
        *,
        filter_system_voice: bool = False,
        page_num: int = 1,
        page_size: int = 100,
    ) -> AsyncNumberPaged[Voice]:
        """
        Get available voices, including system voices + user cloned voices
        Tips: Voices cloned under each Volcano account can be reused within the team

        :param filter_system_voice: If True, system voices will not be returned.
        :param page_num: The page number for paginated queries. Default is 1, meaning the data return starts from the
        first page.
        :param page_size: The size of pagination. Default is 100, meaning that 100 data entries are returned per page.
        :return: list of Voice
        """
        url = f"{self._base_url}/v1/audio/voices"

        def request_maker(i_page_num: int, i_page_size: int) -> HTTPRequest:
            return self._requester.make_request(
                "GET",
                url,
                params={
                    "filter_system_voice": filter_system_voice,
                    "page_num": i_page_num,
                    "page_size": i_page_size,
                },
                cast=_PrivateListVoiceData,
                is_async=False,
                stream=False,
            )

        return await AsyncNumberPaged.build(
            page_num=page_num,
            page_size=page_size,
            requestor=self._requester,
            request_maker=request_maker,
        )
