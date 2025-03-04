import asyncio
import json
import logging
import os
import queue
import threading
import time
import tkinter as tk
from tkinter import scrolledtext, ttk
from typing import Optional

import pyaudio

from cozepy import (
    COZE_CN_BASE_URL,
    AsyncCoze,
    AsyncWebsocketsChatClient,
    AsyncWebsocketsChatEventHandler,
    ChatUpdateEvent,
    ConversationAudioDeltaEvent,
    ConversationChatCompletedEvent,
    ConversationChatCanceledEvent,
    InputAudio,
    InputAudioBufferAppendEvent,
    TokenAuth,
    setup_logging,
)

# 音频参数设置
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 24000
INPUT_BLOCK_TIME = 0.05  # 50ms per block


def setup_examples_logger():
    coze_log = os.getenv("COZE_LOG")
    if coze_log:
        setup_logging(logging.getLevelNamesMapping().get(coze_log.upper(), logging.INFO))


setup_examples_logger()


class ModernAudioChatGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("智能语音助手")
        self.root.geometry("600x800")  # 设置窗口大小

        # 设置主题样式
        style = ttk.Style()
        style.configure("Custom.TButton", padding=10, font=("Helvetica", 12))
        style.configure("Custom.TLabel", font=("Helvetica", 11))

        # 初始化PyAudio
        self.p = pyaudio.PyAudio()
        self.recording = False
        self.stream: Optional[pyaudio.Stream] = None
        self.audio_queue = queue.Queue()

        # 添加音频播放队列
        self.playback_queue = queue.Queue()
        self.is_playing = False
        self.playback_stream = None

        # 创建GUI组件
        self.setup_gui()

        # 初始化Coze客户端
        self.coze = AsyncCoze(
            auth=TokenAuth(os.getenv("COZE_API_TOKEN")),
            base_url=os.getenv("COZE_API_BASE", COZE_CN_BASE_URL),
        )

        # 创建事件循环
        self.loop = asyncio.new_event_loop()
        self.chat_client: Optional[AsyncWebsocketsChatClient] = None

        # 启动异步事件循环
        threading.Thread(target=self.run_async_loop, daemon=True).start()

        # 添加窗口关闭处理
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # 启动播放线程
        threading.Thread(target=self.playback_loop, daemon=True).start()

    def setup_gui(self):
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # 创建聊天记录显示区域
        self.chat_frame = ttk.Frame(self.main_frame)
        self.chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        self.chat_display = scrolledtext.ScrolledText(
            self.chat_frame, wrap=tk.WORD, height=20, font=("Helvetica", 11), bg="#f5f5f5"
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)

        # 状态显示区域
        self.status_frame = ttk.Frame(self.main_frame)
        self.status_frame.pack(fill=tk.X, pady=(0, 20))

        self.status_label = ttk.Label(self.status_frame, text="准备就绪", style="Custom.TLabel")
        self.status_label.pack()

        # 音量指示器
        self.volume_bar = ttk.Progressbar(self.status_frame, mode="determinate", length=200)
        self.volume_bar.pack(pady=10)

        # 按钮控制区域
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(fill=tk.X)

        # 开启通话按钮
        self.start_button = ttk.Button(
            self.button_frame, text="开启通话", command=self.start_chat, style="Custom.TButton"
        )
        self.start_button.pack(side=tk.LEFT, padx=5)

        # 发送数据按钮
        self.send_button = ttk.Button(
            self.button_frame, text="发送", command=self.send_audio, state=tk.DISABLED, style="Custom.TButton"
        )
        self.send_button.pack(side=tk.LEFT, padx=5)

        # 结束按钮
        self.end_button = ttk.Button(
            self.button_frame, text="结束", command=self.end_chat, state=tk.DISABLED, style="Custom.TButton"
        )
        self.end_button.pack(side=tk.LEFT, padx=5)

    def update_chat_display(self, message: str, is_user: bool = True):
        self.chat_display.insert(tk.END, f"{'你' if is_user else 'AI'}: {message}\n")
        self.chat_display.see(tk.END)  # 自动滚动到底部

    def start_chat(self):
        self.start_button.config(state=tk.DISABLED)
        self.send_button.config(state=tk.NORMAL)
        self.end_button.config(state=tk.NORMAL)

        # 开始录音
        self.start_recording()
        self.status_label.config(text="正在录音...")
        self.update_chat_display("开始新的对话", is_user=False)

    def end_chat(self):
        # 停止录音
        if self.recording:
            self.stop_recording()

        # 关闭WebSocket连接
        self.loop.call_soon_threadsafe(self.close_connection)

        # 重置UI
        self.start_button.config(state=tk.NORMAL)
        self.send_button.config(state=tk.DISABLED)
        self.end_button.config(state=tk.DISABLED)
        self.status_label.config(text="准备就绪")
        self.update_chat_display("对话已结束", is_user=False)

    def close_connection(self):
        async def close():
            if self.chat_client:
                await self.chat_client.close()
                self.chat_client = None

        asyncio.run_coroutine_threadsafe(close(), self.loop)

    def start_recording(self):
        try:
            self.recording = True

            # 计算输入缓冲区大小
            input_frames_per_block = int(RATE * INPUT_BLOCK_TIME)

            # 打开音频流
            self.stream = self.p.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=input_frames_per_block,
                stream_callback=self.audio_callback,
            )

            # 启动WebSocket连接
            self.loop.call_soon_threadsafe(self.start_websocket_connection)

        except Exception as e:
            print(f"启动录音错误: {e}")
            self.recording = False
            self.status_label.config(text="启动录音失败")
            self.start_button.config(state=tk.NORMAL)
            self.send_button.config(state=tk.DISABLED)
            self.end_button.config(state=tk.DISABLED)

    def audio_callback(self, in_data, frame_count, time_info, status):
        if self.recording:
            try:
                self.audio_queue.put(in_data)

                # 更新音量指示器
                amplitude = max(
                    abs(int.from_bytes(in_data[i : i + 2], "little", signed=True)) for i in range(0, len(in_data), 2)
                )
                volume = min(100, int(amplitude / 32768 * 100))
                self.root.after(0, lambda v=volume: self.volume_bar.configure(value=v))

            except Exception as e:
                print(f"录音回调错误: {e}")

        return (None, pyaudio.paContinue)

    def stop_recording(self):
        try:
            self.recording = False
            if self.stream is not None and self.stream.is_active():
                self.stream.stop_stream()
                self.stream.close()
            self.stream = None
        except Exception as e:
            print(f"停止录音错误: {e}")
        finally:
            self.stream = None

    def on_closing(self):
        # 停止录音
        self.stop_recording()

        # 停止播放
        self.is_playing = False
        if self.playback_stream:
            self.playback_stream.stop_stream()
            self.playback_stream.close()

        # 关闭WebSocket连接
        if self.chat_client:
            self.loop.call_soon_threadsafe(self.close_connection)

        # 关闭PyAudio
        if self.p:
            self.p.terminate()

        # 关闭窗口
        self.root.destroy()

    def run_async_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def start_websocket_connection(self):
        async def start():
            class ChatEventHandler(AsyncWebsocketsChatEventHandler):
                def __init__(self, gui):
                    self.gui = gui
                    self.is_first_audio = True
                    self.temp_file = open("temp_response.pcm", "wb")

                async def on_conversation_audio_delta(
                    self, cli: AsyncWebsocketsChatClient, event: ConversationAudioDeltaEvent
                ):
                    try:
                        audio_data = event.data.get_audio()
                        if audio_data:
                            # 写入临时文件
                            self.temp_file.write(audio_data)
                            self.temp_file.flush()

                            # 如果是第一块音频数据，开始播放
                            if self.is_first_audio:
                                self.is_first_audio = False
                                self.gui.start_streaming_playback()

                            # 将音频数据放入播放队列
                            self.gui.playback_queue.put(audio_data)
                    except Exception as e:
                        print(f"处理音频数据错误: {e}")

                async def on_conversation_chat_completed(
                    self, cli: AsyncWebsocketsChatClient, event: ConversationChatCompletedEvent
                ):
                    try:
                        # 关闭临时文件
                        self.temp_file.close()

                        # 标记播放结束
                        self.gui.playback_queue.put(None)

                        # 重新开始录音
                        self.gui.root.after(1000, self.gui.resume_recording)
                    except Exception as e:
                        print(f"完成对话错误: {e}")

                async def on_conversation_chat_canceled(
                    self, cli: AsyncWebsocketsChatClient, event: ConversationChatCanceledEvent
                ):
                    try:
                        print("打断")
                    except Exception as e:
                        print(f"对话打断错误: {e}")

            kwargs = json.loads(os.getenv("COZE_KWARGS") or "{}")
            self.chat_client = self.coze.websockets.chat.create(
                bot_id=os.getenv("COZE_BOT_ID"),
                on_event=ChatEventHandler(self),
                **kwargs,
            )

            async with self.chat_client() as client:
                await client.chat_update(
                    ChatUpdateEvent.Data.model_validate(
                        {
                            "input_audio": InputAudio.model_validate(
                                {
                                    "format": "pcm",
                                    "sample_rate": RATE,
                                    "channel": CHANNELS,
                                    "bit_depth": 16,
                                    "codec": "pcm",
                                }
                            ),
                        }
                    )
                )
                while self.chat_client:
                    if not self.audio_queue.empty():
                        audio_data = self.audio_queue.get()
                        await client.input_audio_buffer_append(
                            InputAudioBufferAppendEvent.Data.model_validate(
                                {
                                    "delta": audio_data,
                                }
                            )
                        )
                    await asyncio.sleep(0.1)

        asyncio.run_coroutine_threadsafe(start(), self.loop)

    def resume_recording(self):
        # 重新开始录音
        self.start_recording()
        self.send_button.config(state=tk.NORMAL)
        self.status_label.config(text="正在录音...")

    def complete_audio(self):
        async def complete():
            while not self.audio_queue.empty():
                await asyncio.sleep(0.1)
            if self.chat_client:
                await self.chat_client.input_audio_buffer_complete()
                await self.chat_client.wait()

        asyncio.run_coroutine_threadsafe(complete(), self.loop)

    def start_streaming_playback(self):
        """开始流式播放"""
        self.status_label.config(text="正在播放回复...")
        self.update_chat_display("正在回复...", is_user=False)
        self.is_playing = True

    def playback_loop(self):
        """音频播放循环"""
        while True:
            try:
                if self.is_playing:
                    # 从队列中获取音频数据
                    audio_data = self.playback_queue.get()

                    # None 表示播放结束
                    if audio_data is None:
                        if self.playback_stream:
                            self.playback_stream.stop_stream()
                            self.playback_stream.close()
                            self.playback_stream = None
                        self.is_playing = False
                        continue

                    # 创建播放流（如果还没有创建）
                    if not self.playback_stream:
                        self.playback_stream = self.p.open(
                            format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK
                        )

                    # 播放音频数据
                    self.playback_stream.write(audio_data)

            except Exception as e:
                print(f"播放错误: {e}")
                self.is_playing = False
                if self.playback_stream:
                    try:
                        self.playback_stream.stop_stream()
                        self.playback_stream.close()
                    except Exception as e:
                        pass
                    self.playback_stream = None

            # 短暂休眠以避免CPU过载
            time.sleep(0.001)

    def send_audio(self):
        # 停止录音
        self.stop_recording()

        # 禁用发送按钮
        self.send_button.config(state=tk.DISABLED)
        self.status_label.config(text="正在发送...")
        self.update_chat_display("发送语音消息", is_user=True)

        # 发送完成事件
        self.loop.call_soon_threadsafe(self.complete_audio)


def main():
    root = tk.Tk()
    ModernAudioChatGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
