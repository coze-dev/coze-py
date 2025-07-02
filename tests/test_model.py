from typing import Dict

import httpx
import pytest
from httpx import Response

from cozepy import AsyncStream, CozeInvalidEventError, ListResponse, Stream
from cozepy.model import DynamicStrEnum
from cozepy.util import anext

from .test_util import mock_response, to_async_iterator


def mock_sync_handler(d: Dict[str, str], response: Response):
    return d


class TestSyncStream:
    def test_sync_stream_invalid_event(self):
        items = ["event:x"]
        response = mock_response()
        s = Stream(response._raw_response, iter(items), ["field"], mock_sync_handler)
        with pytest.raises(CozeInvalidEventError, match="invalid event, data: event:x, logid: " + response.logid):
            next(s)

    def test_stream_invalid_field(self):
        items = ["event:x1", "event:x2"]
        response = mock_response()
        s = Stream(response._raw_response, iter(items), ["event", "second"], mock_sync_handler)

        with pytest.raises(
            CozeInvalidEventError, match="invalid event, field: event, data: event:x2, logid: " + response.logid
        ):
            next(s)


@pytest.mark.asyncio
class TestAsyncStream:
    async def test_asynv_stream_invalid_event(self):
        response = mock_response()
        items = ["event:x"]
        s = AsyncStream(to_async_iterator(items), ["field"], mock_sync_handler, response._raw_response)

        with pytest.raises(CozeInvalidEventError, match="invalid event, data: event:x, logid: " + response.logid):
            await anext(s)

    async def test_stream_invalid_field(self):
        response = mock_response()
        items = ["event:x1", "event:x2"]
        s = AsyncStream(to_async_iterator(items), ["event", "second"], mock_sync_handler, response._raw_response)

        with pytest.raises(
            CozeInvalidEventError, match="invalid event, field: event, data: event:x2, logid: " + response.logid
        ):
            await anext(s)


class TestListResponse:
    def test_slice(self):
        res = ListResponse(httpx.Response(200), [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        # len
        assert len(res) == 10
        # iter
        assert list(res) == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        # contains
        assert 1 in res
        assert 11 not in res
        # reversed
        assert list(reversed(res)) == [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
        # get item
        assert res[0] == 1
        # get item with slice
        assert res[1:3] == [2, 3]
        # get item with slice and step
        assert res[1:3:2] == [2]
        assert res[1:10:3] == [2, 5, 8]
        # set item
        assert list(res) == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        res[1:3] = [11, 12]
        assert list(res) == [1, 11, 12, 4, 5, 6, 7, 8, 9, 10]
        # set item with slice
        res[1:3] = [13, 14, 15]
        assert list(res) == [1, 13, 14, 15, 4, 5, 6, 7, 8, 9, 10]
        # set item with slice and step
        res[1:10:3] = [16, 17, 18]
        assert list(res) == [1, 16, 14, 15, 17, 5, 6, 18, 8, 9, 10]
        # del item
        del res[1]
        assert list(res) == [1, 14, 15, 17, 5, 6, 18, 8, 9, 10]
        # del item with slice
        del res[1:3]
        assert list(res) == [1, 17, 5, 6, 18, 8, 9, 10]
        # del item with slice and step
        del res[1:10:3]
        assert list(res) == [1, 5, 6, 8, 9]


class TestDynamicStrEnum:
    """测试动态字符串枚举基类"""

    def test_basic_enum_creation(self):
        """测试基本的枚举创建"""

        class TestEnum(DynamicStrEnum):
            VALUE1 = "value1"
            VALUE2 = "value2"

        # 测试预定义值
        assert TestEnum.VALUE1 == "value1"
        assert TestEnum.VALUE2 == "value2"
        assert TestEnum("value1") == "value1"
        assert TestEnum("value2") == "value2"

        # 测试 is_dynamic 属性
        assert not TestEnum.VALUE1.is_dynamic
        assert not TestEnum.VALUE2.is_dynamic

    def test_dynamic_enum_creation(self):
        """测试动态枚举创建"""

        class TestEnum(DynamicStrEnum):
            VALUE1 = "value1"

        # 测试未知值 - 应该发出警告并创建动态成员
        with pytest.warns(UserWarning, match="Unknown TestEnum value: unknown_value"):
            dynamic_value = TestEnum("unknown_value")

        assert dynamic_value == "unknown_value"
        assert dynamic_value.is_dynamic
        assert dynamic_value._name_ == "UNKNOWN_VALUE"
        assert dynamic_value._value_ == "unknown_value"

    def test_multiple_dynamic_values(self):
        """测试多个动态值"""

        class TestEnum(DynamicStrEnum):
            VALUE1 = "value1"

        # 创建多个动态值
        with pytest.warns(UserWarning):
            dynamic1 = TestEnum("dynamic1")
            dynamic2 = TestEnum("message.delta")

        assert dynamic1 == "dynamic1"
        assert dynamic2 == "message.delta"
        assert dynamic1.is_dynamic
        assert dynamic2.is_dynamic
        assert dynamic1._name_ == "DYNAMIC1"
        assert dynamic2._name_ == "MESSAGE_DELTA"

    def test_case_sensitivity(self):
        """测试大小写敏感性"""

        class TestEnum(DynamicStrEnum):
            VALUE1 = "value1"

        # 动态值应该保持原始大小写
        with pytest.warns(UserWarning):
            dynamic_value = TestEnum("MixedCase")

        assert dynamic_value == "MixedCase"
        assert dynamic_value._name_ == "MIXEDCASE"  # 名称转为大写
        assert dynamic_value._value_ == "MixedCase"  # 值保持原样

    def test_empty_string(self):
        """测试空字符串处理"""

        class TestEnum(DynamicStrEnum):
            EMPTY = ""

        # 预定义的空字符串
        assert TestEnum.EMPTY == ""
        assert not TestEnum.EMPTY.is_dynamic

        class TestEnum(DynamicStrEnum):
            NOT_EMPTY = "not_empty"

        # 动态创建的空字符串
        with pytest.warns(UserWarning):
            dynamic_empty = TestEnum("")

        assert dynamic_empty == ""
        assert dynamic_empty.is_dynamic

    def test_special_characters(self):
        """测试特殊字符处理"""

        class TestEnum(DynamicStrEnum):
            SPECIAL = "special"

        # 测试包含特殊字符的动态值
        with pytest.warns(UserWarning):
            dynamic_special = TestEnum("value-with-dashes")

        assert dynamic_special == "value-with-dashes"
        assert dynamic_special._name_ == "VALUE-WITH-DASHES"
        assert dynamic_special.is_dynamic

    def test_unicode_characters(self):
        """测试 Unicode 字符处理"""

        class TestEnum(DynamicStrEnum):
            UNICODE = "unicode"

        # 测试包含 Unicode 字符的动态值
        with pytest.warns(UserWarning):
            dynamic_unicode = TestEnum("测试值")

        assert dynamic_unicode == "测试值"
        assert dynamic_unicode._name_ == "测试值".upper()
        assert dynamic_unicode.is_dynamic

    def test_enum_comparison(self):
        """测试枚举比较"""

        class TestEnum(DynamicStrEnum):
            VALUE1 = "value1"

        # 预定义值比较
        assert TestEnum.VALUE1 == "value1"
        assert TestEnum("value1") == TestEnum.VALUE1

        # 动态值比较
        with pytest.warns(UserWarning):
            dynamic1 = TestEnum("dynamic1")
            dynamic2 = TestEnum("dynamic1")  # 相同的动态值

        assert dynamic1 == "dynamic1"
        assert dynamic1 == dynamic2  # 相同值的动态成员应该相等

    def test_enum_in_collections(self):
        """测试枚举在集合中的使用"""

        class TestEnum(DynamicStrEnum):
            VALUE1 = "value1"

        # 创建动态值
        with pytest.warns(UserWarning):
            dynamic1 = TestEnum("dynamic1")
            dynamic2 = TestEnum("dynamic2")

        # 测试在列表中的使用
        enum_list = [TestEnum.VALUE1, dynamic1, dynamic2]
        assert len(enum_list) == 3
        assert "value1" in enum_list
        assert "dynamic1" in enum_list
        assert "dynamic2" in enum_list

        # 测试在集合中的使用
        enum_set = {TestEnum.VALUE1, dynamic1, dynamic2}
        assert len(enum_set) == 3

    def test_warning_message_format(self):
        """测试警告消息格式"""

        class TestEnum(DynamicStrEnum):
            VALUE1 = "value1"

        # 检查警告消息格式
        with pytest.warns(UserWarning, match="Unknown TestEnum value: test_value") as warning_list:
            TestEnum("test_value")

        assert len(warning_list) == 1
        warning = warning_list[0]
        assert "Unknown TestEnum value: test_value" in str(warning.message)
