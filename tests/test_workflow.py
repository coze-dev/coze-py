import httpx
import pytest

from cozepy import Coze, TokenAuth, WorkflowRunResult


@pytest.mark.respx(base_url="https://api.coze.com")
class TestWorkflowsRuns:
    def test_create(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        respx_mock.post("/v1/workflow/run").mock(
            httpx.Response(200, json={"data": WorkflowRunResult(debug_url="debug_url", data="data").model_dump()})
        )

        res = coze.workflows.runs.create(workflow_id="id")
        assert res
        assert res.data == "data"
