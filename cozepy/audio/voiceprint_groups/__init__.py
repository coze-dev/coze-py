from typing import TYPE_CHECKING, List, Optional

from cozepy.audio.voiceprint_groups.features import UserInfo
from cozepy.files import FileTypes, _try_fix_file
from cozepy.model import AsyncNumberPaged, CozeModel, HTTPRequest, NumberPaged, NumberPagedResponse
from cozepy.request import Requester
from cozepy.util import remove_none_values, remove_url_trailing_slash

if TYPE_CHECKING:
    from .features import AsyncVoiceprintGroupsFeaturesClient, VoiceprintGroupsFeaturesClient


class CreateVoicePrintGroupResp(CozeModel):
    id: str


class UpdateVoicePrintGroupResp(CozeModel):
    pass


class DeleteVoicePrintGroupResp(CozeModel):
    pass


class VoicePrintGroup(CozeModel):
    id: str
    name: str
    desc: str
    created_at: int
    updated_at: int
    icon_url: str
    feature_count: int
    user_info: UserInfo


class FeatureScore(CozeModel):
    feature_id: str
    feature_name: str
    feature_desc: str
    score: float


class SpeakerIdentifyResp(CozeModel):
    feature_score_list: List[FeatureScore]


class _PrivateListVoicePrintGroupData(CozeModel, NumberPagedResponse[VoicePrintGroup]):
    items: List[VoicePrintGroup]
    total: int

    def get_total(self) -> Optional[int]:
        return self.total

    def get_has_more(self) -> Optional[bool]:
        return None

    def get_items(self) -> List[VoicePrintGroup]:
        return self.items


class VoiceprintGroupsClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

        self._features: Optional[VoiceprintGroupsFeaturesClient] = None

    @property
    def features(self) -> "VoiceprintGroupsFeaturesClient":
        if self._features is None:
            from .features import VoiceprintGroupsFeaturesClient

            self._features = VoiceprintGroupsFeaturesClient(base_url=self._base_url, requester=self._requester)
        return self._features

    def create(
        self,
        *,
        name: str,
        desc: Optional[str] = None,
        **kwargs,
    ) -> CreateVoicePrintGroupResp:
        url = f"{self._base_url}/v1/audio/voiceprint_groups"
        headers: Optional[dict] = kwargs.get("headers")
        body = remove_none_values(
            {
                "name": name,
                "desc": desc,
            }
        )

        return self._requester.request("post", url, False, cast=CreateVoicePrintGroupResp, headers=headers, body=body)

    def update(
        self,
        *,
        group_id: str,
        name: Optional[str] = None,
        desc: Optional[str] = None,
        **kwargs,
    ) -> UpdateVoicePrintGroupResp:
        url = f"{self._base_url}/v1/audio/voiceprint_groups/{group_id}"
        headers: Optional[dict] = kwargs.get("headers")
        body = remove_none_values(
            {
                "name": name,
                "desc": desc,
            }
        )

        return self._requester.request("put", url, False, cast=UpdateVoicePrintGroupResp, headers=headers, body=body)

    def delete(
        self,
        *,
        group_id: str,
        **kwargs,
    ) -> DeleteVoicePrintGroupResp:
        url = f"{self._base_url}/v1/audio/voiceprint_groups/{group_id}"
        headers: Optional[dict] = kwargs.get("headers")

        return self._requester.request("delete", url, False, cast=DeleteVoicePrintGroupResp, headers=headers)

    def list(
        self,
        *,
        name: Optional[str] = None,
        group_id: Optional[str] = None,
        user_id: Optional[str] = None,
        page_num: int = 1,
        page_size: int = 10,
    ) -> NumberPaged[VoicePrintGroup]:
        """
        Get available voices, including system voices + user cloned voices
        Tips: Voices cloned under each Volcano account can be reused within the team

        :param filter_system_voice: If True, system voices will not be returned.
        :param page_num: The page number for paginated queries. Default is 1, meaning the data return starts from the
        first page.
        :param page_size: The size of pagination. Default is 100, meaning that 100 data entries are returned per page.
        :return: list of Voice
        """
        url = f"{self._base_url}/v1/audio/voiceprint_groups"

        def request_maker(i_page_num: int, i_page_size: int) -> HTTPRequest:
            return self._requester.make_request(
                "GET",
                url,
                params=remove_none_values(
                    {
                        "name": name,
                        "group_id": group_id,
                        "user_id": user_id,
                        "page_num": i_page_num,
                        "page_size": i_page_size,
                    }
                ),
                cast=_PrivateListVoicePrintGroupData,
                stream=False,
            )

        return NumberPaged(
            page_num=page_num,
            page_size=page_size,
            requestor=self._requester,
            request_maker=request_maker,
        )

    def speaker_identify(
        self,
        *,
        group_id: str,
        file: FileTypes,
        top_k: Optional[int] = None,
        sample_rate: Optional[int] = None,
        channel: Optional[int] = None,
        **kwargs,
    ) -> SpeakerIdentifyResp:
        url = f"{self._base_url}/v1/audio/voiceprint_groups/{group_id}/speaker_identify"
        headers: Optional[dict] = kwargs.get("headers")
        files = {"file": _try_fix_file(file)}
        body = remove_none_values(
            {
                "top_k": top_k,
                "sample_rate": sample_rate,
                "channel": channel,
            }
        )

        return self._requester.request(
            "post", url, False, cast=SpeakerIdentifyResp, headers=headers, body=body, files=files
        )


class AsyncVoiceprintGroupsClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

        self._features: Optional[AsyncVoiceprintGroupsFeaturesClient] = None

    @property
    def features(self) -> "AsyncVoiceprintGroupsFeaturesClient":
        if self._features is None:
            from .features import AsyncVoiceprintGroupsFeaturesClient

            self._features = AsyncVoiceprintGroupsFeaturesClient(base_url=self._base_url, requester=self._requester)
        return self._features

    async def create(
        self,
        *,
        name: str,
        desc: Optional[str] = None,
        **kwargs,
    ) -> CreateVoicePrintGroupResp:
        url = f"{self._base_url}/v1/audio/voiceprint_groups"
        headers: Optional[dict] = kwargs.get("headers")
        body = remove_none_values(
            {
                "name": name,
                "desc": desc,
            }
        )

        return await self._requester.arequest(
            "post", url, False, cast=CreateVoicePrintGroupResp, headers=headers, body=body
        )

    async def update(
        self,
        *,
        group_id: str,
        name: Optional[str] = None,
        desc: Optional[str] = None,
        **kwargs,
    ) -> UpdateVoicePrintGroupResp:
        url = f"{self._base_url}/v1/audio/voiceprint_groups/{group_id}"
        headers: Optional[dict] = kwargs.get("headers")
        body = remove_none_values(
            {
                "name": name,
                "desc": desc,
            }
        )

        return await self._requester.arequest(
            "put", url, False, cast=UpdateVoicePrintGroupResp, headers=headers, body=body
        )

    async def delete(
        self,
        *,
        group_id: str,
        **kwargs,
    ) -> DeleteVoicePrintGroupResp:
        url = f"{self._base_url}/v1/audio/voiceprint_groups/{group_id}"
        headers: Optional[dict] = kwargs.get("headers")

        return await self._requester.arequest("delete", url, False, cast=DeleteVoicePrintGroupResp, headers=headers)

    async def list(
        self,
        *,
        name: Optional[str] = None,
        group_id: Optional[str] = None,
        user_id: Optional[str] = None,
        page_num: int = 1,
        page_size: int = 100,
    ) -> AsyncNumberPaged[VoicePrintGroup]:
        """
        Get available voices, including system voices + user cloned voices
        Tips: Voices cloned under each Volcano account can be reused within the team

        :param filter_system_voice: If True, system voices will not be returned.
        :param page_num: The page number for paginated queries. Default is 1, meaning the data return starts from the
        first page.
        :param page_size: The size of pagination. Default is 100, meaning that 100 data entries are returned per page.
        :return: list of Voice
        """
        url = f"{self._base_url}/v1/audio/voiceprint_groups"

        async def request_maker(i_page_num: int, i_page_size: int) -> HTTPRequest:
            return await self._requester.amake_request(
                "GET",
                url,
                params=remove_none_values(
                    {
                        "name": name,
                        "group_id": group_id,
                        "user_id": user_id,
                        "page_num": i_page_num,
                        "page_size": i_page_size,
                    }
                ),
                cast=_PrivateListVoicePrintGroupData,
                stream=False,
            )

        return await AsyncNumberPaged.build(
            page_num=page_num,
            page_size=page_size,
            requestor=self._requester,
            request_maker=request_maker,
        )

    async def speaker_identify(
        self,
        *,
        group_id: str,
        file: FileTypes,
        top_k: Optional[int] = None,
        sample_rate: Optional[int] = None,
        channel: Optional[int] = None,
        **kwargs,
    ) -> SpeakerIdentifyResp:
        url = f"{self._base_url}/v1/audio/voiceprint_groups/{group_id}/speaker_identify"
        headers: Optional[dict] = kwargs.get("headers")
        files = {"file": _try_fix_file(file)}
        body = remove_none_values(
            {
                "top_k": top_k,
                "sample_rate": sample_rate,
                "channel": channel,
            }
        )

        return await self._requester.arequest(
            "post", url, False, cast=SpeakerIdentifyResp, headers=headers, body=body, files=files
        )
