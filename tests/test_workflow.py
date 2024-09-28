import unittest

from cozepy import COZE_CN_BASE_URL, Coze, Stream, WorkflowEvent, WorkflowEventType
from tests.config import fixed_token_auth


@unittest.skip("not available in not cn")
def test_workflows():
    cli = Coze(auth=fixed_token_auth, base_url=COZE_CN_BASE_URL)

    # not stream
    res = cli.workflows.runs.create(
        workflow_id="xxxx",
        parameters={
            "biz_param_str": "biz_param_str",
            "biz_param_int": 300,
            "biz_param_bool": "True",
        },
    )
    print(res.data)
    print(res.debug_url)

    # stream
    iter = cli.workflows.runs.stream(
        workflow_id="xxxx",
        parameters={
            "biz_param_str": "biz_param_str",
            "biz_param_int": 300,
            "biz_param_bool": "True",
        },
    )

    def handle_iter(iter: Stream[WorkflowEvent]):
        for item in iter:
            if item.event == WorkflowEventType.MESSAGE:
                print("msg", item.message)
            elif item.event == WorkflowEventType.ERROR:
                print("error", item.error)
            elif item.event == WorkflowEventType.INTERRUPT:
                print("interrupt", item.interrupt)
                handle_iter(
                    cli.workflows.runs.resume(
                        workflow_id="xxxx",
                        event_id=item.interrupt.interrupt_data.event_id,
                        resume_data="yyyy",
                        interrupt_type=item.interrupt.interrupt_data.type,
                    )
                )

    handle_iter(iter)
