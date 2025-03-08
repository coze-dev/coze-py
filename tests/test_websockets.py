import pytest

from cozepy import (
    AsyncWebsocketsAudioSpeechEventHandler,
    AsyncWebsocketsAudioTranscriptionsEventHandler,
    AsyncWebsocketsChatEventHandler,
    WebsocketsAudioSpeechEventHandler,
    WebsocketsAudioTranscriptionsEventHandler,
    WebsocketsChatEventHandler,
)


@pytest.mark.respx(base_url="https://api.coze.com")
class TestSyncWebsocketsHandler:
    def test_sync_rooms_create(self, respx_mock):
        # init handlers
        speech = WebsocketsAudioSpeechEventHandler()
        transcriptions = WebsocketsAudioTranscriptionsEventHandler()
        chat = WebsocketsChatEventHandler()

        # call event_handlers
        speech_handlers = speech.event_handlers()
        transcriptions_handlers = transcriptions.event_handlers()
        chat_handlers = chat.event_handlers()

        # call twice
        speech_handlers_2 = speech.event_handlers()
        transcriptions_handlers_2 = transcriptions.event_handlers()
        chat_handlers_2 = chat.event_handlers()

        # assert that they are the same
        assert speech_handlers == speech_handlers_2
        assert transcriptions_handlers == transcriptions_handlers_2
        assert chat_handlers == chat_handlers_2

        # assert that they are not the same
        assert speech_handlers != transcriptions_handlers
        assert speech_handlers != chat_handlers
        assert speech_handlers != transcriptions_handlers_2
        assert speech_handlers != chat_handlers_2

        assert transcriptions_handlers != chat_handlers
        assert transcriptions_handlers != chat_handlers_2


@pytest.mark.respx(base_url="https://api.coze.com")
class TestAsyncWebsocketsHandler:
    def test_sync_rooms_create(self, respx_mock):
        # init handlers
        speech = AsyncWebsocketsAudioSpeechEventHandler()
        transcriptions = AsyncWebsocketsAudioTranscriptionsEventHandler()
        chat = AsyncWebsocketsChatEventHandler()

        # call event_handlers
        speech_handlers = speech.event_handlers()
        transcriptions_handlers = transcriptions.event_handlers()
        chat_handlers = chat.event_handlers()

        # call twice
        speech_handlers_2 = speech.event_handlers()
        transcriptions_handlers_2 = transcriptions.event_handlers()
        chat_handlers_2 = chat.event_handlers()

        # assert that they are the same
        assert speech_handlers == speech_handlers_2
        assert transcriptions_handlers == transcriptions_handlers_2
        assert chat_handlers == chat_handlers_2

        # assert that they are not the same
        assert speech_handlers != transcriptions_handlers
        assert speech_handlers != chat_handlers
        assert speech_handlers != transcriptions_handlers_2
        assert speech_handlers != chat_handlers_2

        assert transcriptions_handlers != chat_handlers
        assert transcriptions_handlers != chat_handlers_2
