import json
import logging
import os
import time
from functools import lru_cache
from typing import Optional, Type, TypeVar

import click
from pydantic import BaseModel
from rich.console import Console
from rich.table import Table

from cozepy import COZE_CN_BASE_URL, Coze, DeviceOAuthApp, OAuthToken, TokenAuth
from cozepy.bots import Bot
from cozepy.log import setup_logging
from cozepy.workspaces import Workspace

BaseT = TypeVar("BaseT", bound=BaseModel)


setup_logging(logging.ERROR)
console = Console()


class FileCache(object):
    def __init__(self, cache_dir: str):
        self._cache_dir = cache_dir
        if not os.path.exists(self._cache_dir):
            os.makedirs(self._cache_dir)

    def get(self, key: str) -> Optional[str]:
        cache_key = os.path.join(self._cache_dir, key)
        if not os.path.exists(cache_key):
            return None
        with open(cache_key, "r") as f:
            return f.read()

    def set(self, key: str, value: str) -> None:
        cache_key = os.path.join(self._cache_dir, key)
        with open(cache_key, "w") as f:
            f.write(value)

    def get_typed(self, key: str, model: Type[BaseT]) -> Optional[BaseT]:
        value = self.get(key)
        if not value:
            return None
        return model.model_validate_json(value)

    def set_typed(self, key: str, value: BaseT) -> None:
        self.set(key, value.model_dump_json())


class DeviceAuth(object):
    """设备授权认证类"""

    def __init__(self):
        # 初始化客户端ID和API基础URL
        self._client_id = "57294420732781205987760324720643.app.coze"
        self._api_base = COZE_CN_BASE_URL
        # 创建设备OAuth应用实例
        self._oauth_app = DeviceOAuthApp(client_id=self._client_id, base_url=self._api_base)
        self._token: Optional[OAuthToken] = None
        self._file_cache = FileCache(".cache")

    @property
    def token(self) -> Optional[OAuthToken]:
        """获取有效的token

        按以下顺序尝试获取token:
        1. 使用内存中缓存的token
        2. 从文件加载token
        3. 重新获取新token
        """
        # 检查内存中的token
        if self._token and self._is_token_valid(self._token):
            return self._token

        # 尝试从文件加载token
        if file_token := self._load_token():
            if self._is_token_valid(file_token):
                self._token = file_token
                return self._token
            # token过期但有refresh_token,尝试刷新
            if refreshed_token := self._refresh_token(file_token):
                self._token = refreshed_token
                self._save_token(refreshed_token)
                return self._token

        # 重新获取新token
        if new_token := self._get_token():
            self._token = new_token
            self._save_token(new_token)
            return self._token

        return None

    def client(self, workspace_id: Optional[str] = None) -> Coze:
        """创建Coze客户端"""
        if not (token := self.token):
            raise Exception("No valid token found")
        return Coze(auth=TokenAuth(token=token.access_token), base_url=self._api_base)

    def _is_token_valid(self, token: OAuthToken) -> bool:
        """检查token是否有效"""
        return token.expires_in + 30 > int(time.time())

    def _refresh_token(self, token: OAuthToken) -> Optional[OAuthToken]:
        """刷新token"""
        if not token.refresh_token:
            return None
        try:
            return self._oauth_app.refresh_access_token(token.refresh_token)
        except Exception as e:
            print(e)
            return None

    def _load_token(self) -> Optional[OAuthToken]:
        """从文件加载token"""
        try:
            return self._file_cache.get_typed(self._cache_key(), OAuthToken)
        except Exception:
            return None

    def _save_token(self, token: OAuthToken) -> None:
        """保存token到文件"""
        self._file_cache.set_typed(self._cache_key(), token)

    def _get_token(self) -> Optional[OAuthToken]:
        """获取新token"""
        try:
            device_code = self._oauth_app.get_device_code()
            print("Please open url:", device_code.verification_url)
            return self._oauth_app.get_access_token(device_code.device_code, poll=True)
        except Exception:
            return None

    @lru_cache(maxsize=1)
    def _cache_key(self) -> str:
        """获取token缓存文件路径"""
        return f"coze_token_{self._client_id}.json"


class RichBot(Bot):
    def __init__(self, bot: Bot):
        super().__init__(**bot.model_dump())

    def __rich__(self) -> str:
        print(self.model_dump_json())
        return """[bold blue]Bot Info[/bold blue]
[yellow]Name:[/yellow] {name}
[yellow]Description:[/yellow] {description}
[yellow]Version:[/yellow] {version}
[yellow]Create Time:[/yellow] {create_time}
[yellow]Update Time:[/yellow] {update_time}
[yellow]Mode:[/yellow] {bot_mode}
[yellow]Icon URL:[/yellow] [link={icon_url}]{icon_url}[/link]
[yellow]Prompt:[/yellow]
  [green]{prompt}[/green]
[yellow]Onboarding:[/yellow]
  [yellow]Prologue:[/yellow] [cyan]{prologue}[/cyan]
  [yellow]Questions:[/yellow] [cyan]{suggested_questions}[/cyan]
[yellow]Model:[/yellow]
  [yellow]ID:[/yellow] [cyan]{model_id}[/cyan]
  [yellow]Name:[/yellow] [cyan]{model_name}[/cyan]
""".format(
            name=self.name,
            description=self.description or "[italic]-[/italic]",
            version=self.version,
            create_time=self.create_time,
            update_time=self.update_time,
            bot_mode={0: "Single Agent", 1: "Multi Agent", 2: "Workflow as Agent"}[self.bot_mode],
            icon_url=self.icon_url,
            prompt=self.prompt_info.prompt or "[italic]-[/italic]",
            prologue=self.onboarding_info.prologue or "[italic]-[/italic]",
            suggested_questions=self.onboarding_info.suggested_questions or "[italic]-[/italic]",
            model_id=self.model_info.model_id or "[italic]-[/italic]",
            model_name=self.model_info.model_name or "[italic]-[/italic]",
        )


class CozeCli(object):
    """Coze交互式命令行界面"""

    def __init__(self):
        self._auth = DeviceAuth()
        self._file_cache = FileCache(".cache")

    def _ensure_token(self):
        """确保取到有效的token"""
        if not self._auth.token:
            raise Exception("无法获取有效的token")

    def list_workspaces(
        self,
        page: int = 1,
        size: int = 10,
        json_output: bool = False,
        all_pages: bool = False,
        name_filter: Optional[str] = None,
    ):
        """列出工作空间"""
        total = 0
        workspaces = []
        try:
            workspaces_page = self._auth.client().workspaces.list(page_num=page, page_size=size)
            total = workspaces_page.total
            if all_pages:
                workspaces = [ws for ws in workspaces_page]
            else:
                workspaces = workspaces_page.items
        except Exception as e:
            console.print(f"[red]获取工作空间列表失败: {str(e)}[/red]")
            return

        for ws in workspaces:
            self._set_workspace_cache(ws)

        # Filter by name
        if name_filter:
            workspaces = [ws for ws in workspaces if name_filter.lower() in ws.name.lower()]

        if json_output:
            result = {
                "total": len(workspaces),
                "items": [ws.model_dump(mode="json") for ws in workspaces],
            }
            console.print(json.dumps(result, indent=2, ensure_ascii=False))
            return

        # 表格输出
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID", style="dim")
        table.add_column("Name")
        table.add_column("Type")
        table.add_column("Role")

        for ws in workspaces:
            table.add_row(ws.id, ws.name, ws.workspace_type, ws.role_type)

        console.print(table)
        if all_pages:
            console.print(f"\n总数: {len(workspaces)}\n")
        else:
            console.print(f"\n总数: {total} | 当前页: {page} | 每页: {size}\n")

    def list_bots(self, workspace_id: str, page: int = 1, size: int = 10):
        """列出工作空间下的机器人"""
        try:
            # 获取机器人列表
            bots_page = self._auth.client().bots.list(space_id=workspace_id)

            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("ID")
            table.add_column("Name")
            table.add_column("Description")
            table.add_column("Publish Time")

            for bot in bots_page.items:
                table.add_row(bot.bot_id, bot.bot_name, bot.description or "-", bot.publish_time)
                self._set_bot_cache(bot)

            console.print(table)
            console.print(f"\n总数: {bots_page.total} | 当前页: {page} | 每页: {size}\n")

        except Exception as e:
            console.print(f"[red]获取机器人列表失败: {str(e)}[/red]")

    def retrieve_bot(self, workspace_id: str, bot_id: str):
        """显示机器人详细信息"""
        try:
            workspace = self._get_workspace_cache(workspace_id)
            if not workspace:
                console.print(f"[red]工作空间不存在: {workspace_id}[/red]")
                return

            # 获取机器人列表
            bot = self._auth.client().bots.retrieve(bot_id=bot_id)
            if not bot:
                console.print(f"[red]机器人不存在: {bot_id}[/red]")
                return

            # 显示机器人详细信息
            console.print(RichBot(bot))

        except Exception as e:
            console.print(f"[red]获取机器人信息失败: {str(e)}[/red]")

    def _set_workspace_cache(self, workspace: Workspace):
        self._file_cache.set_typed(f"workspace_{workspace.id}.json", workspace)

    def _get_workspace_cache(self, workspace_id: str) -> Optional[Workspace]:
        return self._file_cache.get_typed(f"workspace_{workspace_id}.json", Workspace)

    def _set_bot_cache(self, bot: Bot):
        self._file_cache.set_typed(f"bot_{bot.bot_id}.json", bot)

    def _get_bot_cache(self, bot_id: str) -> Optional[Bot]:
        return self._file_cache.get_typed(f"bot_{bot_id}.json", Bot)


coze = CozeCli()


@click.group()
def cli():
    """Coze 命令行工具"""
    pass


@cli.group()
def workspace():
    """工作空间相关操作"""
    pass


@workspace.command("list")
@click.option("--page", default=1, help="页码")
@click.option("--size", default=10, help="每页数量")
@click.option("--json", "json_output", is_flag=True, help="以JSON格式输出")
@click.option("--all", "all_pages", is_flag=True, help="获取所有数据")
@click.option("--name", "name_filter", help="按名称过滤（不区分大小写）")
def list_workspaces(page: int, size: int, json_output: bool, all_pages: bool, name_filter: Optional[str]):
    """列出所有工作空间"""
    try:
        coze.list_workspaces(page, size, json_output, all_pages, name_filter)
    except Exception as e:
        console.print(f"[red]错误: {str(e)}[/red]")


@cli.group()
def bot():
    """机器人相关操作"""
    pass


@bot.command("list")
@click.argument("workspace")
@click.option("--page", default=1, help="页码")
@click.option("--size", default=10, help="每页数量")
def list_bots(workspace: str, page: int, size: int):
    """列出工作空间下的所有机器人"""
    try:
        coze.list_bots(workspace, page, size)
    except Exception as e:
        console.print(f"[red]错误: {str(e)}[/red]")


@bot.command("retrieve")
@click.argument("workspace_id")
@click.argument("bot_id")
def retrieve_bot(workspace_id: str, bot_id: str):
    """显示机器人详细信息"""
    try:
        coze.retrieve_bot(workspace_id, bot_id)
    except Exception as e:
        console.print(f"[red]错误: {str(e)}[/red]")


if __name__ == "__main__":
    cli()
