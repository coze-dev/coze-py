from enum import IntEnum
from typing import List, Optional

from cozepy.datasets.documents import DocumentSourceType
from cozepy.model import AsyncNumberPaged, CozeModel, HTTPRequest, NumberPaged, NumberPagedResponse
from cozepy.request import Requester
from cozepy.util import remove_url_trailing_slash


class PhotoStatus(IntEnum):
    IN_PROCESSING = 0  # In processing
    COMPLETED = 1  # Completed
    PROCESSING_FAILED = 9  # Processing failed


class Photo(CozeModel):
    document_id: str  # The ID of the image.
    url: str = ""  # The URL of the image.
    name: str = ""  # The name of the image.
    size: int = 0  # The size of the image, in bytes.
    type: str = ""  # File format, i.e., file extension, such as jpg, png.
    status: PhotoStatus  # Status of the file. Values include: 0: In processing, 1: Completed, 9: Processing failed, it is recommended to re-upload
    caption: str = ""  # Image description information.
    creator_id: str = ""  # The ID of the creator.
    source_type: DocumentSourceType  # The source type of the image.
    create_time: int = 0  # The creation time of the image.
    update_time: int = 0  # The update time of the image.


class UpdateImageRes(CozeModel):
    pass


class _PrivateListPhotosData(CozeModel, NumberPagedResponse[Photo]):
    photo_infos: List[Photo]
    total_count: int

    def get_total(self) -> Optional[int]:
        return self.total_count

    def get_has_more(self) -> Optional[bool]:
        return None

    def get_items(self) -> List[Photo]:
        return self.photo_infos


class DatasetsImagesClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    def update(
        self,
        *,
        dataset_id: str,
        document_id: str,
        caption: str,
        **kwargs,
    ) -> UpdateImageRes:
        """
        Call this API to update the description of images in the knowledge base.

        docs en: https://www.coze.com/docs/developer_guides/update_image_caption
        docs zh: https://www.coze.cn/docs/developer_guides/update_image_caption

        :param dataset_id: The ID of the knowledge base.
        :param document_id: The ID of the image.
        :param caption: The description of the image.
        :return: None
        """
        url = f"{self._base_url}/v1/datasets/{dataset_id}/images/{document_id}"
        headers: Optional[dict] = kwargs.get("headers")
        body = {
            "caption": caption,
        }
        return self._requester.request("put", url, False, cast=UpdateImageRes, headers=headers, body=body)

    def list(
        self,
        *,
        dataset_id: str,
        keyword: Optional[str] = None,
        has_caption: Optional[bool] = None,
        page_num: int = 1,
        page_size: int = 10,
        **kwargs,
    ) -> NumberPaged[Photo]:
        """
        Call this API to view detailed information of images in the image knowledge base.
        When viewing images, it is supported to filter through image annotations.

        docs en: https://www.coze.com/docs/developer_guides/get_images
        docs zh: https://www.coze.cn/docs/developer_guides/get_images

        :param dataset_id: The ID of the knowledge base.
        :param keyword: The keyword to filter images.
        :param has_caption: Whether the image has a caption.
        :param page_num: The page number for paginated queries. Default is 1, meaning the data return starts from the
        first page.
        :param page_size: The size of pagination. Default is 10, meaning that 10 data entries are returned per page. The value range is 1~299, with a default of 10.
        """
        url = f"{self._base_url}/v1/datasets/{dataset_id}/images"
        headers: Optional[dict] = kwargs.get("headers")

        def request_maker(i_page_num: int, i_page_size: int) -> HTTPRequest:
            return self._requester.make_request(
                "get",
                url,
                headers=headers,
                params={
                    "page_num": i_page_num,
                    "page_size": i_page_size,
                    "keyword": keyword,
                    "has_caption": has_caption,
                },
                cast=_PrivateListPhotosData,
                stream=False,
            )

        return NumberPaged(
            page_num=page_num,
            page_size=page_size,
            requestor=self._requester,
            request_maker=request_maker,
        )


class AsyncDatasetsImagesClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    async def update(
        self,
        *,
        dataset_id: str,
        document_id: str,
        caption: str,
        **kwargs,
    ) -> UpdateImageRes:
        """
        Call this API to update the description of images in the knowledge base.

        docs en: https://www.coze.com/docs/developer_guides/update_image_caption
        docs zh: https://www.coze.cn/docs/developer_guides/update_image_caption

        :param dataset_id: The ID of the knowledge base.
        :param document_id: The ID of the image.
        :param caption: The description of the image.
        :return: None
        """
        url = f"{self._base_url}/v1/datasets/{dataset_id}/images/{document_id}"
        headers: Optional[dict] = kwargs.get("headers")
        body = {
            "caption": caption,
        }
        return await self._requester.arequest("put", url, False, cast=UpdateImageRes, headers=headers, body=body)

    async def list(
        self,
        *,
        dataset_id: str,
        keyword: Optional[str] = None,
        has_caption: Optional[bool] = None,
        page_num: int = 1,
        page_size: int = 10,
        **kwargs,
    ) -> AsyncNumberPaged[Photo]:
        """
        Call this API to view detailed information of images in the image knowledge base.
        When viewing images, it is supported to filter through image annotations.

        docs en: https://www.coze.com/docs/developer_guides/get_images
        docs zh: https://www.coze.cn/docs/developer_guides/get_images

        :param dataset_id: The ID of the knowledge base.
        :param keyword: The keyword to filter images.
        :param has_caption: Whether the image has a caption.
        :param page_num: The page number for paginated queries. Default is 1, meaning the data return starts from the
        first page.
        :param page_size: The size of pagination. Default is 10, meaning that 10 data entries are returned per page. The value range is 1~299, with a default of 10.
        """
        url = f"{self._base_url}/v1/datasets/{dataset_id}/images"
        headers: Optional[dict] = kwargs.get("headers")

        async def request_maker(i_page_num: int, i_page_size: int) -> HTTPRequest:
            return await self._requester.amake_request(
                "get",
                url,
                headers=headers,
                params={
                    "page_num": i_page_num,
                    "page_size": i_page_size,
                    "keyword": keyword,
                    "has_caption": has_caption,
                },
                cast=_PrivateListPhotosData,
                stream=False,
            )

        return await AsyncNumberPaged.build(
            page_num=page_num,
            page_size=page_size,
            requestor=self._requester,
            request_maker=request_maker,
        )
