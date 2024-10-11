from pathlib import Path
from unittest.mock import mock_open, patch

import httpx
import pytest

from cozepy import AsyncCoze, Coze, File, TokenAuth


@pytest.mark.respx(base_url="https://api.coze.com")
class TestFile:
    def test_sync_file_upload(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        respx_mock.post("/v1/files/upload").mock(
            httpx.Response(200, json={"data": File(id="1", bytes=2, created_at=3, file_name="name").model_dump()})
        )

        with patch("builtins.open", mock_open(read_data="data")):
            file = coze.files.upload(file=Path("/path"))
            assert file
            assert "name" == file.file_name

    def test_file_retrieve(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        respx_mock.get("/v1/files/retrieve").mock(
            httpx.Response(200, json={"data": File(id="1", bytes=2, created_at=3, file_name="name").model_dump()})
        )

        file = coze.files.retrieve(file_id="id")
        assert file
        assert "name" == file.file_name


@pytest.mark.respx(base_url="https://api.coze.com")
@pytest.mark.asyncio
class TestAsyncFile:
    async def test_async_file_upload(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        with patch("builtins.open", mock_open(read_data="data")):
            respx_mock.post("/v1/files/upload").mock(
                httpx.Response(200, json={"data": File(id="1", bytes=2, created_at=3, file_name="name").model_dump()})
            )

            file = await coze.files.upload(file=Path("/path"))
            assert file
            assert "name" == file.file_name

    async def test_async_file_retrieve(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        respx_mock.get("/v1/files/retrieve").mock(
            httpx.Response(200, json={"data": File(id="1", bytes=2, created_at=3, file_name="name").model_dump()})
        )

        file = await coze.files.retrieve(file_id="id")
        assert file
        assert "name" == file.file_name
