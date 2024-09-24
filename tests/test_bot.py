import os
from unittest import TestCase

from cozepy import TokenAuth, Coze, COZE_CN_BASE_URL


class TestBotClient(TestCase):
    def test_list_published_bots_v1(self):
        space_id = os.getenv("SPACE_ID_1").strip()
        token = os.getenv("COZE_TOKEN").strip()
        for i in token:
            print("token", i)
        auth = TokenAuth(token)
        cli = Coze(auth=auth, base_url=COZE_CN_BASE_URL)

        res = cli.bot.list_published_bots_v1(space_id=space_id, page_size=2)
        assert res.total > 1
        assert res.has_more
        assert len(res.items) > 1
