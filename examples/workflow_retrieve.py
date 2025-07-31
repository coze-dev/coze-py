#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
获取工作流详细信息示例

本示例演示如何使用Coze SDK获取指定工作流的详细信息。
"""

import os

from cozepy import Coze, TokenAuth

# 初始化客户端
# 请确保设置了 COZE_API_TOKEN 环境变量
api_token = os.getenv("COZE_API_TOKEN")
if not api_token:
    raise ValueError("请设置 COZE_API_TOKEN 环境变量")

# 创建认证对象
auth = TokenAuth(token=api_token)

# 创建Coze客户端
# 国内环境使用 COZE_CN_BASE_URL
# 国际环境使用 COZE_COM_BASE_URL
coze = Coze(auth=auth, base_url="https://api.coze.cn")


# 示例：获取工作流详细信息
def get_workflow_info_example():
    """
    获取工作流详细信息示例
    """
    # 请替换为实际的工作流ID
    workflow_id = "your_workflow_id_here"

    try:
        # 获取工作流详细信息
        workflow_info = coze.workflows.retrieve(workflow_id=workflow_id)

        # 打印工作流信息
        print("工作流详细信息:")
        print(f"工作流ID: {workflow_info.workflow_id}")
        print(f"工作流名称: {workflow_info.workflow_name}")
        print(f"工作流描述: {workflow_info.description}")
        print(f"工作流图标: {workflow_info.icon_url}")
        print(f"应用ID: {workflow_info.app_id}")
        print(f"工作流模式: {workflow_info.workflow_mode}")
        print(f"创建时间: {workflow_info.created_at}")
        print(f"更新时间: {workflow_info.updated_at}")
        print(f"版本号: {workflow_info.version}")
        print(f"发布状态: {workflow_info.publish_status}")

    except Exception as e:
        print(f"获取工作流信息失败: {e}")


# 示例：异步获取工作流详细信息
async def async_get_workflow_info_example():
    """
    异步获取工作流详细信息示例
    """
    # 请替换为实际的工作流ID
    workflow_id = "your_workflow_id_here"

    try:
        # 获取工作流详细信息
        workflow_info = await coze.workflows.retrieve(workflow_id=workflow_id)

        # 打印工作流信息
        print("异步获取工作流详细信息:")
        print(f"工作流ID: {workflow_info.workflow_id}")
        print(f"工作流名称: {workflow_info.workflow_name}")
        print(f"工作流描述: {workflow_info.description}")
        print(f"工作流图标: {workflow_info.icon_url}")
        print(f"应用ID: {workflow_info.app_id}")
        print(f"工作流模式: {workflow_info.workflow_mode}")
        print(f"创建时间: {workflow_info.created_at}")
        print(f"更新时间: {workflow_info.updated_at}")
        print(f"版本号: {workflow_info.version}")
        print(f"发布状态: {workflow_info.publish_status}")

    except Exception as e:
        print(f"异步获取工作流信息失败: {e}")


if __name__ == "__main__":
    # 运行同步示例
    get_workflow_info_example()

    # 运行异步示例
    import asyncio

    asyncio.run(async_get_workflow_info_example())
