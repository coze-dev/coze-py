from typing import List, Optional

from cozepy.model import AsyncNumberPaged, CozeModel, DynamicStrEnum, HTTPRequest, NumberPaged, NumberPagedResponse
from cozepy.request import Requester
from cozepy.util import dump_exclude_none, remove_url_trailing_slash


class FolderType(DynamicStrEnum):
    DEVELOPMENT = "development"  # 项目开发
    LIBRARY = "library"  # 资源库


class SimpleFolder(CozeModel):
    id: str
    name: str
    description: str
    workspace_id: str
    creator_user_id: str
    folder_type: FolderType

    parent_folder_id: Optional[str] = None
    children_count: Optional[int] = None


class _PrivateListFoldersData(CozeModel, NumberPagedResponse[SimpleFolder]):
    total_count: int
    items: List[SimpleFolder]

    def get_total(self) -> Optional[int]:
        return self.total_count

    def get_has_more(self) -> Optional[bool]:
        return None

    def get_items(self) -> List[SimpleFolder]:
        return self.items


class FoldersClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    def retrieve(
        self,
        *,
        folder_id: str,
        **kwargs,
    ) -> SimpleFolder:
        url = f"{self._base_url}/v1/folders/{folder_id}"
        headers: Optional[dict] = kwargs.get("headers")
        return self._requester.request("GET", url, stream=False, cast=SimpleFolder, headers=headers)

    def list(
        self,
        *,
        workspace_id: str,
        folder_type: FolderType,
        parent_folder_id: Optional[str] = None,
        page_num: int = 1,
        page_size: int = 20,
        **kwargs,
    ) -> NumberPaged[SimpleFolder]:
        url = f"{self._base_url}/v1/folders"
        headers: Optional[dict] = kwargs.get("headers")

        def request_maker(i_page_num: int, i_page_size: int) -> HTTPRequest:
            return self._requester.make_request(
                "GET",
                url,
                headers=headers,
                params=dump_exclude_none(
                    {
                        "page_size": i_page_size,
                        "page_num": i_page_num,
                        "workspace_id": workspace_id,
                        "folder_type": folder_type,
                        "parent_folder_id": parent_folder_id,
                    }
                ),
                cast=_PrivateListFoldersData,
                stream=False,
            )

        return NumberPaged(
            page_num=page_num,
            page_size=page_size,
            requestor=self._requester,
            request_maker=request_maker,
        )


class AsyncFoldersClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    async def retrieve(
        self,
        *,
        folder_id: str,
        **kwargs,
    ) -> SimpleFolder:
        url = f"{self._base_url}/v1/folders/{folder_id}"
        headers: Optional[dict] = kwargs.get("headers")
        return await self._requester.arequest("GET", url, stream=False, cast=SimpleFolder, headers=headers)

    async def list(
        self,
        *,
        workspace_id: str,
        folder_type: FolderType,
        parent_folder_id: Optional[str] = None,
        page_num: int = 1,
        page_size: int = 20,
        **kwargs,
    ) -> AsyncNumberPaged[SimpleFolder]:
        url = f"{self._base_url}/v1/folders"
        headers: Optional[dict] = kwargs.get("headers")

        async def request_maker(i_page_num: int, i_page_size: int) -> HTTPRequest:
            return await self._requester.amake_request(
                "GET",
                url,
                headers=headers,
                params=dump_exclude_none(
                    {
                        "page_size": i_page_size,
                        "page_num": i_page_num,
                        "workspace_id": workspace_id,
                        "folder_type": folder_type,
                        "parent_folder_id": parent_folder_id,
                    }
                ),
                cast=_PrivateListFoldersData,
                stream=False,
            )

        return await AsyncNumberPaged.build(
            page_num=page_num,
            page_size=page_size,
            requestor=self._requester,
            request_maker=request_maker,
        )
