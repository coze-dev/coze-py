import unittest

from cozepy import COZE_CN_BASE_URL, Coze
from tests.config import fixed_token_auth


@unittest.skip("not available in not cn")
def test_knowledge_documents_list():
    cli = Coze(auth=fixed_token_auth, base_url=COZE_CN_BASE_URL)
    print(cli.knowledge.documents.list(dataset_id=""))
