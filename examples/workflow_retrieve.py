"""
获取工作流信息示例

本示例演示如何使用cozepy获取指定工作流的详细信息。
"""

import asyncio
import os

from cozepy import Coze, TokenAuth

# 设置环境变量
COZE_API_TOKEN = os.environ.get("COZE_API_TOKEN")
if not COZE_API_TOKEN:
    print("请先设置环境变量 COZE_API_TOKEN")
    exit(1)


# 同步示例
async def sync_example():
    """同步方式获取工作流信息"""
    # 初始化客户端
    coze = Coze(auth=TokenAuth(COZE_API_TOKEN))

    # 工作流ID（请替换为实际的工作流ID）
    workflow_id = "your_workflow_id_here"

    try:
        # 获取工作流信息
        workflow_info = coze.workflows.retrieve(workflow_id=workflow_id)

        # 打印工作流详细信息
        print("=== 工作流详细信息 ===")
        print(f"工作流ID: {workflow_info.workflow_detail.workflow_id}")
        print(f"工作流名称: {workflow_info.workflow_detail.workflow_name}")
        print(f"工作流描述: {workflow_info.workflow_detail.description}")
        print(f"工作流图标URL: {workflow_info.workflow_detail.icon_url}")
        print(f"应用ID: {workflow_info.workflow_detail.app_id}")
        print(f"创建时间: {workflow_info.workflow_detail.created_at}")
        print(f"更新时间: {workflow_info.workflow_detail.updated_at}")
        print(f"创建者ID: {workflow_info.workflow_detail.creator.id}")
        print(f"创建者名称: {workflow_info.workflow_detail.creator.name}")

    except Exception as e:
        print(f"获取工作流信息失败: {e}")


# 异步示例
async def async_example():
    """异步方式获取工作流信息"""
    # 初始化异步客户端
    coze = Coze(auth=TokenAuth(COZE_API_TOKEN))

    # 工作流ID（请替换为实际的工作流ID）
    workflow_id = "your_workflow_id_here"

    try:
        # 获取工作流信息
        workflow_info = await coze.workflows.retrieve(workflow_id=workflow_id)

        # 打印工作流详细信息
        print("=== 异步获取工作流详细信息 ===")
        print(f"工作流ID: {workflow_info.workflow_detail.workflow_id}")
        print(f"工作流名称: {workflow_info.workflow_detail.workflow_name}")
        print(f"工作流描述: {workflow_info.workflow_detail.description}")
        print(f"工作流图标URL: {workflow_info.workflow_detail.icon_url}")
        print(f"应用ID: {workflow_info.workflow_detail.app_id}")
        print(f"创建时间: {workflow_info.workflow_detail.created_at}")
        print(f"更新时间: {workflow_info.workflow_detail.updated_at}")
        print(f"创建者ID: {workflow_info.workflow_detail.creator.id}")
        print(f"创建者名称: {workflow_info.workflow_detail.creator.name}")

    except Exception as e:
        print(f"异步获取工作流信息失败: {e}")


# 批量获取工作流信息
async def batch_example():
    """批量获取工作流信息示例"""
    coze = Coze(auth=TokenAuth(COZE_API_TOKEN))

    # 假设有一组工作流ID
    workflow_ids = ["workflow_1", "workflow_2", "workflow_3"]

    print("=== 批量获取工作流信息 ===")
    for workflow_id in workflow_ids:
        try:
            workflow_info = coze.workflows.retrieve(workflow_id=workflow_id)
            print(f"\n工作流 {workflow_id} 的信息:")
            print(f"  名称: {workflow_info.workflow_detail.workflow_name}")
            print(f"  描述: {workflow_info.workflow_detail.description}")
            print(f"  创建者: {workflow_info.workflow_detail.creator.name}")
        except Exception as e:
            print(f"获取工作流 {workflow_id} 信息失败: {e}")


if __name__ == "__main__":
    # 运行同步示例
    asyncio.run(sync_example())

    # 运行异步示例
    asyncio.run(async_example())

    # 运行批量示例
    asyncio.run(batch_example())
