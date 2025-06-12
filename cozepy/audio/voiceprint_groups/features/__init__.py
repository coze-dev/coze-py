from typing import List, Optional

from cozepy.files import FileTypes, _try_fix_file
from cozepy.model import AsyncNumberPaged, CozeModel, HTTPRequest, NumberPaged, NumberPagedResponse
from cozepy.request import Requester
from cozepy.util import remove_none_values, remove_url_trailing_slash


class VoicePrintGroupFeature(CozeModel):
    id: str
    group_id: str
    name: str
    audio_url: str
    created_at: int
    updated_at: int
    desc: str
    icon_url: str


class FeatureScore(CozeModel):
    feature_id: str
    feature_name: str
    feature_desc: str
    score: float


class CreateVoicePrintGroupFeatureResp(CozeModel):
    id: str


class UpdateVoicePrintGroupFeatureResp(CozeModel):
    pass


class DeleteVoicePrintGroupFeatureResp(CozeModel):
    pass


class SpeakerIdentifyResp(CozeModel):
    feature_score_list: List[FeatureScore]


class _PrivateListVoicePrintGroupFeatureData(CozeModel, NumberPagedResponse[VoicePrintGroupFeature]):
    items: List[VoicePrintGroupFeature]
    total: int

    def get_total(self) -> Optional[int]:
        return self.total

    def get_has_more(self) -> Optional[bool]:
        return None

    def get_items(self) -> List[VoicePrintGroupFeature]:
        return self.items


class VoiceprintGroupsFeaturesClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    def create(
        self,
        *,
        group_id: str,
        name: str,
        desc: str,
        file: FileTypes,
        **kwargs,
    ) -> CreateVoicePrintGroupFeatureResp:
        url = f"{self._base_url}/v1/audio/voiceprint_groups/{group_id}/features"
        headers: Optional[dict] = kwargs.get("headers")
        files = {"file": _try_fix_file(file)}
        body = remove_none_values(
            {
                "name": name,
                "desc": desc,
            }
        )

        return self._requester.request(
            "post", url, False, cast=CreateVoicePrintGroupFeatureResp, headers=headers, body=body, files=files
        )

    def update(
        self,
        *,
        group_id: str,
        name: str,
        desc: str,
        file: FileTypes,
        **kwargs,
    ) -> UpdateVoicePrintGroupFeatureResp:
        url = f"{self._base_url}/v1/audio/voiceprint_groups/{group_id}/features"
        headers: Optional[dict] = kwargs.get("headers")
        files = {"file": _try_fix_file(file)}
        body = remove_none_values(
            {
                "name": name,
                "desc": desc,
            }
        )

        return self._requester.request(
            "put", url, False, cast=UpdateVoicePrintGroupFeatureResp, headers=headers, body=body, files=files
        )

    def delete(
        self,
        *,
        group_id: str,
        feature_id: str,
        **kwargs,
    ) -> DeleteVoicePrintGroupFeatureResp:
        url = f"{self._base_url}/v1/audio/voiceprint_groups/{group_id}/features/{feature_id}"
        headers: Optional[dict] = kwargs.get("headers")

        return self._requester.request("delete", url, False, cast=DeleteVoicePrintGroupFeatureResp, headers=headers)

    def list(
        self,
        *,
        group_id: str,
        page_num: int = 1,
        page_size: int = 100,
    ) -> NumberPaged[VoicePrintGroupFeature]:
        url = f"{self._base_url}/v1/audio/voiceprint_groups/{group_id}/features"

        def request_maker(i_page_num: int, i_page_size: int) -> HTTPRequest:
            return self._requester.make_request(
                "GET",
                url,
                params=remove_none_values(
                    {
                        "page_num": i_page_num,
                        "page_size": i_page_size,
                    }
                ),
                cast=_PrivateListVoicePrintGroupFeatureData,
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
        top_k: int,
        file: FileTypes,
        **kwargs,
    ) -> SpeakerIdentifyResp:
        url = f"{self._base_url}/v1/audio/voiceprint_groups/{group_id}/speaker_identify"
        headers: Optional[dict] = kwargs.get("headers")
        files = {"file": _try_fix_file(file)}
        body = remove_none_values(
            {
                "top_k": top_k,
            }
        )

        return self._requester.request(
            "post", url, False, cast=SpeakerIdentifyResp, headers=headers, body=body, files=files
        )


class AsyncVoiceprintGroupsFeaturesClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    async def create(
        self,
        *,
        group_id: str,
        name: str,
        desc: str,
        file: FileTypes,
        **kwargs,
    ) -> CreateVoicePrintGroupFeatureResp:
        url = f"{self._base_url}/v1/audio/voiceprint_groups/{group_id}/features"
        headers: Optional[dict] = kwargs.get("headers")
        files = {"file": _try_fix_file(file)}
        body = remove_none_values(
            {
                "name": name,
                "desc": desc,
            }
        )

        return await self._requester.arequest(
            "post", url, False, cast=CreateVoicePrintGroupFeatureResp, headers=headers, body=body, files=files
        )

    async def update(
        self,
        *,
        group_id: str,
        name: str,
        desc: str,
        file: FileTypes,
        **kwargs,
    ) -> UpdateVoicePrintGroupFeatureResp:
        url = f"{self._base_url}/v1/audio/voiceprint_groups/{group_id}/features"
        headers: Optional[dict] = kwargs.get("headers")
        files = {"file": _try_fix_file(file)}
        body = remove_none_values(
            {
                "name": name,
                "desc": desc,
            }
        )

        return await self._requester.arequest(
            "put", url, False, cast=UpdateVoicePrintGroupFeatureResp, headers=headers, body=body, files=files
        )

    async def delete(
        self,
        *,
        group_id: str,
        feature_id: str,
        **kwargs,
    ) -> DeleteVoicePrintGroupFeatureResp:
        url = f"{self._base_url}/v1/audio/voiceprint_groups/{group_id}/features/{feature_id}"
        headers: Optional[dict] = kwargs.get("headers")

        return await self._requester.arequest(
            "delete", url, False, cast=DeleteVoicePrintGroupFeatureResp, headers=headers
        )

    async def list(
        self,
        *,
        group_id: str,
        page_num: int = 1,
        page_size: int = 100,
    ) -> AsyncNumberPaged[VoicePrintGroupFeature]:
        url = f"{self._base_url}/v1/audio/voiceprint_groups/{group_id}/features"

        async def request_maker(i_page_num: int, i_page_size: int) -> HTTPRequest:
            return await self._requester.amake_request(
                "GET",
                url,
                params=remove_none_values(
                    {
                        "page_num": i_page_num,
                        "page_size": i_page_size,
                    }
                ),
                cast=_PrivateListVoicePrintGroupFeatureData,
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
        top_k: int,
        file: FileTypes,
        **kwargs,
    ) -> SpeakerIdentifyResp:
        url = f"{self._base_url}/v1/audio/voiceprint_groups/{group_id}/speaker_identify"
        headers: Optional[dict] = kwargs.get("headers")
        files = {"file": _try_fix_file(file)}
        body = remove_none_values(
            {
                "top_k": top_k,
            }
        )

        return await self._requester.arequest(
            "post", url, False, cast=SpeakerIdentifyResp, headers=headers, body=body, files=files
        )
