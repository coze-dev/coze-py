import json
import sys
from typing import Optional

try:
    from unittest.mock import AsyncMock
except ImportError:
    from unittest.mock import MagicMock as AsyncMock  # For Python < 3.8
from unittest.mock import patch

import pytest

from cozepy import (
    AsyncCoze,
    AsyncTokenAuth,
    WebsocketsEvent,
    WebsocketsEventType,
)
from cozepy.websockets import ws as websockets_ws


class MockEventWithNone(WebsocketsEvent):
    event_type: WebsocketsEventType = WebsocketsEventType.CHAT_UPDATE
    id: Optional[str] = "test_id"
    data: Optional[dict] = None  # This is the field with None


@pytest.mark.skipif(sys.version_info < (3, 8), reason="async websocket need python 3.8+")
@pytest.mark.asyncio
async def test_async_send_event_excludes_none_values():
    """
    Tests that _send_event on AsyncWebsocketsBaseClient correctly serializes
    events using model_dump_json(exclude_none=True), so that fields with
    a value of None are not included in the final JSON payload.
    """
    with patch("websockets.asyncio.client.connect"):
        # 1. Setup
        coze = AsyncCoze(auth=AsyncTokenAuth("dummy_token"), base_url="https://dummy.url")
        # We instantiate the client but don't connect, to avoid starting background tasks.
        client = coze.websockets.chat.create(bot_id="dummy_bot_id", on_event={})

        # Manually inject a mock websocket connection
        mock_ws = AsyncMock()
        client._ws = mock_ws

        # 2. Create an event instance where some fields are None
        event_with_none = MockEventWithNone(data=None)
        # Let's add another None field to be sure
        event_with_none.id = None

        # 3. Action
        # Call the internal _send_event method directly for this unit test
        await client._send_event(event_with_none)

        # 4. Assertions
        # Ensure the send method on the mock websocket was called
        mock_ws.send.assert_called_once()

        # Inspect the data that was sent
        sent_payload_str = mock_ws.send.call_args[0][0]
        sent_payload_json = json.loads(sent_payload_str)

        # Verify that keys with None values were excluded from the JSON
        assert "data" not in sent_payload_json
        assert "id" not in sent_payload_json

        # Verify that the key with a non-None value is present
        assert sent_payload_json["event_type"] == "chat.update"


@pytest.mark.skipif(sys.version_info < (3, 8), reason="async websocket need python 3.8+")
@pytest.mark.asyncio
async def test_log_send_event_is_called():
    """
    Tests that _send_event calls the _log_send_event helper.
    """
    with patch.object(websockets_ws, "_log_send_event") as mock_log:
        # 1. Setup
        coze = AsyncCoze(auth=AsyncTokenAuth("dummy_token"), base_url="https://dummy.url")
        client = coze.websockets.chat.create(bot_id="dummy_bot_id", on_event={})
        mock_ws = AsyncMock()
        client._ws = mock_ws
        event = MockEventWithNone()

        # 2. Action
        await client._send_event(event)

        # 3. Assertion
        mock_log.assert_called_once_with(client._path, event)
