import asyncio
import os

from cozepy.auth import AsyncTokenAuth
from cozepy.chat import Message
from cozepy.coze import AsyncCoze


async def main():
    token = os.getenv("COZE_API_TOKEN")
    bot_id = os.getenv("COZE_BOT_ID")
    coze = AsyncCoze(
        auth=AsyncTokenAuth(token=token),
    )

    async for chunk in coze.chat.stream(
        bot_id=bot_id,
        user_id="1",
        additional_messages=[Message.build_user_question_text("chat")],
    ):
        print(chunk)


if __name__ == "__main__":
    asyncio.run(main())
