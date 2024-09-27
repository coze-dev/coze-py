from cozepy import CozeAPIError


def test_coze_api_error():
    err = CozeAPIError(1, "msg", "logid")
    assert err.code == 1
    assert err.msg == "msg"
    assert err.logid == "logid"
    assert str(err) == "code: 1, msg: msg, logid: logid"

    err = CozeAPIError(None, "msg", "logid")
    assert err.code is None
    assert err.msg == "msg"
    assert err.logid == "logid"
    assert str(err) == "msg: msg, logid: logid"
