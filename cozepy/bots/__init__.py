from enum import IntEnum
from typing import Dict, List, Optional

from pydantic import Field, field_validator

from cozepy.model import AsyncNumberPaged, CozeModel, DynamicStrEnum, NumberPaged, NumberPagedResponse
from cozepy.request import HTTPRequest, Requester
from cozepy.util import dump_exclude_none, remove_none_values, remove_url_trailing_slash


class PublishStatus(DynamicStrEnum):
    ALL = "all"  # 所有智能体，且数据为最新草稿版本
    PUBLISHED_ONLINE = "published_online"  # 已发布智能体的最新线上版本
    PUBLISHED_DRAFT = "published_draft"  # 已发布的最新草稿版本
    UNPUBLISHED_DRAFT = "unpublished_draft"  # 未发布的最新草稿版本


class BotPromptInfo(CozeModel):
    # Configured prompt of the bot.
    prompt: str


class BotOnboardingInfo(CozeModel):
    # Configured prologue of the bot.
    prologue: str = ""
    # The list of recommended questions configured for the bot.
    # This field will not be returned when user suggested questions are not enabled.
    suggested_questions: Optional[List[str]] = []


class BotKnowledge(CozeModel):
    # Configured dataset ids of the bot.
    dataset_ids: List[str] = []
    # Whether to call knowledge base automatically.
    auto_call: bool = True
    # Configured search strategy of the bot, values: 0: semantic search, 1: hybrid search, 20: full-text search.
    search_strategy: int = 0


class BotModelInfo(CozeModel):
    class ResponseFormat(DynamicStrEnum):
        JSON = "json"
        TEXT = "text"
        MARKDOWN = "markdown"

    class CacheType(DynamicStrEnum):
        """
        扣子的部分模型支持开启或关闭上下文缓存中的前缀缓存。开启前缀缓存后，可以将一些公共前缀内容进行缓存，
        后续调用模型时无需重复发送，从而加快模型的响应速度并降低使用成本。默认为 closed。支持的取值如下：
        """

        # 关闭上下文缓存。
        CLOSED = "closed"
        # 前缀缓存模式。
        PREFIX = "prefix"

    # The ID of the model.
    model_id: str
    # The name of the model.
    model_name: Optional[str] = None
    # The temperature of the model.
    temperature: Optional[float] = None
    # The context_round of the model.
    # 携带上下文轮数。
    context_round: Optional[int] = None
    # The max_tokens of the model.
    max_tokens: Optional[int] = None
    # The response format of the model.
    response_format: Optional[ResponseFormat] = None
    # The top_k of the model.
    top_k: Optional[int] = None
    # The top_p of the model.
    top_p: Optional[float] = None
    # 扣子的部分模型支持开启或关闭上下文缓存中的前缀缓存。
    cache_type: Optional[CacheType] = None
    # The presence_penalty of the model.
    # 重复主题惩罚。
    presence_penalty: Optional[float] = None
    # The frequency_penalty of the model.
    # 重复语句惩罚。
    frequency_penalty: Optional[float] = None
    # The parameters of the model.
    # claude: {"thinking_type": "disabled/enable", "thinking_budget_tokens": "2000"}
    # gemini: {"thinking_type": "disabled/enable"}
    # doubao: {"thinking_type": "auto/disabled/enable"}
    parameters: Optional[Dict[str, str]] = None
    # 是否启用 SP 拼接防泄露指令，开启后，当用户尝试获取或复述系统内部的规则、提示词或其他敏感内容时，智能体将礼貌地拒绝用户的请求，确保机密信息不被泄露。
    sp_anti_leak: Optional[bool] = None
    # 是否在 SP 中包含当前时间信息。
    sp_current_time: Optional[bool] = None


class PluginIDList(CozeModel):
    class PluginIDInfo(CozeModel):
        # 智能体绑定的插件 ID
        plugin_id: str
        # 智能体绑定的插件工具 ID
        api_id: str

    id_list: Optional[List[PluginIDInfo]] = None


class WorkflowIDList(CozeModel):
    class WorkflowIDInfo(CozeModel):
        # 智能体绑定的工作流 ID
        id: str

    ids: Optional[List[WorkflowIDInfo]] = None


class BotMode(IntEnum):
    SINGLE_AGENT = 0
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


class SuggestReplyMode(DynamicStrEnum):
    """
    配置智能体回复后，是否提供用户问题建议。
    """

    # The bot does not suggest replies.
    # 在每次智能体回复后，不会提供任何用户问题建议。
    DISABLE = "disable"
    # The bot suggests replies.
    # 在智能体回复后，提供最多 3 条用户问题建议。
    ENABLE = "enable"
    # The bot suggests replies based on the customized prompt.
    # 开启用户问题建议，并根据用户自定义的 Prompt 提供用户问题建议。你需要在 customized_prompt 参数中设置关于用户问题建议的 Prompt。
    CUSTOMIZED = "customized"


class BotSuggestReplyInfo(CozeModel):
    # 配置智能体回复后，是否提供用户问题建议。
    reply_mode: SuggestReplyMode
    # 关于用户问题建议的 Prompt。当 reply_mode 设置为 customized时，需要设置提示词内容。智能体会根据该提示词生成用户问题建议。
    customized_prompt: str = ""


class GradientPosition(CozeModel):
    left: Optional[float] = None
    right: Optional[float] = None


class CanvasPosition(CozeModel):
    width: Optional[float] = None
    height: Optional[float] = None
    left: Optional[float] = None
    top: Optional[float] = None


class BackgroundImageInfo(CozeModel):
    image_url: str = ""
    theme_color: Optional[str] = None
    gradient_position: Optional[GradientPosition] = None
    canvas_position: Optional[CanvasPosition] = None


class BotBackgroundImageInfo(CozeModel):
    web_background_image: Optional[BackgroundImageInfo] = None
    mobile_background_image: Optional[BackgroundImageInfo] = None


class VariableType(DynamicStrEnum):
    # The variable is a key-value pair.
    KVVariable = "KVVariable"
    # The variable is a list.
    ListVariable = "ListVariable"


class VariableChannel(DynamicStrEnum):
    # The variable is a custom variable.
    VariableChannelCustom = "custom"
    # The variable is a system variable.
    VariableChannelSystem = "system"
    # The variable is a location variable.
    VariableChannelLocation = "location"
    # The variable is a Feishu variable.
    VariableChannelFeishu = "feishu"
    # The variable is an app variable.
    VariableChannelAPP = "app"


class BotVariable(CozeModel):
    # The name of the variable.
    keyword: str
    # The default value of the variable.
    default_value: str
    # The type of the variable.
    variable_type: VariableType
    # The source of the variable.
    channel: VariableChannel
    # The description of the variable.
    description: str
    # Whether the variable is enabled.
    enable: bool
    # Whether the variable is supported in the prompt.
    prompt_enable: bool


class BotVoiceInfo(CozeModel):
    voice_id: str
    language_code: str


class UserInputType(DynamicStrEnum):
    """用户输入类型"""

    # 文本输入
    TEXT = "text"
    # 语音通话
    CALL = "call"
    # 语音输入
    VOICE = "voice"


class BotWorkflowInfo(CozeModel):
    id: str
    name: str
    description: str
    icon_url: str


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
    # The knowledge configuration for the bot. For more information, see Knowledge object.
    knowledge: Optional[BotKnowledge] = None
    # The mode of the Bot, values: 0: Single Agent mode, 1: Multi Agent mode, 3: Single Agent Workflow mode.
    bot_mode: Optional[BotMode] = None
    # The plugins configured for the bot. For more information, see  Plugin object.
    plugin_info_list: Optional[List[BotPluginInfo]] = None
    # The model configured for the bot. For more information, see Model object.
    model_info: Optional[BotModelInfo] = None
    # The suggest reply info for the bot.
    suggest_reply_info: Optional[BotSuggestReplyInfo] = None
    # The background image info for the bot.
    background_image_info: Optional[BotBackgroundImageInfo] = None
    # The list of variables configured for the bot. For more information, see Variable object.
    variables: Optional[List[BotVariable]] = None
    # The user ID of the bot's owner.
    owner_user_id: Optional[str] = None
    # The voice info for the bot.
    voice_info_list: Optional[List[BotVoiceInfo]] = None
    # The default user input type for the bot.
    default_user_input_type: Optional[UserInputType] = None
    # The workflow info for the bot.
    workflow_info_list: Optional[List[BotWorkflowInfo]] = None
    # The folder ID for the bot.
    folder_id: Optional[str] = None


class SimpleBot(CozeModel):
    id: str
    name: str
    description: str
    icon_url: str
    is_published: bool
    updated_at: int
    owner_user_id: str

    folder_id: Optional[str] = None
    published_at: Optional[int] = None

    # compatibility fields
    bot_id: str = Field(alias="id")
    bot_name: str = Field(alias="name")
    publish_time: str = Field(alias="updated_at")

    @field_validator("publish_time", mode="before")
    @classmethod
    def convert_to_string(cls, v):
        if isinstance(v, int):
            return str(v)
        return v


class UpdateBotResp(CozeModel):
    pass


class UnpublishBotResp(CozeModel):
    pass


class _PrivateListBotsDataV1(CozeModel, NumberPagedResponse[SimpleBot]):
    class SimpleBotV1(CozeModel):
        bot_id: str
        bot_name: str
        description: str
        icon_url: str
        publish_time: str

        def to_simple_bot(self) -> SimpleBot:
            return SimpleBot(  # type: ignore[call-arg]
                id=self.bot_id,
                name=self.bot_name,
                description=self.description,
                icon_url=self.icon_url,
                is_published=True,
                updated_at=int(self.publish_time),
                owner_user_id="",
                published_at=int(self.publish_time),
            )

    space_bots: List[SimpleBotV1]
    total: int

    def get_total(self) -> Optional[int]:
        return self.total

    def get_has_more(self) -> Optional[bool]:
        return None

    def get_items(self) -> List[SimpleBot]:
        return [bot.to_simple_bot() for bot in self.space_bots]


class _PrivateListBotsDataV2(CozeModel, NumberPagedResponse[SimpleBot]):
    items: List[SimpleBot]
    total: int

    def get_total(self) -> Optional[int]:
        return self.total

    def get_has_more(self) -> Optional[bool]:
        return None

    def get_items(self) -> List[SimpleBot]:
        return self.items


class BotsClient(object):
    """
    Bot class.
    """

    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
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
        suggest_reply_info: Optional[BotSuggestReplyInfo] = None,
        model_info_config: Optional[BotModelInfo] = None,
        plugin_id_list: Optional[PluginIDList] = None,
        workflow_id_list: Optional[WorkflowIDList] = None,
        **kwargs,
    ) -> Bot:
        """
        创建智能体

        通过指定空间、名称等参数创建一个新的智能体。

        docs: https://www.coze.cn/open/docs/developer_guides/create_bot

        :param space_id: 空间 ID。智能体将创建在此空间下。
        :param name: 智能体名称。长度限制为 1-20 个字符。
        :param description: 智能体描述。长度限制为 0-500 个字符，默认为空。
        :param icon_file_id: 智能体头像的文件 ID。如需使用自定义头像，请先通过上传文件接口上传本地文件，
        并从接口响应中获取文件 ID。如果未指定文件 ID，平台将分配默认头像。
        :param prompt_info: 智能体的提示词配置信息。
        :param onboarding_info: 智能体的开场白配置信息。
        :param suggest_reply_info: 智能体的建议回复配置信息。
        :param model_info_config: 智能体的模型配置信息。
        :param plugin_id_list: 智能体使用的插件 ID 列表。
        :param workflow_id_list: 智能体使用的工作流 ID 列表。
        :return: 创建成功的智能体对象
        """
        url = f"{self._base_url}/v1/bot/create"
        body = dump_exclude_none(
            {
                "space_id": space_id,
                "name": name,
                "description": description,
                "icon_file_id": icon_file_id,
                "prompt_info": prompt_info,
                "onboarding_info": onboarding_info,
                "suggest_reply_info": suggest_reply_info,
                "model_info_config": model_info_config,
                "plugin_id_list": plugin_id_list,
                "workflow_id_list": workflow_id_list,
            }
        )
        headers: Optional[dict] = kwargs.get("headers")

        return self._requester.request("post", url, False, Bot, body=body, headers=headers)

    def update(
        self,
        *,
        bot_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        icon_file_id: Optional[str] = None,
        prompt_info: Optional[BotPromptInfo] = None,
        onboarding_info: Optional[BotOnboardingInfo] = None,
        knowledge: Optional[BotKnowledge] = None,
        suggest_reply_info: Optional[BotSuggestReplyInfo] = None,
        model_info_config: Optional[BotModelInfo] = None,
        **kwargs,
    ) -> UpdateBotResp:
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
        :param knowledge: The knowledge base that the bot uses to answer user queries.
        :param suggest_reply_info: The suggest reply info for the bot.
        :param model_info_config: The model configuration for the bot.
        :return: None
        """
        url = f"{self._base_url}/v1/bot/update"
        body = dump_exclude_none(
            {
                "bot_id": bot_id,
                "name": name,
                "description": description,
                "icon_file_id": icon_file_id,
                "prompt_info": prompt_info,
                "onboarding_info": onboarding_info,
                "knowledge": knowledge,
                "suggest_reply_info": suggest_reply_info,
                "model_info_config": model_info_config,
            }
        )
        headers: Optional[dict] = kwargs.get("headers")

        return self._requester.request(
            "post",
            url,
            False,
            cast=UpdateBotResp,
            body=body,
            headers=headers,
        )

    def publish(self, *, bot_id: str, connector_ids: Optional[List[str]] = None, **kwargs) -> Bot:
        url = f"{self._base_url}/v1/bot/publish"
        headers: Optional[dict] = kwargs.get("headers")
        if not connector_ids:
            connector_ids = ["1024"]
        body = {
            "bot_id": bot_id,
            "connector_ids": connector_ids,
        }

        return self._requester.request("post", url, False, Bot, headers=headers, body=body)

    def unpublish(
        self, *, bot_id: str, connector_id: str, unpublish_reason: Optional[str] = None, **kwargs
    ) -> UnpublishBotResp:
        """
        下架智能体

        智能体发布后，你可以调用本 API 从扣子官方渠道及自定义渠道下架智能体。

        docs: https://www.coze.cn/open/docs/developer_guides/unpublish_agent

        :param bot_id: 待下架的智能体的 ID。
        :param connector_id: 渠道 ID，例如 "1024" 表示 API 渠道。
        :param unpublish_reason: 下架渠道的原因说明，用于记录或说明为何执行下架操作。最大 1024 个字符。
        :return: 智能体对象
        """
        url = f"{self._base_url}/v1/bots/{bot_id}/unpublish"
        headers: Optional[dict] = kwargs.get("headers")
        body = {
            "bot_id": bot_id,
            "connector_id": connector_id,
            "unpublish_reason": unpublish_reason,
        }
        return self._requester.request("post", url, False, UnpublishBotResp, headers=headers, body=body)

    def retrieve(self, *, bot_id: str, is_published: Optional[bool] = None, use_api_version: int = 1, **kwargs) -> Bot:
        """查看智能体配置

        查看指定智能体的配置信息，你可以查看该智能体已发布版本的配置，或当前草稿版本的配置。

        docs: https://www.coze.cn/open/docs/developer_guides/get_metadata_draft_published

        :param bot_id: 要查看的智能体 ID。
        :param is_published: 根据智能体的发布状态筛选对应版本。默认值为 true。
        """
        if use_api_version == 2:
            return self._retrieve_v2(bot_id=bot_id, is_published=is_published, **kwargs)
        else:
            return self._retrieve_v1(bot_id=bot_id, **kwargs)

    def _retrieve_v1(self, *, bot_id: str, **kwargs) -> Bot:
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
        headers: Optional[dict] = kwargs.get("headers")

        return self._requester.request("get", url, False, Bot, params=params, headers=headers)

    def _retrieve_v2(self, *, bot_id: str, is_published: Optional[bool] = None, **kwargs) -> Bot:
        """查看智能体配置

        查看指定智能体的配置信息，你可以查看该智能体已发布版本的配置，或当前草稿版本的配置。

        docs: https://www.coze.cn/open/docs/developer_guides/get_metadata_draft_published

        :param bot_id: 要查看的智能体 ID。
        :param is_published: 根据智能体的发布状态筛选对应版本。默认值为 true。
        """
        url = f"{self._base_url}/v1/bots/{bot_id}"
        params = remove_none_values({"is_published": is_published})
        headers: Optional[dict] = kwargs.get("headers")

        return self._requester.request("get", url, False, Bot, params=params, headers=headers)

    def list(
        self,
        *,
        space_id: str,
        publish_status: Optional[PublishStatus] = None,
        connector_id: Optional[str] = None,
        page_num: int = 1,
        page_size: int = 20,
        use_api_version: int = 1,
        **kwargs,
    ) -> NumberPaged[SimpleBot]:
        """
        查看指定空间的智能体列表

        docs en: https://www.coze.com/docs/developer_guides/published_bots_list
        docs zh: https://www.coze.cn/open/docs/developer_guides/bots_list_draft_published

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
        if use_api_version == 2:
            return self._list_v2(
                workspace_id=space_id,
                publish_status=publish_status,
                connector_id=connector_id,
                page_num=page_num,
                page_size=page_size,
            )
        else:
            return self._list_v1(
                space_id=space_id,
                page_num=page_num,
                page_size=page_size,
            )

    def _list_v1(self, *, space_id: str, page_num: int = 1, page_size: int = 20) -> NumberPaged[SimpleBot]:
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
                cast=_PrivateListBotsDataV1,
                stream=False,
            )

        return NumberPaged(
            page_num=page_num,
            page_size=page_size,
            requestor=self._requester,
            request_maker=request_maker,
        )

    def _list_v2(
        self,
        *,
        workspace_id: str,
        publish_status: Optional[PublishStatus] = None,
        connector_id: Optional[str] = None,
        page_num: int = 1,
        page_size: int = 20,
        **kwargs,
    ) -> NumberPaged[SimpleBot]:
        """
        查看指定空间的智能体列表

        docs en: https://www.coze.com/docs/developer_guides/published_bots_list
        docs zh: https://www.coze.cn/open/docs/developer_guides/bots_list_draft_published

        :param workspace_id: The ID of the space.
        Bot 所在的空间的 Space ID。Space ID 是空间的唯一标识。
        :param page_num: Pagination size. The default is 20, meaning that 20 data entries are returned per page.
        分页大小。默认为 20，即每页返回 20 条数据。
        :param page_size: Page number for paginated queries. The default is 1,
        meaning that the data return starts from the first page.
        分页查询时的页码。默认为 1，即从第一页数据开始返回。
        :return: Specify the list of Bots published to the Bot as an API channel in space.
        指定空间发布到 Bot as API 渠道的 Bot 列表。
        """
        url = f"{self._base_url}/v1/bots"
        headers: Optional[dict] = kwargs.get("headers")

        def request_maker(i_page_num: int, i_page_size: int) -> HTTPRequest:
            return self._requester.make_request(
                "GET",
                url,
                params=remove_none_values(
                    {
                        "workspace_id": workspace_id,
                        "page_size": i_page_size,
                        "page_index": i_page_num,
                        "publish_status": publish_status.value if publish_status else None,
                        "connector_id": connector_id,
                    }
                ),
                headers=headers,
                cast=_PrivateListBotsDataV2,
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

    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
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
        suggest_reply_info: Optional[BotSuggestReplyInfo] = None,
        model_info_config: Optional[BotModelInfo] = None,
        plugin_id_list: Optional[PluginIDList] = None,
        workflow_id_list: Optional[WorkflowIDList] = None,
        **kwargs,
    ) -> Bot:
        """
        创建智能体

        通过指定空间、名称等参数创建一个新的智能体。

        docs: https://www.coze.cn/open/docs/developer_guides/create_bot

        :param space_id: 空间 ID。智能体将创建在此空间下。
        :param name: 智能体名称。长度限制为 1-20 个字符。
        :param description: 智能体描述。长度限制为 0-500 个字符，默认为空。
        :param icon_file_id: 智能体头像的文件 ID。如需使用自定义头像，请先通过上传文件接口上传本地文件，
        并从接口响应中获取文件 ID。如果未指定文件 ID，平台将分配默认头像。
        :param prompt_info: 智能体的提示词配置信息。
        :param onboarding_info: 智能体的开场白配置信息。
        :param suggest_reply_info: 智能体的建议回复配置信息。
        :param model_info_config: 智能体的模型配置信息。
        :param plugin_id_list: 智能体使用的插件 ID 列表。
        :param workflow_id_list: 智能体使用的工作流 ID 列表。
        :return: 创建成功的智能体对象
        """
        url = f"{self._base_url}/v1/bot/create"
        body = dump_exclude_none(
            {
                "space_id": space_id,
                "name": name,
                "description": description,
                "icon_file_id": icon_file_id,
                "prompt_info": prompt_info,
                "onboarding_info": onboarding_info,
                "suggest_reply_info": suggest_reply_info,
                "model_info_config": model_info_config,
                "plugin_id_list": plugin_id_list,
                "workflow_id_list": workflow_id_list,
            }
        )
        headers: Optional[dict] = kwargs.get("headers")

        return await self._requester.arequest("post", url, False, Bot, body=body, headers=headers)

    async def update(
        self,
        *,
        bot_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        icon_file_id: Optional[str] = None,
        prompt_info: Optional[BotPromptInfo] = None,
        onboarding_info: Optional[BotOnboardingInfo] = None,
        knowledge: Optional[BotKnowledge] = None,
        suggest_reply_info: Optional[BotSuggestReplyInfo] = None,
        model_info_config: Optional[BotModelInfo] = None,
        **kwargs,
    ) -> UpdateBotResp:
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
        :param knowledge: The knowledge base that the bot uses to answer user queries.
        :param suggest_reply_info: The suggest reply info for the bot.
        :param model_info_config: The model configuration for the bot.
        :return: None
        """
        url = f"{self._base_url}/v1/bot/update"
        body = dump_exclude_none(
            {
                "bot_id": bot_id,
                "name": name,
                "description": description,
                "icon_file_id": icon_file_id,
                "prompt_info": prompt_info,
                "onboarding_info": onboarding_info,
                "knowledge": knowledge,
                "suggest_reply_info": suggest_reply_info,
                "model_info_config": model_info_config,
            }
        )
        headers: Optional[dict] = kwargs.get("headers")

        return await self._requester.arequest("post", url, False, cast=UpdateBotResp, body=body, headers=headers)

    async def publish(
        self,
        *,
        bot_id: str,
        connector_ids: Optional[List[str]] = None,
        **kwargs,
    ) -> Bot:
        url = f"{self._base_url}/v1/bot/publish"
        headers: Optional[dict] = kwargs.get("headers")
        if not connector_ids:
            connector_ids = ["1024"]
        body = {
            "bot_id": bot_id,
            "connector_ids": connector_ids,
        }

        return await self._requester.arequest("post", url, False, Bot, headers=headers, body=body)

    async def unpublish(
        self, *, bot_id: str, connector_id: str, unpublish_reason: Optional[str] = None, **kwargs
    ) -> UnpublishBotResp:
        """
        下架智能体

        智能体发布后，你可以调用本 API 从扣子官方渠道及自定义渠道下架智能体。

        docs: https://www.coze.cn/open/docs/developer_guides/unpublish_agent

        :param bot_id: 待下架的智能体的 ID。
        :param connector_id: 渠道 ID，例如 "1024" 表示 API 渠道。
        :param unpublish_reason: 下架渠道的原因说明，用于记录或说明为何执行下架操作。最大 1024 个字符。
        :return: 智能体对象
        """
        url = f"{self._base_url}/v1/bots/{bot_id}/unpublish"
        headers: Optional[dict] = kwargs.get("headers")
        body = {
            "bot_id": bot_id,
            "connector_id": connector_id,
            "unpublish_reason": unpublish_reason,
        }
        return await self._requester.arequest("post", url, False, UnpublishBotResp, headers=headers, body=body)

    async def retrieve(
        self, *, bot_id: str, is_published: Optional[bool] = None, use_api_version: int = 1, **kwargs
    ) -> Bot:
        """查看智能体配置

        查看指定智能体的配置信息，你可以查看该智能体已发布版本的配置，或当前草稿版本的配置。

        docs: https://www.coze.cn/open/docs/developer_guides/get_metadata_draft_published

        :param bot_id: 要查看的智能体 ID。
        :param is_published: 根据智能体的发布状态筛选对应版本。默认值为 true。
        """
        if use_api_version == 2:
            return await self._retrieve_v2(bot_id=bot_id, is_published=is_published, **kwargs)
        else:
            return await self._retrieve_v1(bot_id=bot_id, **kwargs)

    async def _retrieve_v1(self, *, bot_id: str, **kwargs) -> Bot:
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
        headers: Optional[dict] = kwargs.get("headers")

        return await self._requester.arequest("get", url, False, Bot, params=params, headers=headers)

    async def _retrieve_v2(self, *, bot_id: str, is_published: Optional[bool] = None, **kwargs) -> Bot:
        """查看智能体配置

        查看指定智能体的配置信息，你可以查看该智能体已发布版本的配置，或当前草稿版本的配置。

        docs: https://www.coze.cn/open/docs/developer_guides/get_metadata_draft_published

        :param bot_id: 要查看的智能体 ID。
        :param is_published: 根据智能体的发布状态筛选对应版本。默认值为 true。
        """
        url = f"{self._base_url}/v1/bots/{bot_id}"
        params = remove_none_values({"is_published": is_published})
        headers: Optional[dict] = kwargs.get("headers")

        return await self._requester.arequest("get", url, False, Bot, params=params, headers=headers)

    async def list(
        self,
        *,
        space_id: str,
        publish_status: Optional[PublishStatus] = None,
        connector_id: Optional[str] = None,
        page_num: int = 1,
        page_size: int = 20,
        use_api_version: int = 1,
        **kwargs,
    ) -> AsyncNumberPaged[SimpleBot]:
        """
        查看指定空间的智能体列表

        docs en: https://www.coze.com/docs/developer_guides/published_bots_list
        docs zh: https://www.coze.cn/open/docs/developer_guides/bots_list_draft_published

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
        if use_api_version == 2:
            return await self._list_v2(
                workspace_id=space_id,
                publish_status=publish_status,
                connector_id=connector_id,
                page_num=page_num,
                page_size=page_size,
                **kwargs,
            )
        else:
            return await self._list_v1(space_id=space_id, page_num=page_num, page_size=page_size, **kwargs)

    async def _list_v1(
        self, *, space_id: str, page_num: int = 1, page_size: int = 20, **kwargs
    ) -> AsyncNumberPaged[SimpleBot]:
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

        async def request_maker(i_page_num: int, i_page_size: int) -> HTTPRequest:
            return await self._requester.amake_request(
                "GET",
                url,
                params={
                    "space_id": space_id,
                    "page_size": i_page_size,
                    "page_index": i_page_num,
                },
                cast=_PrivateListBotsDataV1,
                stream=False,
            )

        return await AsyncNumberPaged.build(
            page_num=page_num,
            page_size=page_size,
            requestor=self._requester,
            request_maker=request_maker,
        )

    async def _list_v2(
        self,
        *,
        workspace_id: str,
        publish_status: Optional[PublishStatus] = None,
        connector_id: Optional[str] = None,
        page_num: int = 1,
        page_size: int = 20,
        **kwargs,
    ) -> AsyncNumberPaged[SimpleBot]:
        """
        查看指定空间的智能体列表

        docs en: https://www.coze.com/docs/developer_guides/published_bots_list
        docs zh: https://www.coze.cn/open/docs/developer_guides/bots_list_draft_published

        :param workspace_id: The ID of the space.
        Bot 所在的空间的 Space ID。Space ID 是空间的唯一标识。
        :param page_num: Pagination size. The default is 20, meaning that 20 data entries are returned per page.
        分页大小。默认为 20，即每页返回 20 条数据。
        :param page_size: Page number for paginated queries. The default is 1,
        meaning that the data return starts from the first page.
        分页查询时的页码。默认为 1，即从第一页数据开始返回。
        :return: Specify the list of Bots published to the Bot as an API channel in space.
        指定空间发布到 Bot as API 渠道的 Bot 列表。
        """
        url = f"{self._base_url}/v1/bots"
        headers: Optional[dict] = kwargs.get("headers")

        async def request_maker(i_page_num: int, i_page_size: int) -> HTTPRequest:
            return await self._requester.amake_request(
                "GET",
                url,
                params=remove_none_values(
                    {
                        "workspace_id": workspace_id,
                        "page_size": i_page_size,
                        "page_index": i_page_num,
                        "publish_status": publish_status.value if publish_status else None,
                        "connector_id": connector_id,
                    }
                ),
                headers=headers,
                cast=_PrivateListBotsDataV2,
                stream=False,
            )

        return await AsyncNumberPaged.build(
            page_num=page_num,
            page_size=page_size,
            requestor=self._requester,
            request_maker=request_maker,
        )
