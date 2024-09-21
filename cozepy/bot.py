from enum import IntEnum
from typing import List

from cozepy.auth import Auth
from cozepy.model import CozeModel, NumberPaged
from cozepy.request import Requester


class BotPromptInfo(CozeModel):
    # Configured prompt of the bot.
    prompt: str


class BotOnboardingInfo(CozeModel):
    # Configured prologue of the bot.
    prologue: str = ''
    # The list of recommended questions configured for the bot.
    # This field will not be returned when user suggested questions are not enabled.
    suggested_questions: List[str] = []


class BotModelInfo(CozeModel):
    # The ID of the model.
    model_id: str
    # The name of the model.
    model_name: str


class BotMode(IntEnum):
    SingleAgent = 0
    MultiAgent = 1
    SingleAgentWorkflow = 2


class BotPluginAPIInfo(CozeModel):
    # The ID of the tool.
    api_id: str
    # The name of the tool.
    name: str
    # The description of the tool.
    description: str


class BotPluginInfo(CozeModel):
    # The unique identifier for the plugin.
    plugin_id: str
    # The name of the plugin.
    name: str
    # The description of the plugin.
    description: str
    # The avatar URL for the plugin.
    icon_url: str
    # The list of tool information for the plugin. For more information, see PluginAPI object.
    api_info_list: List[BotPluginAPIInfo]


class Bot(CozeModel):
    # The ID for the bot.
    bot_id: str
    # The name of the bot.
    name: str
    # The description of the bot.
    description: str
    # The URL address for the bot's avatar.
    icon_url: str
    # The creation time, in the format of a 10-digit Unix timestamp in seconds (s).
    create_time: int
    # The update time, in the format of a 10-digit Unix timestamp in seconds (s).
    update_time: int
    # The latest version of the bot.
    version: str
    # The prompt configuration for the bot. For more information, see Prompt object.
    prompt_info: BotPromptInfo
    # The onboarding message configuration for the bot. For more information, see Onboarding object.
    onboarding_info: BotOnboardingInfo
    # The mode of the Bot, values: 0: Single Agent mode, 1: Multi Agent mode, 3: Single Agent Workflow mode.
    bot_mode: BotMode
    # The plugins configured for the bot. For more information, see  Plugin object.
    plugin_info_list: List[BotPluginInfo]
    # The model configured for the bot. For more information, see Model object.
    model_info: BotModelInfo


class SimpleBot(CozeModel):
    # The ID for the bot.
    bot_id: str
    # The name of the bot.
    bot_name: str
    # The description of the bot.
    description: str
    # The URL address for the bot's avatar.
    icon_url: str
    # The latest publish time of the bot, in the format of a 10-digit Unix timestamp in seconds (s).
    # This API returns the list of bots sorted in descending order by this field.
    publish_time: str


class BotClient(object):
    """
    Bot class.
    """

    def __init__(self, base_url: str, auth: Auth, requester: Requester):
        self._base_url = base_url
        self._auth = auth
        self._requester = requester

    def get_online_info_v1(self, *, bot_id: str) -> Bot:
        """
        Get the configuration information of the bot, which must have been published
        to the Bot as API channel.

        :docs: https://www.coze.com/docs/developer_guides/get_metadata?_lang=en
        :calls: `GET /v1/bot/get_online_info`
        """
        url = f'{self._base_url}/v1/bot/get_online_info'
        params = {
            'bot_id': bot_id
        }

        return self._requester.request('get', url, Bot, params=params)

    def list_published_bots_v1(self, *,
                               space_id: str,
                               page_num: int = 1,
                               page_size: int = 20) -> NumberPaged[SimpleBot]:
        """
        Get the bots published as API service.

        :docs: https://www.coze.com/docs/developer_guides/published_bots_list?_lang=en
        :calls: `GET /v1/space/published_bots_list`
        """
        url = f'{self._base_url}/v1/space/published_bots_list'
        params = {
            'space_id': space_id,
            'page_size': page_size,
            'page_index': page_num,
        }
        data = self._requester.request('get', url, self._PrivateListPublishedBotsV1Data, params=params)
        return NumberPaged(
            items=data.space_bots,
            page_num=page_num,
            page_size=page_size,
            total=data.total,
        )

    class _PrivateListPublishedBotsV1Data(CozeModel):
        space_bots: List[SimpleBot]
        total: int
