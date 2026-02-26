from typing import List, Optional

from cozepy.model import AsyncNumberPaged, CozeModel, NumberPaged, NumberPagedResponse
from cozepy.request import HTTPRequest, Requester
from cozepy.util import remove_none_values, remove_url_trailing_slash


class BenefitBillTask(CozeModel):
    # 创建时间，Unix 时间戳
    created_at: Optional[int] = None
    # 结束时间，Unix 时间戳
    ended_at: Optional[int] = None
    # 过期时间，Unix 时间戳
    expires_at: Optional[int] = None
    file_urls: Optional[List[str]] = None
    # 开始时间，Unix 时间戳
    started_at: Optional[int] = None
    status: Optional[str] = None
    task_id: Optional[str] = None


class _PrivateListBenefitBillTasksData(CozeModel, NumberPagedResponse[BenefitBillTask]):
    task_infos: List[BenefitBillTask]
    total: int

    def get_total(self) -> Optional[int]:
        return self.total

    def get_has_more(self) -> Optional[bool]:
        return None

    def get_items(self) -> List[BenefitBillTask]:
        return self.task_infos


class CommerceBenefitClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    def list_bill_tasks(
        self,
        *,
        task_ids: Optional[List[str]] = None,
        page_num: int = 1,
        page_size: int = 20,
        **kwargs,
    ) -> NumberPaged[BenefitBillTask]:
        url = f"{self._base_url}/v1/commerce/benefit/bill_tasks"
        headers: Optional[dict] = kwargs.get("headers")

        def request_maker(i_page_num: int, i_page_size: int) -> HTTPRequest:
            return self._requester.make_request(
                "GET",
                url,
                headers=headers,
                params=remove_none_values(
                    {
                        "task_ids": ",".join(task_ids) if task_ids else None,
                        "page_num": i_page_num,
                        "page_size": i_page_size,
                    }
                ),
                cast=_PrivateListBenefitBillTasksData,
                stream=False,
            )

        return NumberPaged(
            page_num=page_num,
            page_size=page_size,
            requestor=self._requester,
            request_maker=request_maker,
        )


class AsyncCommerceBenefitClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    async def list_bill_tasks(
        self,
        *,
        task_ids: Optional[List[str]] = None,
        page_num: int = 1,
        page_size: int = 20,
        **kwargs,
    ) -> AsyncNumberPaged[BenefitBillTask]:
        url = f"{self._base_url}/v1/commerce/benefit/bill_tasks"
        headers: Optional[dict] = kwargs.get("headers")

        async def request_maker(i_page_num: int, i_page_size: int) -> HTTPRequest:
            return await self._requester.amake_request(
                "GET",
                url,
                headers=headers,
                params=remove_none_values(
                    {
                        "task_ids": ",".join(task_ids) if task_ids else None,
                        "page_num": i_page_num,
                        "page_size": i_page_size,
                    }
                ),
                cast=_PrivateListBenefitBillTasksData,
                stream=False,
            )

        return await AsyncNumberPaged.build(
            page_num=page_num,
            page_size=page_size,
            requestor=self._requester,
            request_maker=request_maker,
        )
