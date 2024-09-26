import unittest

from cozepy import Coze, COZE_CN_BASE_URL
from tests.config import fixed_token_auth


@unittest.skip("not available in not cn")
def test_files():
    cli = Coze(auth=fixed_token_auth, base_url=COZE_CN_BASE_URL)

    file = cli.files.upload(file="./tests/test_file.py")
    assert file is not None
    assert file.id != ""

    file_retrieve = cli.files.retrieve(file_id=file.id)
    assert file_retrieve is not None
    assert file_retrieve.id == file.id
