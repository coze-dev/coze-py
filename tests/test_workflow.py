import httpx
import pytest

from cozepy import (
    AsyncCoze,
    Coze,
    TokenAuth,
    WorkflowExecuteStatus,
    WorkflowRunHistory,
    WorkflowRunMode,
    WorkflowRunResult,
)
from cozepy.util import random_hex
from tests.config import make_stream_response

stream_testdata = make_stream_response("""
id: 0
event: Message
data: {"content":"msg","node_is_finish":false,"node_seq_id":"0","node_title":"Message"}

id: 1
event: Message
data: {"content":"为","node_is_finish":false,"node_seq_id":"1","node_title":"Message"}

id: 2
event: Message
data: {"content":"什么小明要带一把尺子去看电影因","node_is_finish":false,"node_seq_id":"2","node_title":"Message"}

id: 3
event: Message
data: {"content":"为他听说电影很长，怕","node_is_finish":false,"node_seq_id":"3","node_title":"Message"}

id: 4
event: Message
data: {"content":"坐不下！","node_is_finish":true,"node_seq_id":"4","node_title":"Message"}

id: 5
event: Message
data: {"content":"{\\"output\\":\\"为什么小明要带一把尺子去看电影？因为他听说电影很长，怕坐不下！\\"}","cost":"0.00","node_is_finish":true,"node_seq_id":"0","node_title":"","token":0}

id: 0
event: Error
data: {"error_code":4000,"error_message":"Request parameter error"}

id: 0
event: Message
data: {"content":"请问你想查看哪个城市、哪一天的天气呢","content_type":"text","node_is_finish":true,"node_seq_id":"0","node_title":"问答"}

id: 1
event: Interrupt
data: {"interrupt_data":{"data":"","event_id":"7404830425073352713/2769808280134765896","type":2},"node_title":"问答"}

id: 6
event: Done
data: {}

""")


def mock_create_workflow_run(respx_mock, is_async: bool):
    respx_mock.post(
        "/v1/workflow/run",
        json={
            "workflow_id": "id",
            "parameters": None,
            "bot_id": None,
            "is_async": is_async,
            "ext": None,
        },
    ).mock(
        httpx.Response(
            200,
            json={
                "data": WorkflowRunResult(
                    debug_url="debug_url",
                    data="data" if not is_async else None,
                    execute_id="execute_id" if is_async else None,
                ).model_dump()
            },
        )
    )


def mock_create_workflow_stream(respx_mock, data):
    respx_mock.post("/v1/workflow/stream_run").mock(data)


@pytest.mark.respx(base_url="https://api.coze.com")
class TestWorkflowsRuns:
    def test_sync_workflows_runs_create_no_async(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        mock_create_workflow_run(respx_mock, False)

        res = coze.workflows.runs.create(workflow_id="id")
        assert res
        assert res.data == "data"

    def test_sync_workflows_runs_create_async(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        mock_create_workflow_run(respx_mock, True)

        res = coze.workflows.runs.create(workflow_id="id", is_async=True)
        assert res
        assert not res.data
        assert res.execute_id

    def test_sync_workflows_runs_stream(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        respx_mock.post("/v1/workflow/stream_run").mock(stream_testdata)

        events = list(coze.workflows.runs.stream(workflow_id="id"))

        assert events
        assert len(events) == 9

    def test_sync_workflows_runs_resume(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        respx_mock.post("/v1/workflow/stream_resume").mock(stream_testdata)

        events = list(
            coze.workflows.runs.resume(
                workflow_id="id",
                event_id="event_id",
                resume_data="resume_data",
                interrupt_type=123,
            )
        )

        assert events
        assert len(events) == 9

    def test_sync_workflows_runs_invalid_stream_event(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        respx_mock.post("/v1/workflow/stream_resume").mock(
            make_stream_response("""
id:0
event:invalid
data:{}""")
        )

        with pytest.raises(Exception, match="invalid workflows.event: invalid"):
            list(
                coze.workflows.runs.resume(
                    workflow_id="id",
                    event_id="event_id",
                    resume_data="resume_data",
                    interrupt_type=123,
                )
            )

    def test_sync_workflows_runs_run_histories_retrieve(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        workflow_id = random_hex(10)
        execute_id = random_hex(10)
        url = f"/v1/workflows/{workflow_id}/run_histories/{execute_id}"
        respx_mock.get(url).mock(
            httpx.Response(
                200,
                json={
                    "data": [
                        WorkflowRunHistory(
                            execute_id="execute_id",
                            execute_status=WorkflowExecuteStatus.RUNNING,
                            bot_id="bot_id",
                            connector_id="connector_id",
                            connector_uid="connector_uid",
                            run_mode=WorkflowRunMode.SYNCHRONOUS,
                            logid="logid",
                            create_time=0,
                            update_time=0,
                            output="output",
                            error_code=0,
                            error_message="error_message",
                            debug_url="debug_url",
                        ).model_dump()
                    ]
                },
            )
        )

        res = coze.workflows.runs.run_histories.retrieve(workflow_id=workflow_id, execute_id=execute_id)
        assert res


@pytest.mark.respx(base_url="https://api.coze.com")
@pytest.mark.asyncio
class TestAsyncWorkflowsRuns:
    async def test_async_workflows_runs_create_no_async(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        mock_create_workflow_run(respx_mock, False)

        res = await coze.workflows.runs.create(workflow_id="id")
        assert res
        assert res.data == "data"
        assert not res.execute_id

    async def test_async_workflows_runs_create_async(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        mock_create_workflow_run(respx_mock, True)

        res = await coze.workflows.runs.create(workflow_id="id", is_async=True)
        assert res
        assert not res.data
        assert res.execute_id == "execute_id"

    async def test_async_workflows_runs_stream(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        respx_mock.post("/v1/workflow/stream_run").mock(stream_testdata)

        events = [event async for event in coze.workflows.runs.stream(workflow_id="id")]

        assert events
        assert len(events) == 9

    async def test_async_workflows_runs_resume(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        respx_mock.post("/v1/workflow/stream_resume").mock(stream_testdata)

        events = [
            event
            async for event in coze.workflows.runs.resume(
                workflow_id="id",
                event_id="event_id",
                resume_data="resume_data",
                interrupt_type=123,
            )
        ]

        assert events
        assert len(events) == 9

    async def test_async_workflows_runs_invalid_stream_event(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        respx_mock.post("/v1/workflow/stream_resume").mock(
            make_stream_response("""
id:0
event:invalid
data:{}""")
        )

        with pytest.raises(Exception, match="invalid workflows.event: invalid"):
            async for event in coze.workflows.runs.resume(
                workflow_id="id",
                event_id="event_id",
                resume_data="resume_data",
                interrupt_type=123,
            ):
                assert event

    async def test_async_workflows_runs_run_histories_retrieve(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        workflow_id = random_hex(10)
        execute_id = random_hex(10)
        url = f"/v1/workflows/{workflow_id}/run_histories/{execute_id}"
        respx_mock.get(url).mock(
            httpx.Response(
                200,
                json={
                    "data": [
                        WorkflowRunHistory(
                            execute_id="execute_id",
                            execute_status=WorkflowExecuteStatus.RUNNING,
                            bot_id="bot_id",
                            connector_id="connector_id",
                            connector_uid="connector_uid",
                            run_mode=WorkflowRunMode.SYNCHRONOUS,
                            logid="logid",
                            create_time=0,
                            update_time=0,
                            output="output",
                            error_code=0,
                            error_message="error_message",
                            debug_url="debug_url",
                        ).model_dump()
                    ]
                },
            )
        )

        res = await coze.workflows.runs.run_histories.retrieve(workflow_id=workflow_id, execute_id=execute_id)
        assert res
