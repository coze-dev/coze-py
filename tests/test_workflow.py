import httpx
import pytest

from cozepy import AsyncCoze, Coze, TokenAuth, WorkflowRunResult

stream_testdata = """
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

"""


@pytest.mark.respx(base_url="https://api.coze.com")
class TestWorkflowsRuns:
    def test_sync_workflows_runs_create(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        respx_mock.post("/v1/workflow/run").mock(
            httpx.Response(200, json={"data": WorkflowRunResult(debug_url="debug_url", data="data").model_dump()})
        )

        res = coze.workflows.runs.create(workflow_id="id")
        assert res
        assert res.data == "data"

    def test_sync_workflows_runs_stream(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        respx_mock.post("/v1/workflow/stream_run").mock(httpx.Response(200, content=stream_testdata))

        events = list(coze.workflows.runs.stream(workflow_id="id"))

        assert events
        assert len(events) == 9

    def test_sync_workflows_runs_resume(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        respx_mock.post("/v1/workflow/stream_resume").mock(httpx.Response(200, content=stream_testdata))

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
            httpx.Response(
                200,
                content="""
id:0
event:invalid
data:{}""",
            )
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


@pytest.mark.respx(base_url="https://api.coze.com")
@pytest.mark.asyncio
class TestAsyncWorkflowsRuns:
    async def test_async_workflows_runs_create(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        respx_mock.post("/v1/workflow/run").mock(
            httpx.Response(200, json={"data": WorkflowRunResult(debug_url="debug_url", data="data").model_dump()})
        )

        res = await coze.workflows.runs.create(workflow_id="id")
        assert res
        assert res.data == "data"

    async def test_async_workflows_runs_stream(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        respx_mock.post("/v1/workflow/stream_run").mock(httpx.Response(200, content=stream_testdata))

        events = [event async for event in coze.workflows.runs.stream(workflow_id="id")]

        assert events
        assert len(events) == 9

    async def test_async_workflows_runs_resume(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        respx_mock.post("/v1/workflow/stream_resume").mock(httpx.Response(200, content=stream_testdata))

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
            httpx.Response(
                200,
                content="""
id:0
event:invalid
data:{}""",
            )
        )

        with pytest.raises(Exception, match="invalid workflows.event: invalid"):
            async for event in coze.workflows.runs.resume(
                workflow_id="id",
                event_id="event_id",
                resume_data="resume_data",
                interrupt_type=123,
            ):
                assert event
