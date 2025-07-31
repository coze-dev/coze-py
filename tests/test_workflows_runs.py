import httpx
import pytest

from cozepy import (
    AsyncCoze,
    AsyncTokenAuth,
    Coze,
    TokenAuth,
    WorkflowEventType,
    WorkflowExecuteStatus,
    WorkflowNodeExecuteHistory,
    WorkflowRunHistory,
    WorkflowRunMode,
    WorkflowRunResult,
)
from cozepy.util import random_hex
from tests.test_util import logid_key, read_file


def mock_create_workflows_runs(respx_mock, is_async: bool):
    res = WorkflowRunResult(
        debug_url="debug_url",
        data="data" if not is_async else None,
        execute_id="execute_id" if is_async else None,
    )
    res._raw_response = httpx.Response(200, json={"data": res.model_dump()}, headers={logid_key(): random_hex(10)})
    respx_mock.post(
        "/v1/workflow/run",
        json={
            "workflow_id": "id",
            "is_async": is_async,
        },
    ).mock(res._raw_response)
    return res


def mock_create_workflows_runs_stream(respx_mock, content: str):
    logid = random_hex(10)
    respx_mock.post("/v1/workflow/stream_run").mock(
        httpx.Response(
            200,
            headers={"content-type": "text/event-stream", logid_key(): logid},
            content=content,
        )
    )
    return logid


def mock_create_workflows_runs_resume(respx_mock, content: str):
    logid = random_hex(10)
    respx_mock.post("/v1/workflow/stream_resume").mock(
        httpx.Response(
            200,
            headers={"content-type": "text/event-stream", logid_key(): logid},
            content=content,
        )
    )
    return logid


def mock_create_workflows_runs_run_histories_retrieve(respx_mock):
    current_logid = "current_logid"
    execute_logid = "execute_logid"
    workflow_id = random_hex(10)
    execute_id = random_hex(10)
    workflow_run_result = WorkflowRunHistory(
        execute_id=execute_id,
        execute_status=WorkflowExecuteStatus.RUNNING,
        bot_id="bot_id",
        connector_id="connector_id",
        connector_uid="connector_uid",
        run_mode=WorkflowRunMode.SYNCHRONOUS,
        logid=execute_logid,
        create_time=0,
        update_time=0,
        output="output",
        error_code=0,
        error_message="error_message",
        debug_url="debug_url",
        is_output_trimmed=False,
    )
    workflow_run_result._raw_response = httpx.Response(
        200,
        json={"data": [workflow_run_result.model_dump()]},
        headers={logid_key(): current_logid},
    )
    url = f"/v1/workflows/{workflow_id}/run_histories/{execute_id}"
    respx_mock.get(url).mock(workflow_run_result._raw_response)
    return workflow_id, execute_id, current_logid, execute_logid


@pytest.mark.respx(base_url="https://api.coze.com")
class TestSyncWorkflowsRuns:
    def test_sync_workflows_runs_create_no_async(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        mock_res = mock_create_workflows_runs(respx_mock, False)

        res = coze.workflows.runs.create(workflow_id="id")
        assert res
        assert res.response.logid == mock_res.response.logid
        assert res.data == "data"

    def test_sync_workflows_runs_create_async(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        mock_res = mock_create_workflows_runs(respx_mock, True)

        res = coze.workflows.runs.create(workflow_id="id", is_async=True)
        assert res
        assert res.response.logid == mock_res.response.logid
        assert not res.data
        assert res.execute_id == mock_res.execute_id

    def test_sync_workflows_runs_stream(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        mock_logid = mock_create_workflows_runs_stream(respx_mock, read_file("testdata/workflow_run_stream_resp.txt"))
        stream = coze.workflows.runs.stream(workflow_id="id")
        assert stream.response.logid == mock_logid
        events = list(stream)
        assert events
        assert len(events) == 9

    def test_sync_workflows_runs_resume(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        mock_logid = mock_create_workflows_runs_resume(respx_mock, read_file("testdata/workflow_run_stream_resp.txt"))
        stream = coze.workflows.runs.resume(
            workflow_id="id",
            event_id="event_id",
            resume_data="resume_data",
            interrupt_type=123,
        )
        assert stream.response.logid == mock_logid
        events = list(stream)
        assert events
        assert len(events) == 9

    def test_sync_workflows_runs_invalid_stream_event(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        mock_logid = mock_create_workflows_runs_resume(
            respx_mock, read_file("testdata/workflow_run_invalid_stream_resp.txt")
        )
        stream = coze.workflows.runs.resume(
            workflow_id="id",
            event_id="event_id",
            resume_data="resume_data",
            interrupt_type=123,
        )
        assert stream.response.logid == mock_logid

        event = list(stream)[0]
        assert event.event == WorkflowEventType.UNKNOWN

    def test_sync_workflows_runs_run_histories_retrieve(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        workflow_id, execute_id, current_logid, execute_logid = mock_create_workflows_runs_run_histories_retrieve(
            respx_mock
        )

        res = coze.workflows.runs.run_histories.retrieve(workflow_id=workflow_id, execute_id=execute_id)
        assert res
        assert res.logid == execute_logid
        assert res.response.logid == current_logid

    def test_sync_workflows_runs_execute_nodes_retrieve(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        workflow_id = random_hex(10)
        execute_id = random_hex(10)
        node_execute_uuid = random_hex(10)
        logid = random_hex(10)
        node_output = "node_output"
        resp = WorkflowNodeExecuteHistory(is_finish=True, node_output=node_output)
        resp._raw_response = httpx.Response(
            200,
            json={"data": resp.model_dump()},
            headers={logid_key(): logid},
        )
        url = f"/v1/workflows/{workflow_id}/run_histories/{execute_id}/execute_nodes/{node_execute_uuid}"
        respx_mock.get(url).mock(resp._raw_response)

        res = coze.workflows.runs.run_histories.execute_nodes.retrieve(
            workflow_id=workflow_id, execute_id=execute_id, node_execute_uuid=node_execute_uuid
        )
        assert res.is_finish is True
        assert res.node_output == node_output
        assert res.response.logid == logid


@pytest.mark.respx(base_url="https://api.coze.com")
@pytest.mark.asyncio
class TestAsyncWorkflowsRuns:
    async def test_async_workflows_runs_create_no_async(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        mock_res = mock_create_workflows_runs(respx_mock, False)

        res = await coze.workflows.runs.create(workflow_id="id")
        assert res
        assert res.response.logid == mock_res.response.logid
        assert res.data == "data"

    async def test_async_workflows_runs_create_async(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        mock_res = mock_create_workflows_runs(respx_mock, True)

        res = await coze.workflows.runs.create(workflow_id="id", is_async=True)
        assert res
        assert res.response.logid == mock_res.response.logid
        assert not res.data
        assert res.execute_id == mock_res.execute_id

    async def test_async_workflows_runs_stream(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        mock_create_workflows_runs_stream(respx_mock, read_file("testdata/workflow_run_stream_resp.txt"))
        stream = coze.workflows.runs.stream(workflow_id="id")
        events = [event async for event in stream]
        assert events
        assert len(events) == 9

    async def test_async_workflows_runs_resume(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        mock_create_workflows_runs_resume(respx_mock, read_file("testdata/workflow_run_stream_resp.txt"))
        stream = coze.workflows.runs.resume(
            workflow_id="id",
            event_id="event_id",
            resume_data="resume_data",
            interrupt_type=123,
        )
        events = [event async for event in stream]
        assert events
        assert len(events) == 9

    async def test_async_workflows_runs_invalid_stream_event(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        mock_create_workflows_runs_resume(respx_mock, read_file("testdata/workflow_run_invalid_stream_resp.txt"))
        stream = coze.workflows.runs.resume(
            workflow_id="id",
            event_id="event_id",
            resume_data="resume_data",
            interrupt_type=123,
        )

        event = [event async for event in stream][0]
        assert event.event == WorkflowEventType.UNKNOWN

    async def test_async_workflows_runs_run_histories_retrieve(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        workflow_id, execute_id, current_logid, execute_logid = mock_create_workflows_runs_run_histories_retrieve(
            respx_mock
        )

        res = await coze.workflows.runs.run_histories.retrieve(workflow_id=workflow_id, execute_id=execute_id)
        assert res
        assert res.logid == execute_logid
        assert res.response.logid == current_logid

    async def test_async_workflows_runs_execute_nodes_retrieve(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        workflow_id = random_hex(10)
        execute_id = random_hex(10)
        node_execute_uuid = random_hex(10)
        logid = random_hex(10)
        node_output = "node_output"
        resp = WorkflowNodeExecuteHistory(is_finish=True, node_output=node_output)
        resp._raw_response = httpx.Response(
            200,
            json={"data": resp.model_dump()},
            headers={logid_key(): logid},
        )
        url = f"/v1/workflows/{workflow_id}/run_histories/{execute_id}/execute_nodes/{node_execute_uuid}"
        respx_mock.get(url).mock(resp._raw_response)

        res = await coze.workflows.runs.run_histories.execute_nodes.retrieve(
            workflow_id=workflow_id, execute_id=execute_id, node_execute_uuid=node_execute_uuid
        )
        assert res.is_finish is True
        assert res.node_output == node_output
        assert res.response.logid == logid
