from cozepy.auth import Auth
from cozepy.model import CozeModel
from cozepy.request import Requester


class File(CozeModel):
    # The ID of the uploaded file.
    # 已上传的文件 ID。
    id: str

    # 文件的总字节数。
    # The total byte size of the file.
    bytes: int

    # 文件的上传时间，格式为 10 位的 Unixtime 时间戳，单位为秒（s）。
    # The upload time of the file, in the format of a 10-digit Unix timestamp in seconds (s).
    created_at: int

    # 文件名称。
    # The name of the file.
    file_name: str


class FileClient(object):
    def __init__(self, base_url: str, auth: Auth, requester: Requester):
        self._base_url = base_url
        self._auth = auth
        self._requester = requester
        self._v1 = None

    def upload(self, file: str) -> File:
        """
        Upload files to Coze platform.

        Local files cannot be used directly in messages. Before creating messages or conversations,
        you need to call this interface to upload local files to the platform first.
        After uploading the file, you can use it directly in multimodal content in messages
        by specifying the file_id.

        调用接口上传文件到扣子。

        docs en: https://www.coze.com/docs/developer_guides/upload_files
        docs zh: https://www.coze.cn/docs/developer_guides/upload_files

        Args:
            file: local file path

        Returns:
            File: file info
        """
        url = f"{self._base_url}/v1/files/upload"
        files = {"file": open(file, "rb")}
        return self._requester.request("get", url, File, files=files)

    def retrieve(self, file_id: str):
        """
        Get the information of the specific file uploaded to Coze platform.

        查看已上传的文件详情。

        docs en: https://www.coze.com/docs/developer_guides/retrieve_files
        docs cn: https://www.coze.cn/docs/developer_guides/retrieve_files

        Args:
            file_id: file id of file

        Returns:
            File: file info
        """
        url = f"{self._base_url}/v1/files/retrieve"
        params = {"file_id": file_id}
        return self._requester.request("get", url, File, params=params)
