import httpx
import pytest

from cozepy import (
    AsyncCoze,
    AsyncTokenAuth,
    BenefitBasicInfo,
    BenefitInfo,
    BenefitItemInfo,
    BenefitOverview,
    BenefitStatusInfo,
    Coze,
    TokenAuth,
)
from cozepy.util import random_hex
from tests.test_util import logid_key


def mock_get_benefits(respx_mock) -> BenefitOverview:
    benefit_item_info = BenefitItemInfo(
        used=100,
        total=1000,
        start_at=1735689600,
        end_at=1735689600,
        strategy="by_quota",
    )
    benefit_status_info = BenefitStatusInfo(
        status="valid",
        item_info=benefit_item_info,
    )
    benefits = BenefitOverview(
        basic_info=BenefitBasicInfo(user_level="enterprise"),
        benefit_info=[
            BenefitInfo(
                basic=benefit_status_info,
                extra=[benefit_status_info],
                effective=benefit_status_info,
                resource_id="chat",
                benefit_type="api_run_qps",
            )
        ],
    )
    benefits._raw_response = httpx.Response(
        200,
        json={"data": benefits.model_dump()},
        headers={logid_key(): random_hex(10)},
    )
    respx_mock.get(
        "/v1/commerce/benefit/benefits/get",
        params={
            "benefit_type_list": "api_run_qps,call_tool_limit",
            "resource_id": "chat",
        },
    ).mock(benefits._raw_response)
    return benefits


@pytest.mark.respx(base_url="https://api.coze.com")
class TestSyncBenefits:
    def test_sync_benefits_retrieve(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        mock_benefits = mock_get_benefits(respx_mock)

        benefits = coze.benefits.retrieve(benefit_type_list=["api_run_qps", "call_tool_limit"], resource_id="chat")
        assert benefits
        assert benefits.response.logid == mock_benefits.response.logid
        assert benefits.basic_info and benefits.basic_info.user_level == "enterprise"
        assert benefits.benefit_info and benefits.benefit_info[0].resource_id == "chat"


@pytest.mark.respx(base_url="https://api.coze.com")
@pytest.mark.asyncio
class TestAsyncBenefits:
    async def test_async_benefits_retrieve(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))

        mock_benefits = mock_get_benefits(respx_mock)

        benefits = await coze.benefits.retrieve(
            benefit_type_list=["api_run_qps", "call_tool_limit"], resource_id="chat"
        )
        assert benefits
        assert benefits.response.logid == mock_benefits.response.logid
        assert benefits.basic_info and benefits.basic_info.user_level == "enterprise"
        assert benefits.benefit_info and benefits.benefit_info[0].resource_id == "chat"
