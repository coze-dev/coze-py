import os
from unittest import TestCase

from cozepy import Coze, COZE_CN_BASE_URL
from tests.config import fixed_token_auth, jwt_auth


class TestBotsClient(TestCase):
    def test_bots_list(self):
        space_id = os.getenv("SPACE_ID_1").strip()

        cli_list = [
            # fixed token
            Coze(auth=fixed_token_auth, base_url=COZE_CN_BASE_URL),
            # jwt auth
            Coze(auth=jwt_auth, base_url=COZE_CN_BASE_URL),
        ]
        for cli in cli_list:
            res = cli.bots.list(space_id=space_id, page_size=2)
            assert res.total > 1
            assert res.has_more
            assert len(res.items) > 1

    def test_bots_retrieve(self):
        bot_id = self.bot_id

        cli_list = [
            # fixed token
            Coze(auth=fixed_token_auth, base_url=COZE_CN_BASE_URL),
            # jwt auth
            Coze(auth=jwt_auth, base_url=COZE_CN_BASE_URL),
        ]
        for cli in cli_list:
            bot = cli.bots.retrieve(bot_id=bot_id)
            assert bot is not None
            assert bot.bot_id == bot_id

    @property
    def bot_id(self) -> str:
        space_id = os.getenv("SPACE_ID_1").strip()

        # fixed token
        cli = Coze(auth=fixed_token_auth, base_url=COZE_CN_BASE_URL)
        res = cli.bots.list(space_id=space_id, page_size=2)
        return res.items[0].bot_id
