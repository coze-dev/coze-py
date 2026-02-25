from typing import List, Optional

from cozepy import AudioFormat
from cozepy.files import FileTypes, _try_fix_file
from cozepy.model import AsyncNumberPaged, CozeModel, DynamicStrEnum, HTTPRequest, NumberPaged, NumberPagedResponse
from cozepy.request import Requester
from cozepy.util import remove_none_values, remove_url_trailing_slash


class VoiceState(DynamicStrEnum):
    INIT = "init"  # 初始化
    CLONED = "cloned"  # 已克隆
    ALL = "all"  # 所有, 只有查询的时候有效


class VoiceModelType(DynamicStrEnum):
    BIG = "big"  # 大模型音色
    SMALL = "small"  # 小模型音色


class VoiceEmotionInfoInterval(CozeModel):
    default: Optional[float] = None
    max: Optional[float] = None
    min: Optional[float] = None


class VoiceEmotionInfo(CozeModel):
    display_name: Optional[str] = None
    emotion: Optional[str] = None
    emotion_scale_interval: Optional[VoiceEmotionInfoInterval] = None


class Voice(CozeModel):
    # 唯一音色代号
    voice_id: str
    # 音色名
    name: str
    # 是否系统音色
    is_system_voice: bool
    # 语言代号
    language_code: str
    # 语言名
    language_name: str
    # 音色预览文本
    preview_text: str
    # 音色预览音频
    preview_audio: str
    # 剩余训练次数
    available_training_times: int
    # 创建时间unix时间戳
    create_time: int
    # 更新时间unix时间戳
    update_time: int
    # 模型类型
    model_type: VoiceModelType
    # Voice state
    state: VoiceState
    # 支持的情感列表
    support_emotions: Optional[List[VoiceEmotionInfo]] = None


class _PrivateListVoiceData(CozeModel, NumberPagedResponse[Voice]):
    voice_list: List[Voice]
    has_more: bool

    def get_total(self) -> Optional[int]:
        return None

    def get_has_more(self) -> Optional[bool]:
        return self.has_more

    def get_items(self) -> List[Voice]:
        return self.voice_list


class VoicesClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    def clone(
        self,
        *,
        voice_name: str,
        audio_format: AudioFormat,
        language: Optional[str] = None,
        voice_id: Optional[str] = None,
        preview_text: Optional[str] = None,
        text: Optional[str] = None,
        space_id: Optional[str] = None,
        description: Optional[str] = None,
        file: FileTypes,
        **kwargs,
    ) -> Voice:
        """
        复刻音色

        音频时长 复刻指定音频文件中人声的音色。 接口说明 和扣子智能体进行实时的智能语音通话时，你可以选择智能体使用的音色，支持使用扣子编程提供系统内置音色，或通过 复刻音色 API 复刻出的自定义音色。 此 API 用于上传音频文件复刻一个新的音色。调用此 API 时需要上传一个音频文件作为音色复刻的素材。扣子编程会自动复刻音频文件中的人声音色，并将音色保存在当前账号的音色列表中。复刻出的音色可以用于合成语音，或者在扣子编程实时通话中作为智能体的音色。 音色复刻素材要求 上传的音频文件素材应符合以下要求： 类别 文件格式 建议 10s~30s。 支持中文、英文、日语、西班牙语、印度尼西亚语葡萄牙语。 文件录制 仅扣子企业版（企业标准版、企业旗舰版）用户可以使用音色复刻功能。 企业版订阅套餐中默认赠送了一个复刻音色，如需调用复刻音色 OpenAPI 复刻更多音色，请联系超级管理员或管理员购买音色复刻扩容包，具体步骤请参见 购买音色复刻扩容包 。  音色复刻涉及 音色数量费用 和 音色模型存储数费用 ，详细的费用信息可参考 音视频费用 。 调用此 API 之前请确认账户中资源点或余额充足，以免账号欠费导致服务中断 。 最大不超过 10MB。每次最多上传1个音频文件。 语种 文件大小 录制环境：选择安静的空间，建议将麦克风放置在离说话人50厘米以内的位置，尽量保持自然的发声状态，避免刻意改变声线或呢喃，这样得到的音色会更加自然。 音频质量：确保录音中只包含一个人的声音，说话人应保持清晰的发音和音质、稳定的音量和语速，保持姿态稳定。 录制内容：避免说话时韵律过于平淡，尽量让语调、节奏和强度有所变化，尽量不要尝试复刻小孩或老人的声音。 在工作空间中复刻的音色资源仅限于该工作空间的成员使用。即使在同一个企业中，不同工作空间复刻的音色资源是独立的，不允许跨空间使用。 同一个音色 ID 最多复刻 10 次。为节省音色成本，你可以调用此接口训练自己已复刻的音色，即录制一个新的音频文件重新复刻音色，训练后的音色会覆盖原音色，但音色 ID 不变。例如，购买一个音色后，你可以对这个音色重新免费复刻 9 次。 必须使用 multipart/form-data 方式上传音频文件。 说明 wav、mp3、ogg、m4a、aac、pcm。其中 pcm 仅支持 24k 采样率，单通道。

        :param voice_name: 音色名
        :param audio_format: 传入文件的音频格式，例如 pcm, m4a, mp3
        :param voice_id: 如果有，则使用此 voice_id 进行训练覆盖，否则使用新的 voice_id 进行训练
        :param preview_text: 如果传入会基于该文本生成预览音频，否则使用默认的文本"你好，我是你的专属AI克隆声音，希望未来可以一起好好相处哦"
        :param text: 可以让用户按照该文本念诵，服务会对比音频与该文本的差异。若差异过大会返回1109 WERError
        :param space_id: 克隆音色保存的空间，默认在个人空间
        """
        url = f"{self._base_url}/v1/audio/voices/clone"
        headers: Optional[dict] = kwargs.get("headers")
        body = remove_none_values(
            {
                "voice_name": voice_name,
                "audio_format": audio_format,
                "language": language,
                "voice_id": voice_id,
                "preview_text": preview_text,
                "text": text,
                "space_id": space_id,
                "description": description,
            }
        )
        files = {"file": _try_fix_file(file)}

        return self._requester.request("post", url, False, cast=Voice, headers=headers, body=body, files=files)

    def list(
        self,
        *,
        filter_system_voice: bool = False,
        voice_state: Optional[VoiceState] = None,
        model_type: Optional[VoiceModelType] = None,
        page_num: int = 1,
        page_size: int = 100,
        **kwargs,
    ) -> NumberPaged[Voice]:
        """
        查看音色列表

        查看可用的音色列表，包括系统预置音色和自定义音色。 接口说明 调用此 API 可查看当前扣子用户可使用的音色列表，包括： 系统预置音色：扣子平台提供的默认音色。 自定义音色：当前扣子用户通过 复刻音色 API 复刻的音色、当前账号加入的所有工作空间中其他扣子用户复刻的音色。

        :param filter_system_voice: 查看音色列表时是否过滤掉系统音色。 * true：过滤系统音色 * false：（默认）不过滤系统音色
        :param model_type: 音色模型的类型，如果不填，默认都返回。可选值包括： * big：大模型 * small：小模型
        :param page_num: 查询结果分页展示时，此参数用于设置查看的页码。最小值为 1，默认为 1。
        :param page_size: 查询结果分页展示时，此参数用于设置每页返回的数据量。取值范围为 1~100，默认为 100。
        :param voice_state: 音色克隆状态，用于筛选特定状态的音色。可选值包括： * init：待克隆。 * cloned：（默认值）已克隆。 * all：全部。
        """
        url = f"{self._base_url}/v1/audio/voices"
        headers: Optional[dict] = kwargs.get("headers")

        def request_maker(i_page_num: int, i_page_size: int) -> HTTPRequest:
            return self._requester.make_request(
                "GET",
                url,
                headers=headers,
                params=remove_none_values(
                    {
                        "filter_system_voice": filter_system_voice,
                        "voice_state": voice_state.value if voice_state else None,
                        "model_type": model_type.value if model_type else None,
                        "page_num": i_page_num,
                        "page_size": i_page_size,
                    }
                ),
                cast=_PrivateListVoiceData,
                stream=False,
            )

        return NumberPaged(
            page_num=page_num,
            page_size=page_size,
            requestor=self._requester,
            request_maker=request_maker,
        )


class AsyncVoicesClient(object):
    def __init__(self, base_url: str, requester: Requester):
        self._base_url = remove_url_trailing_slash(base_url)
        self._requester = requester

    async def clone(
        self,
        *,
        voice_name: str,
        audio_format: AudioFormat,
        language: Optional[str] = None,
        voice_id: Optional[str] = None,
        preview_text: Optional[str] = None,
        text: Optional[str] = None,
        space_id: Optional[str] = None,
        description: Optional[str] = None,
        file: FileTypes,
        **kwargs,
    ) -> Voice:
        """
        复刻音色

        在工作空间中复刻的音色资源仅限于该工作空间的成员使用。即使在同一个企业中，不同工作空间复刻的音色资源是独立的，不允许跨空间使用。 同一个音色 ID 最多复刻 10 次。为节省音色成本，你可以调用此接口训练自己已复刻的音色，即录制一个新的音频文件重新复刻音色，训练后的音色会覆盖原音色，但音色 ID 不变。例如，购买一个音色后，你可以对这个音色重新免费复刻 9 次。 必须使用 multipart/form-data 方式上传音频文件。 文件格式 wav、mp3、ogg、m4a、aac、pcm。其中 pcm 仅支持 24k 采样率，单通道。 最大不超过 10MB。每次最多上传1个音频文件。 音频时长 支持中文、英文、日语、西班牙语、印度尼西亚语葡萄牙语。 复刻指定音频文件中人声的音色。 接口说明 和扣子智能体进行实时的智能语音通话时，你可以选择智能体使用的音色，支持使用扣子编程提供系统内置音色，或通过 复刻音色 API 复刻出的自定义音色。 此 API 用于上传音频文件复刻一个新的音色。调用此 API 时需要上传一个音频文件作为音色复刻的素材。扣子编程会自动复刻音频文件中的人声音色，并将音色保存在当前账号的音色列表中。复刻出的音色可以用于合成语音，或者在扣子编程实时通话中作为智能体的音色。 音色复刻素材要求 上传的音频文件素材应符合以下要求： 建议 10s~30s。 语种 文件大小 文件录制 录制环境：选择安静的空间，建议将麦克风放置在离说话人50厘米以内的位置，尽量保持自然的发声状态，避免刻意改变声线或呢喃，这样得到的音色会更加自然。 音频质量：确保录音中只包含一个人的声音，说话人应保持清晰的发音和音质、稳定的音量和语速，保持姿态稳定。 录制内容：避免说话时韵律过于平淡，尽量让语调、节奏和强度有所变化，尽量不要尝试复刻小孩或老人的声音。 仅扣子企业版（企业标准版、企业旗舰版）用户可以使用音色复刻功能。 企业版订阅套餐中默认赠送了一个复刻音色，如需调用复刻音色 OpenAPI 复刻更多音色，请联系超级管理员或管理员购买音色复刻扩容包，具体步骤请参见 购买音色复刻扩容包 。  音色复刻涉及 音色数量费用 和 音色模型存储数费用 ，详细的费用信息可参考 音视频费用 。 调用此 API 之前请确认账户中资源点或余额充足，以免账号欠费导致服务中断 。 类别 说明

        :param voice_name: 音色名
        :param audio_format: 传入文件的音频格式，例如 pcm, m4a, mp3
        :param voice_id: 如果有，则使用此 voice_id 进行训练覆盖，否则使用新的 voice_id 进行训练
        :param preview_text: 如果传入会基于该文本生成预览音频，否则使用默认的文本"你好，我是你的专属AI克隆声音，希望未来可以一起好好相处哦"
        :param text: 可以让用户按照该文本念诵，服务会对比音频与该文本的差异。若差异过大会返回1109 WERError
        :param space_id: 克隆音色保存的空间，默认在个人空间
        """
        url = f"{self._base_url}/v1/audio/voices/clone"
        headers: Optional[dict] = kwargs.get("headers")
        body = remove_none_values(
            {
                "voice_name": voice_name,
                "audio_format": audio_format,
                "language": language,
                "voice_id": voice_id,
                "preview_text": preview_text,
                "text": text,
                "space_id": space_id,
                "description": description,
            }
        )
        files = {"file": _try_fix_file(file)}

        return await self._requester.arequest("post", url, False, cast=Voice, headers=headers, body=body, files=files)

    async def list(
        self,
        *,
        filter_system_voice: bool = False,
        voice_state: Optional[VoiceState] = None,
        model_type: Optional[VoiceModelType] = None,
        page_num: int = 1,
        page_size: int = 100,
        **kwargs,
    ) -> AsyncNumberPaged[Voice]:
        """
        查看音色列表

        查看可用的音色列表，包括系统预置音色和自定义音色。 接口说明 调用此 API 可查看当前扣子用户可使用的音色列表，包括： 系统预置音色：扣子平台提供的默认音色。 自定义音色：当前扣子用户通过 复刻音色 API 复刻的音色、当前账号加入的所有工作空间中其他扣子用户复刻的音色。

        :param filter_system_voice: 查看音色列表时是否过滤掉系统音色。 * true：过滤系统音色 * false：（默认）不过滤系统音色
        :param model_type: 音色模型的类型，如果不填，默认都返回。可选值包括： * big：大模型 * small：小模型
        :param page_num: 查询结果分页展示时，此参数用于设置查看的页码。最小值为 1，默认为 1。
        :param page_size: 查询结果分页展示时，此参数用于设置每页返回的数据量。取值范围为 1~100，默认为 100。
        :param voice_state: 音色克隆状态，用于筛选特定状态的音色。可选值包括： * init：待克隆。 * cloned：（默认值）已克隆。 * all：全部。
        """
        url = f"{self._base_url}/v1/audio/voices"
        headers: Optional[dict] = kwargs.get("headers")

        async def request_maker(i_page_num: int, i_page_size: int) -> HTTPRequest:
            return await self._requester.amake_request(
                "GET",
                url,
                headers=headers,
                params=remove_none_values(
                    {
                        "filter_system_voice": filter_system_voice,
                        "voice_state": voice_state.value if voice_state else None,
                        "model_type": model_type.value if model_type else None,
                        "page_num": i_page_num,
                        "page_size": i_page_size,
                    }
                ),
                cast=_PrivateListVoiceData,
                stream=False,
            )

        return await AsyncNumberPaged.build(
            page_num=page_num,
            page_size=page_size,
            requestor=self._requester,
            request_maker=request_maker,
        )
