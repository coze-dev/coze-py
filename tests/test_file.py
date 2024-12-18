from pathlib import Path
from unittest.mock import mock_open, patch

import httpx
import pytest

from cozepy import AsyncCoze, Coze, File, TokenAuth
from cozepy.util import random_hex
from tests.test_util import logid_key


def mock_upload_files(respx_mock):
    file = File(id="1", bytes=2, created_at=3, file_name="name")
    file._raw_response = httpx.Response(200, json={"data": file.model_dump()}, headers={logid_key(): random_hex(10)})
    respx_mock.post("/v1/files/upload").mock(file._raw_response)
    return file


def mock_retrieve_files(respx_mock):
    file = File(id="1", bytes=2, created_at=3, file_name="name")
    file._raw_response = httpx.Response(200, json={"data": file.model_dump()}, headers={logid_key(): random_hex(10)})
    respx_mock.get("/v1/files/retrieve").mock(file._raw_response)
    return file


@pytest.mark.respx(base_url="https://api.coze.com")
class TestSyncFiles:
    def test_sync_files_upload(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        mock_file = mock_upload_files(respx_mock)

        with patch("builtins.open", mock_open(read_data="data")):
            file = coze.files.upload(file=Path("/path"))
            assert file
            assert file.logid == mock_file.logid
            assert file.file_name == "name"

    def test_sync_files_retrieve(self, respx_mock):
        coze = Coze(auth=TokenAuth(token="token"))

        mock_file = mock_retrieve_files(respx_mock)

        file = coze.files.retrieve(file_id="id")
        assert file
        assert file.logid == mock_file.logid
        assert file.file_name == "name"


@pytest.mark.respx(base_url="https://api.coze.com")
@pytest.mark.asyncio
class TestAsyncFiles:
    async def test_async_files_upload(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        mock_file = mock_upload_files(respx_mock)

        with patch("builtins.open", mock_open(read_data="data")):
            file = await coze.files.upload(file=Path("/path"))
            assert file
            assert file.logid == mock_file.logid
            assert file.file_name == "name"

    async def test_async_files_retrieve(self, respx_mock):
        coze = AsyncCoze(auth=TokenAuth(token="token"))

        mock_file = mock_retrieve_files(respx_mock)

        file = await coze.files.retrieve(file_id="id")
        assert file
        assert file.logid == mock_file.logid
        assert file.file_name == "name"
