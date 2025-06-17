import httpx
import pytest

from cozepy import AsyncCoze, AsyncTokenAuth, Coze, TokenAuth, WorkspaceMember, WorkspaceRoleType
from cozepy.model import HTTPResponse, NumberPagedResponse
from cozepy.util import random_hex
from tests.test_util import logid_key


class MockWorkspacesMembersPagedResponse(NumberPagedResponse[WorkspaceMember]):
    def __init__(self, user_id, total_count, raw_response):
        self._user_id = user_id
        self._total_count = total_count
        self._raw_response = raw_response

    def get_total(self):
        return self._total_count

    def get_has_more(self):
        return None

    def get_items(self):
        return [WorkspaceMember(user_id=self._user_id, role_type=WorkspaceRoleType.MEMBER)]

    @property
    def response(self):
        return HTTPResponse(self._raw_response)


def mock_create_workspaces_members(respx_mock, workspace_id, user_ids):
    respx_mock.post(f"/v1/workspaces/{workspace_id}/members").mock(
        httpx.Response(
            200,
            json={
                "data": {
                    "added_success_user_ids": user_ids,
                    "invited_success_user_ids": [],
                    "not_exist_user_ids": [],
                    "already_joined_user_ids": [],
                    "already_invited_user_ids": [],
                }
            },
            headers={logid_key(): "logid"},
        )
    )


def mock_delete_workspaces_members(respx_mock, workspace_id, user_ids):
    respx_mock.delete(f"/v1/workspaces/{workspace_id}/members").mock(
        httpx.Response(
            200,
            json={
                "data": {
                    "removed_success_user_ids": user_ids,
                    "not_in_workspace_user_ids": [],
                    "owner_not_support_remove_user_ids": [],
                }
            },
            headers={logid_key(): "logid"},
        )
    )


def mock_list_workspaces_members(respx_mock, workspace_id, total_count, page, user_id, is_async=False):
    from cozepy.request import Requester

    orig_send = getattr(Requester, "send", None)
    orig_asend = getattr(Requester, "asend", None)

    def _mock_send(self, request):
        response = httpx.Response(200, headers={logid_key(): "logid"})
        return MockWorkspacesMembersPagedResponse(user_id, total_count, response)

    async def _mock_asend(self, request):
        response = httpx.Response(200, headers={logid_key(): "logid"})
        return MockWorkspacesMembersPagedResponse(user_id, total_count, response)

    if is_async:
        Requester.asend = _mock_asend
        respx_mock._restore_asend = lambda: setattr(Requester, "asend", orig_asend)
    else:
        Requester.send = _mock_send
        respx_mock._restore_send = lambda: setattr(Requester, "send", orig_send)


@pytest.fixture(autouse=True)
def restore_send(request):
    yield
    if hasattr(request.node, "parent") and hasattr(request.node.parent, "_restore_send"):
        request.node.parent._restore_send()
    elif hasattr(request.node, "_restore_send"):
        request.node._restore_send()
    if hasattr(request.node, "parent") and hasattr(request.node.parent, "_restore_asend"):
        request.node.parent._restore_asend()
    elif hasattr(request.node, "_restore_asend"):
        request.node._restore_asend()


@pytest.mark.respx(base_url="https://api.coze.com")
class TestSyncWorkspacesMembers:
    def test_sync_members_create(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))
        workspace_id = random_hex(10)
        user_ids = [random_hex(10), random_hex(10)]
        mock_create_workspaces_members(respx_mock, workspace_id, user_ids)
        resp = coze.workspaces.members.create(
            workspace_id=workspace_id,
            users=[WorkspaceMember(user_id=user_id, role_type=WorkspaceRoleType.MEMBER) for user_id in user_ids],
        )
        assert resp.added_success_user_ids == user_ids
        assert resp.response.logid == "logid"

    def test_sync_members_delete(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))
        workspace_id = random_hex(10)
        user_ids = [random_hex(10), random_hex(10)]
        mock_delete_workspaces_members(respx_mock, workspace_id, user_ids)
        resp = coze.workspaces.members.delete(workspace_id=workspace_id, user_ids=user_ids)
        assert resp.removed_success_user_ids == user_ids
        assert resp.response.logid == "logid"

    def test_sync_members_list(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))
        workspace_id = random_hex(10)
        user_id = random_hex(10)
        total = 2
        for idx in range(total):
            mock_list_workspaces_members(respx_mock, workspace_id, total, idx + 1, user_id)
        resp = coze.workspaces.members.list(workspace_id=workspace_id, page_num=1, page_size=1)
        assert resp
        total_result = 0
        for member in resp:
            total_result += 1
            assert member.user_id == user_id
        assert total_result == total


@pytest.mark.respx(base_url="https://api.coze.com")
@pytest.mark.asyncio
class TestAsyncWorkspacesMembers:
    async def test_async_members_create(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))
        workspace_id = random_hex(10)
        user_ids = [random_hex(10), random_hex(10)]
        mock_create_workspaces_members(respx_mock, workspace_id, user_ids)
        resp = await coze.workspaces.members.create(
            workspace_id=workspace_id,
            users=[WorkspaceMember(user_id=user_id, role_type=WorkspaceRoleType.MEMBER) for user_id in user_ids],
        )
        assert resp.added_success_user_ids == user_ids
        assert resp.response.logid == "logid"

    async def test_async_members_delete(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))
        workspace_id = random_hex(10)
        user_ids = [random_hex(10), random_hex(10)]
        mock_delete_workspaces_members(respx_mock, workspace_id, user_ids)
        resp = await coze.workspaces.members.delete(workspace_id=workspace_id, user_ids=user_ids)
        assert resp.removed_success_user_ids == user_ids
        assert resp.response.logid == "logid"

    async def test_async_members_list(self, respx_mock):
        coze = AsyncCoze(auth=AsyncTokenAuth(token="token"))
        workspace_id = random_hex(10)
        user_id = random_hex(10)
        total = 2
        for idx in range(total):
            mock_list_workspaces_members(respx_mock, workspace_id, total, idx + 1, user_id, is_async=True)
        resp = await coze.workspaces.members.list(workspace_id=workspace_id, page_num=1, page_size=1)
        assert resp
        total_result = 0
        async for member in resp:
            total_result += 1
            assert member.user_id == user_id
        assert total_result == total
