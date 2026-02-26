import httpx
import pytest

from cozepy import AsyncCoze, AsyncTokenAuth, BenefitBillTask, Coze, TokenAuth
from cozepy.util import random_hex
from tests.test_util import logid_key


def mock_benefit_bill_task(task_id: str) -> BenefitBillTask:
    return BenefitBillTask(
        task_id=task_id,
        status="succeed",
        started_at=1743004800,
        ended_at=1743091200,
        created_at=1743094800,
        expires_at=1743703200,
        file_urls=[f"https://example.com/{task_id}.csv"],
    )


def mock_list_bill_tasks(respx_mock, total_count, page, task_ids):
    logid = random_hex(10)
    task_id = f"task_{page}"
    respx_mock.get(
        "/v1/commerce/benefit/bill_tasks",
        params={
            "task_ids": ",".join(task_ids),
            "page_num": page,
            "page_size": 1,
        },
    ).mock(
        httpx.Response(
            200,
            json={
                "data": {
                    "task_infos": [mock_benefit_bill_task(task_id).model_dump()],
                    "total": total_count,
                }
            },
            headers={logid_key(): logid},
        )
    )
    return logid


@pytest.mark.respx(base_url="https://api.coze.com")
class TestSyncBillTasks:
    def test_sync_bill_tasks_list(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        task_ids = ["task_a", "task_b"]
        total = 5
        size = 1
        for idx in range(total):
            mock_list_bill_tasks(respx_mock, total_count=total, page=idx + 1, task_ids=task_ids)

        resp = coze.bill_tasks.list(task_ids=task_ids, page_num=1, page_size=1)
        assert resp
        assert resp.has_more is True

        total_result = 0
        for task in resp:
            total_result += 1
            assert task
            assert task.task_id == f"task_{total_result}"
            assert task.status == "succeed"
        assert total_result == total

        total_result = 0
        for page in resp.iter_pages():
            total_result += 1
            assert page
            assert page.has_more == (total_result < total)
            assert len(page.items) == size
            task = page.items[0]
            assert task.task_id == f"task_{total_result}"
            assert task.response.logid is not None
        assert total_result == total


@pytest.mark.respx(base_url="https://api.coze.com")
@pytest.mark.asyncio
class TestAsyncBillTasks:
    async def test_async_bill_tasks_list(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        task_ids = ["task_a", "task_b"]
        total = 5
        size = 1
        for idx in range(total):
            mock_list_bill_tasks(respx_mock, total_count=total, page=idx + 1, task_ids=task_ids)

        resp = await coze.bill_tasks.list(task_ids=task_ids, page_num=1, page_size=1)
        assert resp
        assert resp.has_more is True

        total_result = 0
        async for task in resp:
            total_result += 1
            assert task
            assert task.task_id == f"task_{total_result}"
            assert task.status == "succeed"
        assert total_result == total

        total_result = 0
        async for page in resp.iter_pages():
            total_result += 1
            assert page
            assert page.has_more == (total_result < total)
            assert len(page.items) == size
            task = page.items[0]
            assert task.task_id == f"task_{total_result}"
            assert task.response.logid is not None
        assert total_result == total
