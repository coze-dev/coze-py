from pycoze.auth import Auth
from pycoze.model import CozeModel
from pycoze.request import Requester


class BotPromptInfo(CozeModel):
    prompt: str


class BotModelInfo(CozeModel):
    model_id: str
    model_name: str


class Bot(CozeModel):
    bot_id: str  # Bot 的唯一标识
    name: str  # Bot 的名称
    description: str  # Bot 的描述信息
    icon_url: str  # Bot 的图标
    create_time: int  # 创建时间，格式为 10 位的 Unixtime 时间戳，单位为秒（s）
    update_time: int  # Bot 的更新时间
    version: str  # Bot 最新版本的版本号
    prompt_info: BotPromptInfo
    model_info: BotModelInfo


class BotClient(object):
    """
    Bot class.
    """

    def __init__(self, base_url: str, auth: Auth, requester: Requester):
        self._base_url = base_url
        self._auth = auth
        self._requester = requester

    def get_online_info_v1(self, *, bot_id: str):
        """
        :calls: `GET /v1/bot/get_online_info`
        :param bot_id:
        :return:
        """
        url = f'{self._base_url}/v1/bot/get_online_info'
        params = {
            'bot_id': bot_id
        }

        return self._requester.request('get', url, Bot, params=params)
