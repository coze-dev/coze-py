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
    # 文本prompt
    prompt: str


class BotOnboardingInfo(CozeModel):
    # 对应 Coze Opening Dialog开场白
    prologue: str = ""
    # 建议问题
    suggested_questions: Optional[List[str]] = []


class BotKnowledge(CozeModel):
    # 更新知识库列表 全量覆盖更新
    dataset_ids: List[str] = []
    # 自动调用 or 按需调用
    auto_call: bool = True
    # 搜索策略
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

    # 模型id
    model_id: str
    # The name of the model.
    model_name: Optional[str] = None
    # 生成随机性
    temperature: Optional[float] = None
    # 携带上下文轮数
    context_round: Optional[int] = None
    # 最大回复长度
    max_tokens: Optional[int] = None
    # 输出格式 text、markdown、json
    response_format: Optional[ResponseFormat] = None
    # 生成时，采样候选集的大小
    top_k: Optional[int] = None
    # top p
    top_p: Optional[float] = None
    # 缓存配置
    cache_type: Optional[CacheType] = None
    # 存在惩罚
    presence_penalty: Optional[float] = None
    # 频率惩罚
    frequency_penalty: Optional[float] = None
    # 模型个性化配置参数
    parameters: Optional[Dict[str, str]] = None
    # sp拼接防泄露指令
    sp_anti_leak: Optional[bool] = None
    # sp拼接当前时间
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
    # api id
    api_id: str
    # api名称
    name: str
    # api描述
    description: str


class BotPluginInfo(CozeModel):
    # 插件id
    plugin_id: str
    # 插件名称
    name: str
    # 插件描述
    description: str
    # 插件图片url
    icon_url: str
    # 插件包含的api列表
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
    # 回复模式
    reply_mode: SuggestReplyMode
    # custom 模式下的自定义 prompt
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
    # 变量名
    keyword: str
    # 默认值
    default_value: str
    # The type of the variable.
    variable_type: VariableType
    # The source of the variable.
    channel: VariableChannel
    # 变量描述
    description: str
    # 是否启用
    enable: bool
    # 变量默认支持在Prompt中访问，取消勾选后将不支持在Prompt中访问（仅能在Workflow中访问
    prompt_enable: bool


class BotVoiceInfo(CozeModel):
    # 唯一id
    voice_id: str
    # 音色语种code
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
    # workflow_id
    id: str
    # workflow名称
    name: str
    # workflow描述
    description: str
    # workflow图片url
    icon_url: str


class Bot(CozeModel):
    # bot id
    bot_id: str
    # bot名称
    name: Optional[str] = None
    # bot描述
    description: Optional[str] = None
    # bot图像url
    icon_url: Optional[str] = None
    # 创建时间
    create_time: Optional[int] = None
    # 更新时间
    update_time: Optional[int] = None
    # 版本
    version: Optional[str] = None
    # The prompt configuration for the bot. For more information, see Prompt object.
    prompt_info: Optional[BotPromptInfo] = None
    # The onboarding message configuration for the bot. For more information, see Onboarding object.
    onboarding_info: Optional[BotOnboardingInfo] = None
    # The knowledge configuration for the bot. For more information, see Knowledge object.
    knowledge: Optional[BotKnowledge] = None
    # The mode of the Bot, values: 0: Single Agent mode, 1: Multi Agent mode, 3: Single Agent Workflow mode.
    bot_mode: Optional[BotMode] = None
    # 插件信息列表
    plugin_info_list: Optional[List[BotPluginInfo]] = None
    # The model configured for the bot. For more information, see Model object.
    model_info: Optional[BotModelInfo] = None
    # The suggest reply info for the bot.
    suggest_reply_info: Optional[BotSuggestReplyInfo] = None
    # The background image info for the bot.
    background_image_info: Optional[BotBackgroundImageInfo] = None
    # 变量列表
    variables: Optional[List[BotVariable]] = None
    # owner_id
    owner_user_id: Optional[str] = None
    # 音色配置
    voice_info_list: Optional[List[BotVoiceInfo]] = None
    # 默认用户输入类型
    default_user_input_type: Optional[UserInputType] = None
    # workflow信息列表
    workflow_info_list: Optional[List[BotWorkflowInfo]] = None
    # The folder ID for the bot.
    folder_id: Optional[str] = None


class SimpleBot(CozeModel):
    id: str
    name: str
    description: str
    icon_url: str
    is_published: bool
    # 草稿返回update_time
    updated_at: int
    owner_user_id: str
    folder_id: Optional[str] = None
    # 发布态返回publish_time
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

        创建一个新的智能体。 创建的智能体为未发布的草稿状态，创建后可以在扣子编程智能体列表中查看智能体。调用 发布智能体 API 发布智能体后，才能通过 查看智能体列表 或 查看智能体配置 API 查看此智能体。 通过 API 方式创建智能体时，支持为智能体设置所在空间、智能体名称和描述、头像、人设与回复逻辑及开场白。

        :param icon_file_id: 头像文件id
        """
        url = f"{self._base_url}/v1/bot/create"
        headers: Optional[dict] = kwargs.get("headers")
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
        return self._requester.request("post", url, False, cast=Bot, headers=headers, body=body)

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
        更新智能体

        更新智能体的配置。 通过此 API 可更新通过扣子编程或 API 方式创建的所有智能体。通过 API 方式修改智能体除了智能体名称和描述、头像、人设与回复逻辑及开场白之外，还支持为智能体绑定知识库和插件。 接口限制 不支持通过 API 绑定火山知识库，只能绑定扣子知识库。
        """
        url = f"{self._base_url}/v1/bot/update"
        headers: Optional[dict] = kwargs.get("headers")
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
        return self._requester.request(
            "post",
            url,
            False,
            cast=UpdateBotResp,
            headers=headers,
            body=body,
        )

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

    def publish(self, *, bot_id: str, connector_ids: Optional[List[str]] = None, **kwargs) -> Bot:
        """
        发布智能体

        将指定智能体发布到 API、Chat SDK 或者自定义渠道。
        """
        url = f"{self._base_url}/v1/bot/publish"
        headers: Optional[dict] = kwargs.get("headers")
        if not connector_ids:
            connector_ids = ["1024"]
        body = {
            "bot_id": bot_id,
            "connector_ids": connector_ids,
        }

        return self._requester.request("post", url, False, cast=Bot, headers=headers, body=body)

    def unpublish(
        self,
        *,
        bot_id: str,
        connector_id: str,
        unpublish_reason: Optional[str] = None,
        **kwargs,
    ) -> UnpublishBotResp:
        """
        下架智能体

        智能体发布后，你可以调用本 API 从扣子官方渠道及自定义渠道下架智能体。 接口限制 仅智能体所有者可以下架智能体。 暂不支持调用本 API 下架豆包渠道的智能体。

        :param bot_id: 待下架的智能体的 ID。你可通过智能体开发页面 URL 中的 `bot` 参数获取智能体 ID 。例如 URL 为 `https://www.coze.com/space/341****/bot/73428668*****` 时，智能体 ID 为 `73428668*****`。
        """
        url = f"{self._base_url}/v1/bots/{bot_id}/unpublish"
        headers: Optional[dict] = kwargs.get("headers")
        body = {
            "bot_id": bot_id,
            "connector_id": connector_id,
            "unpublish_reason": unpublish_reason,
        }
        return self._requester.request("post", url, False, cast=UnpublishBotResp, headers=headers, body=body)

    def _retrieve_v1(self, *, bot_id: str, **kwargs) -> Bot:
        """
        获取已发布智能体配置（即将下线）

        获取指定智能体的配置信息，此智能体必须已发布到 Agent as API 渠道中。 此接口仅支持查看已发布为 API 服务的智能体。对于创建后从未发布到 API 渠道的智能体，可以在 扣子平台 中查看列表及配置。

        :param bot_id: 要查看的智能体 ID。 进入智能体的 开发页面，开发页面 URL 中 `bot` 参数后的数字就是智能体 ID。例如`https://www.coze.cn/space/341****/bot/73428668*****`，bot ID 为`73428668*****`。 确保该智能体的所属空间已经生成了访问令牌。
        """
        url = f"{self._base_url}/v1/bot/get_online_info"
        params = {"bot_id": bot_id}
        headers: Optional[dict] = kwargs.get("headers")
        return self._requester.request("get", url, False, cast=Bot, params=params, headers=headers)

    def _retrieve_v2(self, *, bot_id: str, is_published: Optional[bool] = None, **kwargs) -> Bot:
        """
        查看智能体配置

        查看指定智能体的配置信息，你可以查看该智能体已发布版本的配置，或当前草稿版本的配置。

        :param bot_id: 要查看的智能体 ID。 进入智能体的开发页面，开发页面 URL 中 `bot` 参数后的数字就是智能体 ID。例如`https://www.coze.cn/space/341****/bot/73428668*****`，bot ID 为`73428668*****`。 确保该智能体的所属空间已经生成了访问令牌。
        :param is_published: 根据智能体的发布状态筛选对应版本。默认值为 `true`。 * `true` ：查看已发布版本的配置。 * `false` ：查看当前草稿版本的配置。
        """
        url = f"{self._base_url}/v1/bots/{bot_id}"
        params = remove_none_values({"is_published": is_published})
        headers: Optional[dict] = kwargs.get("headers")
        return self._requester.request("get", url, False, cast=Bot, params=params, headers=headers)

    def _list_v1(
        self,
        *,
        space_id: str,
        page_num: int = 1,
        page_size: int = 20,
        **kwargs,
    ) -> NumberPaged[SimpleBot]:
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
        headers: Optional[dict] = kwargs.get("headers")

        def request_maker(i_page_num: int, i_page_size: int) -> HTTPRequest:
            return self._requester.make_request(
                "GET",
                url,
                headers=headers,
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
                headers=headers,
                params=remove_none_values(
                    {
                        "workspace_id": workspace_id,
                        "page_size": i_page_size,
                        "page_index": i_page_num,
                        "publish_status": publish_status.value if publish_status else None,
                        "connector_id": connector_id,
                    }
                ),
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

        创建一个新的智能体。 创建的智能体为未发布的草稿状态，创建后可以在扣子编程智能体列表中查看智能体。调用 发布智能体 API 发布智能体后，才能通过 查看智能体列表 或 查看智能体配置 API 查看此智能体。 通过 API 方式创建智能体时，支持为智能体设置所在空间、智能体名称和描述、头像、人设与回复逻辑及开场白。

        :param icon_file_id: 头像文件id
        """
        url = f"{self._base_url}/v1/bot/create"
        headers: Optional[dict] = kwargs.get("headers")
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
        return await self._requester.arequest("post", url, False, cast=Bot, headers=headers, body=body)

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
        更新智能体

        更新智能体的配置。 通过此 API 可更新通过扣子编程或 API 方式创建的所有智能体。通过 API 方式修改智能体除了智能体名称和描述、头像、人设与回复逻辑及开场白之外，还支持为智能体绑定知识库和插件。 接口限制 不支持通过 API 绑定火山知识库，只能绑定扣子知识库。
        """
        url = f"{self._base_url}/v1/bot/update"
        headers: Optional[dict] = kwargs.get("headers")
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
        return await self._requester.arequest("post", url, False, cast=UpdateBotResp, headers=headers, body=body)

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

    async def publish(
        self,
        *,
        bot_id: str,
        connector_ids: Optional[List[str]] = None,
        **kwargs,
    ) -> Bot:
        """
        发布智能体

        将指定智能体发布到 API、Chat SDK 或者自定义渠道。
        """
        url = f"{self._base_url}/v1/bot/publish"
        headers: Optional[dict] = kwargs.get("headers")
        if not connector_ids:
            connector_ids = ["1024"]
        body = {
            "bot_id": bot_id,
            "connector_ids": connector_ids,
        }

        return await self._requester.arequest("post", url, False, cast=Bot, headers=headers, body=body)

    async def unpublish(
        self,
        *,
        bot_id: str,
        connector_id: str,
        unpublish_reason: Optional[str] = None,
        **kwargs,
    ) -> UnpublishBotResp:
        """
        下架智能体

        智能体发布后，你可以调用本 API 从扣子官方渠道及自定义渠道下架智能体。 接口限制 仅智能体所有者可以下架智能体。 暂不支持调用本 API 下架豆包渠道的智能体。

        :param bot_id: 待下架的智能体的 ID。你可通过智能体开发页面 URL 中的 `bot` 参数获取智能体 ID 。例如 URL 为 `https://www.coze.com/space/341****/bot/73428668*****` 时，智能体 ID 为 `73428668*****`。
        """
        url = f"{self._base_url}/v1/bots/{bot_id}/unpublish"
        headers: Optional[dict] = kwargs.get("headers")
        body = {
            "bot_id": bot_id,
            "connector_id": connector_id,
            "unpublish_reason": unpublish_reason,
        }
        return await self._requester.arequest("post", url, False, cast=UnpublishBotResp, headers=headers, body=body)

    async def _retrieve_v1(self, *, bot_id: str, **kwargs) -> Bot:
        """
        获取已发布智能体配置（即将下线）

        获取指定智能体的配置信息，此智能体必须已发布到 Agent as API 渠道中。 此接口仅支持查看已发布为 API 服务的智能体。对于创建后从未发布到 API 渠道的智能体，可以在 扣子平台 中查看列表及配置。

        :param bot_id: 要查看的智能体 ID。 进入智能体的 开发页面，开发页面 URL 中 `bot` 参数后的数字就是智能体 ID。例如`https://www.coze.cn/space/341****/bot/73428668*****`，bot ID 为`73428668*****`。 确保该智能体的所属空间已经生成了访问令牌。
        """
        url = f"{self._base_url}/v1/bot/get_online_info"
        params = {"bot_id": bot_id}
        headers: Optional[dict] = kwargs.get("headers")
        return await self._requester.arequest("get", url, False, cast=Bot, params=params, headers=headers)

    async def _retrieve_v2(self, *, bot_id: str, is_published: Optional[bool] = None, **kwargs) -> Bot:
        """
        查看智能体配置

        查看指定智能体的配置信息，你可以查看该智能体已发布版本的配置，或当前草稿版本的配置。

        :param bot_id: 要查看的智能体 ID。 进入智能体的开发页面，开发页面 URL 中 `bot` 参数后的数字就是智能体 ID。例如`https://www.coze.cn/space/341****/bot/73428668*****`，bot ID 为`73428668*****`。 确保该智能体的所属空间已经生成了访问令牌。
        :param is_published: 根据智能体的发布状态筛选对应版本。默认值为 `true`。 * `true` ：查看已发布版本的配置。 * `false` ：查看当前草稿版本的配置。
        """
        url = f"{self._base_url}/v1/bots/{bot_id}"
        params = remove_none_values({"is_published": is_published})
        headers: Optional[dict] = kwargs.get("headers")
        return await self._requester.arequest("get", url, False, cast=Bot, params=params, headers=headers)

    async def _list_v1(
        self,
        *,
        space_id: str,
        page_num: int = 1,
        page_size: int = 20,
        **kwargs,
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
        headers: Optional[dict] = kwargs.get("headers")

        async def request_maker(i_page_num: int, i_page_size: int) -> HTTPRequest:
            return await self._requester.amake_request(
                "GET",
                url,
                headers=headers,
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
                headers=headers,
                params=remove_none_values(
                    {
                        "workspace_id": workspace_id,
                        "page_size": i_page_size,
                        "page_index": i_page_num,
                        "publish_status": publish_status.value if publish_status else None,
                        "connector_id": connector_id,
                    }
                ),
                cast=_PrivateListBotsDataV2,
                stream=False,
            )

        return await AsyncNumberPaged.build(
            page_num=page_num,
            page_size=page_size,
            requestor=self._requester,
            request_maker=request_maker,
        )
