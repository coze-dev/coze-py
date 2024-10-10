from enum import IntEnum
from typing import List, Optional

from cozepy.auth import Auth
from cozepy.model import AsyncNumberPaged, CozeModel, NumberPaged, NumberPagedResponse
from cozepy.request import HTTPRequest, Requester


class BotPromptInfo(CozeModel):
    # Configured prompt of the bot.
    prompt: str


class BotOnboardingInfo(CozeModel):
    # Configured prologue of the bot.
    prologue: str = ""
    # The list of recommended questions configured for the bot.
    # This field will not be returned when user suggested questions are not enabled.
    suggested_questions: List[str] = []


class BotModelInfo(CozeModel):
    # The ID of the model.
    model_id: str
    # The name of the model.
    model_name: str


class BotMode(IntEnum):
    SINGL_EAGENT = 0
    MULTI_AGENT = 1
    SINGLE_AGENT_WORKFLOW = 2


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
    name: Optional[str] = None
    # The description of the bot.
    description: Optional[str] = None
    # The URL address for the bot's avatar.
    icon_url: Optional[str] = None
    # The creation time, in the format of a 10-digit Unix timestamp in seconds (s).
    create_time: Optional[int] = None
    # The update time, in the format of a 10-digit Unix timestamp in seconds (s).
    update_time: Optional[int] = None
    # The latest version of the bot.
    version: Optional[str] = None
    # The prompt configuration for the bot. For more information, see Prompt object.
    prompt_info: Optional[BotPromptInfo] = None
    # The onboarding message configuration for the bot. For more information, see Onboarding object.
    onboarding_info: Optional[BotOnboardingInfo] = None
    # The mode of the Bot, values: 0: Single Agent mode, 1: Multi Agent mode, 3: Single Agent Workflow mode.
    bot_mode: Optional[BotMode] = None
    # The plugins configured for the bot. For more information, see  Plugin object.
    plugin_info_list: Optional[List[BotPluginInfo]] = None
    # The model configured for the bot. For more information, see Model object.
    model_info: Optional[BotModelInfo] = None


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


class _PrivateListBotsData(CozeModel, NumberPagedResponse[SimpleBot]):
    space_bots: List[SimpleBot]
    total: int

    def get_total(self) -> int:
        return self.total

    def get_items(self) -> List[SimpleBot]:
        return self.space_bots


class BotsClient(object):
    """
    Bot class.
    """

    def __init__(self, base_url: str, auth: Auth, requester: Requester):
        self._base_url = base_url
        self._auth = auth
        self._requester = requester

    def create(
        self,
        *,
        space_id: str,
        name: str,
        description: Optional[str] = None,
        icon_file_id: Optional[str] = None,
        prompt_info: Optional[BotPromptInfo] = None,
        onboarding_info: Optional[BotOnboardingInfo] = None,
    ) -> Bot:
        url = f"{self._base_url}/v1/bot/create"
        body = {
            "space_id": space_id,
            "name": name,
            "description": description,
            "icon_file_id": icon_file_id,
            "prompt_info": prompt_info.model_dump() if prompt_info else None,
            "onboarding_info": onboarding_info.model_dump() if onboarding_info else None,
        }

        return self._requester.request("post", url, False, Bot, body=body)

    def update(
        self,
        *,
        bot_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        icon_file_id: Optional[str] = None,
        prompt_info: Optional[BotPromptInfo] = None,
        onboarding_info: Optional[BotOnboardingInfo] = None,
    ) -> None:
        """
        Update the configuration of a bot.
        This API can be used to update all bots created through the Coze platform or via the API.
        In addition to updating the bot's name and description, avatar, personality and reply logic,
        and opening remarks, this API also supports binding a knowledge base to the bot.

        docs en: https://www.coze.com/docs/developer_guides/update_bot
        docs zh: https://www.coze.cn/docs/developer_guides/update_bot

        :param bot_id: The ID of the bot that the API interacts with.
        :param name: The name of the bot. It should be 1 to 20 characters long.
        :param description: The description of the Bot. It can be 0 to 500 characters long. The default is empty.
        :param icon_file_id: The file ID for the Bot's avatar. If no file ID is specified, the Coze platform will
        assign a default avatar for the bot. To use a custom avatar, first upload the local file through the Upload
        file interface and obtain the file ID from the interface response.
        :param prompt_info: The personality and reply logic of the bot.
        :param onboarding_info: The settings related to the bot's opening remarks.
        :return: None
        """
        url = f"{self._base_url}/v1/bot/update"
        body = {
            "bot_id": bot_id,
            "name": name,
            "description": description,
            "icon_file_id": icon_file_id,
            "prompt_info": prompt_info.model_dump() if prompt_info else None,
            "onboarding_info": onboarding_info.model_dump() if onboarding_info else None,
        }

        return self._requester.request(
            "post",
            url,
            False,
            None,
            body=body,
        )

    def publish(
        self,
        *,
        bot_id: str,
        connector_ids: Optional[List[str]] = None,
    ) -> Bot:
        url = f"{self._base_url}/v1/bot/publish"
        if not connector_ids:
            connector_ids = ["API"]
        body = {
            "bot_id": bot_id,
            "connector_ids": connector_ids,
        }

        return self._requester.request("post", url, False, Bot, body=body)

    def retrieve(self, *, bot_id: str) -> Bot:
        """
        Get the configuration information of the bot, which must have been published
        to the Bot as API channel.
        获取指定 Bot 的配置信息，此 Bot 必须已发布到 Bot as API 渠道中。

        docs en: https://www.coze.com/docs/developer_guides/get_metadata
        docs zh: https://www.coze.cn/docs/developer_guides/get_metadata

        :param bot_id: The ID of the bot that the API interacts with.
        要查看的 Bot ID。
        :return: bot object
        Bot 的配置信息
        """
        url = f"{self._base_url}/v1/bot/get_online_info"
        params = {"bot_id": bot_id}

        return self._requester.request("get", url, False, Bot, params=params)

    def list(self, *, space_id: str, page_num: int = 1, page_size: int = 20) -> NumberPaged[SimpleBot]:
        """
        Get the bots published as API service.
        查看指定空间发布到 Bot as API 渠道的 Bot 列表。

        docs en: https://www.coze.com/docs/developer_guides/published_bots_list
        docs zh: https://www.coze.cn/docs/developer_guides/published_bots_list

        :param space_id: The ID of the space.
        Bot 所在的空间的 Space ID。Space ID 是空间的唯一标识。
        :param page_num: Pagination size. The default is 20, meaning that 20 data entries are returned per page.
        分页大小。默认为 20，即每页返回 20 条数据。
        :param page_size: Page number for paginated queries. The default is 1,
        meaning that the data return starts from the first page.
        分页查询时的页码。默认为 1，即从第一页数据开始返回。
        :return: Specify the list of Bots published to the Bot as an API channel in space.
        指定空间发布到 Bot as API 渠道的 Bot 列表。
        """
        url = f"{self._base_url}/v1/space/published_bots_list"

        def request_maker(i_page_num: int, i_page_size: int) -> HTTPRequest:
            return self._requester.make_request(
                "GET",
                url,
                params={
                    "space_id": space_id,
                    "page_size": i_page_size,
                    "page_index": i_page_num,
                },
                cast=_PrivateListBotsData,
                is_async=False,
                stream=False,
            )

        return NumberPaged(
            page_num=page_num,
            page_size=page_size,
            requestor=self._requester,
            request_maker=request_maker,
        )


class AsyncBotsClient(object):
    """
    Bot class.
    """

    def __init__(self, base_url: str, auth: Auth, requester: Requester):
        self._base_url = base_url
        self._auth = auth
        self._requester = requester

    async def create(
        self,
        *,
        space_id: str,
        name: str,
        description: Optional[str] = None,
        icon_file_id: Optional[str] = None,
        prompt_info: Optional[BotPromptInfo] = None,
        onboarding_info: Optional[BotOnboardingInfo] = None,
    ) -> Bot:
        url = f"{self._base_url}/v1/bot/create"
        body = {
            "space_id": space_id,
            "name": name,
            "description": description,
            "icon_file_id": icon_file_id,
            "prompt_info": prompt_info.model_dump() if prompt_info else None,
            "onboarding_info": onboarding_info.model_dump() if onboarding_info else None,
        }

        return await self._requester.arequest("post", url, False, Bot, body=body)

    async def update(
        self,
        *,
        bot_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        icon_file_id: Optional[str] = None,
        prompt_info: Optional[BotPromptInfo] = None,
        onboarding_info: Optional[BotOnboardingInfo] = None,
    ) -> None:
        """
        Update the configuration of a bot.
        This API can be used to update all bots created through the Coze platform or via the API.
        In addition to updating the bot's name and description, avatar, personality and reply logic,
        and opening remarks, this API also supports binding a knowledge base to the bot.

        docs en: https://www.coze.com/docs/developer_guides/update_bot
        docs zh: https://www.coze.cn/docs/developer_guides/update_bot

        :param bot_id: The ID of the bot that the API interacts with.
        :param name: The name of the bot. It should be 1 to 20 characters long.
        :param description: The description of the Bot. It can be 0 to 500 characters long. The default is empty.
        :param icon_file_id: The file ID for the Bot's avatar. If no file ID is specified, the Coze platform will
        assign a default avatar for the bot. To use a custom avatar, first upload the local file through the Upload
        file interface and obtain the file ID from the interface response.
        :param prompt_info: The personality and reply logic of the bot.
        :param onboarding_info: The settings related to the bot's opening remarks.
        :return: None
        """
        url = f"{self._base_url}/v1/bot/update"
        body = {
            "bot_id": bot_id,
            "name": name,
            "description": description,
            "icon_file_id": icon_file_id,
            "prompt_info": prompt_info.model_dump() if prompt_info else None,
            "onboarding_info": onboarding_info.model_dump() if onboarding_info else None,
        }

        return await self._requester.arequest("post", url, False, None, body=body)

    async def publish(
        self,
        *,
        bot_id: str,
        connector_ids: Optional[List[str]] = None,
    ) -> Bot:
        url = f"{self._base_url}/v1/bot/publish"
        if not connector_ids:
            connector_ids = ["API"]
        body = {
            "bot_id": bot_id,
            "connector_ids": connector_ids,
        }

        return await self._requester.arequest("post", url, False, Bot, body=body)

    async def retrieve(self, *, bot_id: str) -> Bot:
        """
        Get the configuration information of the bot, which must have been published
        to the Bot as API channel.
        获取指定 Bot 的配置信息，此 Bot 必须已发布到 Bot as API 渠道中。

        docs en: https://www.coze.com/docs/developer_guides/get_metadata
        docs zh: https://www.coze.cn/docs/developer_guides/get_metadata

        :param bot_id: The ID of the bot that the API interacts with.
        要查看的 Bot ID。
        :return: bot object
        Bot 的配置信息
        """
        url = f"{self._base_url}/v1/bot/get_online_info"
        params = {"bot_id": bot_id}

        return await self._requester.arequest("get", url, False, Bot, params=params)

    async def list(self, *, space_id: str, page_num: int = 1, page_size: int = 20) -> AsyncNumberPaged[SimpleBot]:
        """
        Get the bots published as API service.
        查看指定空间发布到 Bot as API 渠道的 Bot 列表。

        docs en: https://www.coze.com/docs/developer_guides/published_bots_list
        docs zh: https://www.coze.cn/docs/developer_guides/published_bots_list

        :param space_id: The ID of the space.
        Bot 所在的空间的 Space ID。Space ID 是空间的唯一标识。
        :param page_num: Pagination size. The default is 20, meaning that 20 data entries are returned per page.
        分页大小。默认为 20，即每页返回 20 条数据。
        :param page_size: Page number for paginated queries. The default is 1,
        meaning that the data return starts from the first page.
        分页查询时的页码。默认为 1，即从第一页数据开始返回。
        :return: Specify the list of Bots published to the Bot as an API channel in space.
        指定空间发布到 Bot as API 渠道的 Bot 列表。
        """
        url = f"{self._base_url}/v1/space/published_bots_list"

        def request_maker(i_page_num: int, i_page_size: int) -> HTTPRequest:
            return self._requester.make_request(
                "GET",
                url,
                params={
                    "space_id": space_id,
                    "page_size": i_page_size,
                    "page_index": i_page_num,
                },
                cast=_PrivateListBotsData,
                is_async=False,
                stream=False,
            )

        return await AsyncNumberPaged.build(
            page_num=page_num,
            page_size=page_size,
            requestor=self._requester,
            request_maker=request_maker,
        )
