from cozepy import WorkflowRunHistory


def test_empty_str_to_zero():
    data = {
        "logid": "logid",
        "debug_url": "https://www.coze.cn/work_flow",
        "execute_id": "123",
        "bot_id": "0",
        "update_time": 1744960910,
        "token": "0",
        "execute_status": "Running",
        "connector_uid": "123",
        "connector_id": "1024",
        "create_time": 1744960910,
        "run_mode": 2,
        "output": '{"Output":"null"}',
        "cost": "0.00000",
        "error_code": "",
        "is_output_trimmed": False,
    }
    history = WorkflowRunHistory(**data)
    assert history.error_code == 0
