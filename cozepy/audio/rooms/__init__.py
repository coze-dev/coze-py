from typing import Optional

from pydantic import Field

from cozepy.model import CozeModel, DynamicStrEnum
from cozepy.request import Requester
from cozepy.util import remove_none_values, remove_url_trailing_slash


class RoomAudioConfig(CozeModel):
    # 房间音频编码格式，支持设置为：
    # AACLC: AAC-LC 编码格式。
    # G711A: G711A 编码格式。
    # OPUS: （默认）Opus 编码格式。
    # G722: G.722 编码格式。
    codec: Optional[str]


class RoomVideoConfig(CozeModel):
    # 房间视频编码格式，支持设置为：
    # H264:（默认）H264 编码格式。
    # BYTEVC1: 火山引擎自研的视频编码格式。
    codec: Optional[str]
    # 房间视频流类型, 支持 main 和 screen。
    # main: 主流，包括通过摄像头/麦克风的内部采集机制获取的流，以及通过自定义采集方式获取的流。
    # screen: 屏幕流，用于屏幕共享或屏幕录制的视频流。
    stream_video_type: Optional[str]
    # 视频抽帧速率, 默认值是 1, 范围 [1, 24]
    video_frame_rate: Optional[int]
    # 视频帧过期时间,单位为s，默认值是1，范围[1, 10]
    video_frame_expire_duration: Optional[int]


class RoomMode(DynamicStrEnum):
    DEFAULT = "default"
    S2S = "s2s"
    PODCAST = "podcast"
    TRANSLATE = "translate"


"""
struct TranslateConfig {
    1: optional string From (go.tag = "json:\"from\"") // 翻译源语言
    2: optional string To (go.tag = "json:\"to\"") // 翻译目标语言
}
"""


class TranslateConfig(CozeModel):
    from_: Optional[str] = Field(alias="from")
    to: Optional[str]


class RoomConfig(CozeModel):
    # The audio config of the room.
    audio_config: Optional[RoomAudioConfig]
    # The video config of the room.
    video_config: Optional[RoomVideoConfig]
    # 自定义开场白
    prologue_content: Optional[str]
    # 房间模式
    room_mode: Optional[RoomMode]
    # 同传配置，仅在房间模式为同传时生效
    translate_config: Optional[TranslateConfig]
    # 在进房后等待多长时间播放开场白，默认是500ms，[0, 5000]
    prologue_delay_duration_ms: Optional[int]


class CreateRoomResp(CozeModel):
    # Token to join the room
    token: str
    # The id of user
    uid: str
    # The id of room
    room_id: str
    # App id to join the room
    app_id: str


class RoomsClient(object):
    """
    Room service client.
    """

    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    def create(
        self,
        *,
        bot_id: str,
        voice_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        uid: Optional[str] = None,
        workflow_id: Optional[str] = None,
        config: Optional[RoomConfig] = None,
        **kwargs,
    ) -> CreateRoomResp:
        """
        创建房间

        创建房间，并将智能体加入房间。 接口描述 扣子智能语音功能通过 RTC 技术实现用户和智能体的实时语音通话。在 RTC 领域中，房间是一个虚拟的概念，类似逻辑上的分组，同一个房间内的用户才能互相接收和交换音视频数据、实现音视频通话。 此 API 用于创建一个房间，并将智能体加入房间，然后才能调用 RTC SDK 和智能体开始语音通话。 调用创建房间 API 之后，智能体随即加入房间并开始计费，包括智能体的 对话式 Al-音频费用 和 语音通话费用 ，具体费用详情请参考 音视频费用 。 为避免不必要的费用产生，请在调用接口前仔细了解费用详情，并合理控制创建房间接口的调用频率。 用户未加入房间与智能体进行对话时，智能体会在房间等待用户 3 分钟，这期间会产生 3 分钟的最低费用。

        :param bot_id: 必选参数，Bot id
        :param voice_id: 可选参数，音色 id，不传默认为 xxxy音色
        :param conversation_id: 可选参数， conversation_id，不传会默认创建一个，见【创建会话】接口
        :param uid: 可选参数，标识当前与智能体的用户，由使用方自行定义、生成与维护。uid 用于标识对话中的不同用户，不同的 uid，其对话的数据库等对话记忆数据互相隔离。如果不需要用户数据隔离，可以不传此参数。
        :param config: 可选参数，room 的配置
        """
        url = f"{self._base_url}/v1/audio/rooms"
        headers: Optional[dict] = kwargs.get("headers")
        body = remove_none_values(
            {
                "bot_id": bot_id,
                "voice_id": voice_id,
                "conversation_id": conversation_id,
                "uid": uid,
                "workflow_id": workflow_id,
                "config": config.model_dump() if config else None,
            }
        )
        return self._requester.request("post", url, stream=False, cast=CreateRoomResp, headers=headers, body=body)


class AsyncRoomsClient(object):
    """
    Room service async client.
    """

    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    async def create(
        self,
        *,
        bot_id: str,
        voice_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        uid: Optional[str] = None,
        workflow_id: Optional[str] = None,
        config: Optional[RoomConfig] = None,
        **kwargs,
    ) -> CreateRoomResp:
        """
        创建房间

        创建房间，并将智能体加入房间。 接口描述 扣子智能语音功能通过 RTC 技术实现用户和智能体的实时语音通话。在 RTC 领域中，房间是一个虚拟的概念，类似逻辑上的分组，同一个房间内的用户才能互相接收和交换音视频数据、实现音视频通话。 此 API 用于创建一个房间，并将智能体加入房间，然后才能调用 RTC SDK 和智能体开始语音通话。 调用创建房间 API 之后，智能体随即加入房间并开始计费，包括智能体的 对话式 Al-音频费用 和 语音通话费用 ，具体费用详情请参考 音视频费用 。 为避免不必要的费用产生，请在调用接口前仔细了解费用详情，并合理控制创建房间接口的调用频率。 用户未加入房间与智能体进行对话时，智能体会在房间等待用户 3 分钟，这期间会产生 3 分钟的最低费用。

        :param bot_id: 必选参数，Bot id
        :param voice_id: 可选参数，音色 id，不传默认为 xxxy音色
        :param conversation_id: 可选参数， conversation_id，不传会默认创建一个，见【创建会话】接口
        :param uid: 可选参数，标识当前与智能体的用户，由使用方自行定义、生成与维护。uid 用于标识对话中的不同用户，不同的 uid，其对话的数据库等对话记忆数据互相隔离。如果不需要用户数据隔离，可以不传此参数。
        :param config: 可选参数，room 的配置
        """
        url = f"{self._base_url}/v1/audio/rooms"
        headers: Optional[dict] = kwargs.get("headers")
        body = remove_none_values(
            {
                "bot_id": bot_id,
                "voice_id": voice_id,
                "conversation_id": conversation_id,
                "uid": uid,
                "workflow_id": workflow_id,
                "config": config.model_dump() if config else None,
            }
        )
        return await self._requester.arequest(
            "post", url, stream=False, cast=CreateRoomResp, headers=headers, body=body
        )
