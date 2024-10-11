from cozepy import CozeAPIError, CozeInvalidEventError, CozePKCEAuthError, CozePKCEAuthErrorType


def test_coze_error():
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

    err = CozePKCEAuthError(CozePKCEAuthErrorType.AUTHORIZATION_PENDING)
    assert err.error == "authorization_pending"

    err = CozeInvalidEventError("event", "xxx", "logid")
    assert str(err) == "invalid event, field: event, data: xxx, logid: logid"

    err = CozeInvalidEventError("", "xxx", "logid")
    assert str(err) == "invalid event, data: xxx, logid: logid"
