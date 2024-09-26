from cozepy import Coze, COZE_CN_BASE_URL
from tests.config import fixed_token_auth
import unittest


@unittest.skip("not available in not cn")
def test_file_v1():
    cli = Coze(auth=fixed_token_auth, base_url=COZE_CN_BASE_URL)

    file = cli.file.v1.upload("./tests/test_file.py")
    assert file is not None
    assert file.id != ""

    file_retrieve = cli.file.v1.retrieve(file_id=file.id)
    assert file_retrieve is not None
    assert file_retrieve.id == file.id
