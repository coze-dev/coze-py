import httpx
import pytest

from cozepy import AsyncCoze, AsyncTokenAuth, Coze, TokenAuth


def make_task(task_id: str) -> dict:
    return {
        "task_id": task_id,
        "status": "finished",
    }


def mock_list_bill_tasks(respx_mock, page_num: int, page_size: int, total: int, task_id: str):
    return respx_mock.get(
        "/v1/commerce/benefit/bill_tasks",
        params={
            "task_ids": "task_1,task_2",
            "page_num": page_num,
            "page_size": page_size,
        },
    ).mock(
        httpx.Response(
            200,
            json={
                "data": {
                    "task_infos": [make_task(task_id)],
                    "total": total,
                }
            },
        )
    )


@pytest.mark.respx(base_url="https://api.coze.com")
class TestSyncBillTasks:
    def test_sync_bill_tasks_list(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        mock_list_bill_tasks(respx_mock, page_num=1, page_size=1, total=2, task_id="task_1")
        mock_list_bill_tasks(respx_mock, page_num=2, page_size=1, total=2, task_id="task_2")

        pager = coze.bill_tasks.list(task_ids=["task_1", "task_2"], page_num=1, page_size=1)
        assert pager

        result_ids = []
        for item in pager:
            result_ids.append(item.task_id)

        assert result_ids == ["task_1", "task_2"]


@pytest.mark.respx(base_url="https://api.coze.com")
@pytest.mark.asyncio
class TestAsyncBillTasks:
    async def test_async_bill_tasks_list(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        mock_list_bill_tasks(respx_mock, page_num=1, page_size=1, total=2, task_id="task_1")
        mock_list_bill_tasks(respx_mock, page_num=2, page_size=1, total=2, task_id="task_2")

        pager = await coze.bill_tasks.list(task_ids=["task_1", "task_2"], page_num=1, page_size=1)
        assert pager

        result_ids = []
        async for item in pager:
            result_ids.append(item.task_id)

        assert result_ids == ["task_1", "task_2"]
