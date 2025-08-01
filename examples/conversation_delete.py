"""
删除对话示例

本示例演示如何使用Coze SDK删除指定的对话。
删除对话后，对话及其中的所有消息都将被永久删除，无法恢复。
"""

import os

from cozepy import Coze, TokenAuth

# 设置访问令牌和基础URL
COZE_API_TOKEN = os.getenv("COZE_API_TOKEN") or "your_access_token"
COZE_API_BASE = os.getenv("COZE_API_BASE") or "https://api.coze.cn"

# 初始化Coze客户端
client = Coze(auth=TokenAuth(COZE_API_TOKEN), base_url=COZE_API_BASE)

# 要删除的对话ID
conversation_id = "your_conversation_id"

try:
    # 删除对话
    success = client.conversations.delete(conversation_id=conversation_id)

    if success:
        print(f"成功删除对话: {conversation_id}")
    else:
        print("删除对话失败")

except Exception as e:
    print(f"删除对话时发生错误: {e}")
