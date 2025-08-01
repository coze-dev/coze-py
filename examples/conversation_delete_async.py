"""
异步删除对话示例

本示例演示如何使用Coze SDK异步删除指定的对话。
删除对话后，对话及其中的所有消息都将被永久删除，无法恢复。
"""

import asyncio
import os

from cozepy import AsyncCoze, TokenAuth

# 设置访问令牌和基础URL
COZE_API_TOKEN = os.getenv("COZE_API_TOKEN") or "your_access_token"
COZE_API_BASE = os.getenv("COZE_API_BASE") or "https://api.coze.cn"


async def main():
    # 初始化异步Coze客户端
    client = AsyncCoze(auth=TokenAuth(COZE_API_TOKEN), base_url=COZE_API_BASE)

    # 要删除的对话ID
    conversation_id = "your_conversation_id"

    try:
        # 异步删除对话
        success = await client.conversations.delete(conversation_id=conversation_id)

        if success:
            print(f"成功删除对话: {conversation_id}")
        else:
            print("删除对话失败")

    except Exception as e:
        print(f"删除对话时发生错误: {e}")


if __name__ == "__main__":
    asyncio.run(main())
