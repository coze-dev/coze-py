import os
from pathlib import Path
from typing import IO, Optional, Tuple, Union

from cozepy.model import CozeModel
from cozepy.request import Requester
from cozepy.util import remove_url_trailing_slash

FileContent = Union[IO[bytes], bytes, str, Path]
FileTypes = Union[
    # file (or bytes)
    FileContent,
    # (filename, file (or bytes))
    Tuple[Optional[str], FileContent],
]


class File(CozeModel):
    # 文件ID
    id: str
    # 文件字节数
    bytes: Optional[int] = None
    # 上传时间戳，单位s
    created_at: Optional[int] = None
    # 文件名
    file_name: Optional[str] = None


def _try_fix_file(file: FileTypes) -> FileTypes:
    if isinstance(file, Path):
        if not file.exists():
            raise ValueError(f"File not found: {file}")
        return open(file, "rb")

    if isinstance(file, str):
        if not os.path.isfile(file):
            raise ValueError(f"File not found: {file}")
        return open(file, "rb")

    return file


class FilesClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    def retrieve(self, *, file_id: str):
        """
        Get the information of the specific file uploaded to Coze platform.

        查看已上传的文件详情。

        docs en: https://www.coze.com/docs/developer_guides/retrieve_files
        docs cn: https://www.coze.cn/docs/developer_guides/retrieve_files

        :param file_id: file id
        :return: file info
        """
        url = f"{self._base_url}/v1/files/retrieve"
        params = {"file_id": file_id}
        return self._requester.request("get", url, False, File, params=params)

    def upload(self, *, file: FileTypes) -> File:
        """
        Upload files to Coze platform.

        Local files cannot be used directly in messages. Before creating messages or conversations,
        you need to call this interface to upload local files to the platform first.
        After uploading the file, you can use it directly in multimodal content in messages
        by specifying the file_id.

        调用接口上传文件到扣子。

        docs en: https://www.coze.com/docs/developer_guides/upload_files
        docs zh: https://www.coze.cn/docs/developer_guides/upload_files

        :param file: local file path
        :return: file info
        """
        url = f"{self._base_url}/v1/files/upload"
        files = {"file": _try_fix_file(file)}
        return self._requester.request("post", url, False, File, files=files)


class AsyncFilesClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    async def retrieve(self, *, file_id: str):
        """
        Get the information of the specific file uploaded to Coze platform.

        查看已上传的文件详情。

        docs en: https://www.coze.com/docs/developer_guides/retrieve_files
        docs cn: https://www.coze.cn/docs/developer_guides/retrieve_files

        :param file_id: file id
        :return: file info
        """
        url = f"{self._base_url}/v1/files/retrieve"
        params = {"file_id": file_id}
        return await self._requester.arequest("get", url, False, File, params=params)

    async def upload(self, *, file: FileTypes) -> File:
        """
        Upload files to Coze platform.

        Local files cannot be used directly in messages. Before creating messages or conversations,
        you need to call this interface to upload local files to the platform first.
        After uploading the file, you can use it directly in multimodal content in messages
        by specifying the file_id.

        调用接口上传文件到扣子。

        docs en: https://www.coze.com/docs/developer_guides/upload_files
        docs zh: https://www.coze.cn/docs/developer_guides/upload_files

        :param file: local file path
        :return: file info
        """
        url = f"{self._base_url}/v1/files/upload"
        files = {"file": _try_fix_file(file)}
        return await self._requester.arequest("post", url, False, File, files=files)
