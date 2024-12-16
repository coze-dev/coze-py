#!/usr/bin/env python3
import json
import logging
import os
import time
import warnings
from datetime import datetime
from functools import lru_cache
from typing import List, Optional, Type, TypeVar

from pydantic import BaseModel

from cozepy import (
    COZE_CN_BASE_URL,
    Bot,
    Coze,
    CreateDatasetRes,
    DeviceOAuthApp,
    OAuthToken,
    TemplateEntityType,
    TokenAuth,
    Voice,
    Workspace,
)
from cozepy.datasets import DatasetFormatType
from cozepy.log import setup_logging

try:
    from rich.console import Console
    from rich.table import Table
except ImportError:
    warnings.warn("rich is not installed, please install it by `pip install rich`")
    exit(1)

try:
    import click
except ImportError:
    warnings.warn("click is not installed, please install it by `pip install click`")
    exit(1)

BaseT = TypeVar("BaseT", bound=BaseModel)


setup_logging(logging.ERROR)
console = Console()


def format_time(timestamp: int) -> str:
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


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
    """Device authorization authentication class"""

    def __init__(self):
        # Initialize client ID and API base URL
        self._client_id = "57294420732781205987760324720643.app.coze"
        self._api_base = COZE_CN_BASE_URL
        # Create device OAuth application instance
        self._oauth_app = DeviceOAuthApp(client_id=self._client_id, base_url=self._api_base)
        self._token: Optional[OAuthToken] = None
        self._file_cache = FileCache(".cache")

    @property
    def token(self) -> Optional[OAuthToken]:
        """Get valid token

        Try to get token in the following order:
        1. Use token in memory
        2. Load token from file
        3. Get new token
        """
        # Check token in memory
        if self._token and self._is_token_valid(self._token):
            return self._token

        # Try to load token from file
        if file_token := self._load_token():
            if self._is_token_valid(file_token):
                self._token = file_token
                return self._token
            # Token expired but has refresh_token, try to refresh
            if refreshed_token := self._refresh_token(file_token):
                self._token = refreshed_token
                self._save_token(refreshed_token)
                return self._token

        # Get new token
        if new_token := self._get_token():
            self._token = new_token
            self._save_token(new_token)
            return self._token

        return None

    def client(self, workspace_id: Optional[str] = None) -> Coze:
        """Create Coze client"""
        if not (token := self.token):
            raise Exception("No valid token found")
        return Coze(auth=TokenAuth(token=token.access_token), base_url=self._api_base)

    def _is_token_valid(self, token: OAuthToken) -> bool:
        """Check if token is valid"""
        return token.expires_in + 30 > int(time.time())

    def _refresh_token(self, token: OAuthToken) -> Optional[OAuthToken]:
        """Refresh token"""
        if not token.refresh_token:
            return None
        try:
            return self._oauth_app.refresh_access_token(token.refresh_token)
        except Exception as e:
            print(e)
            return None

    def _load_token(self) -> Optional[OAuthToken]:
        """Load token from file"""
        try:
            return self._file_cache.get_typed(self._cache_key(), OAuthToken)
        except Exception:
            return None

    def _save_token(self, token: OAuthToken) -> None:
        """Save token to file"""
        self._file_cache.set_typed(self._cache_key(), token)

    def _get_token(self) -> Optional[OAuthToken]:
        """Get new token"""
        try:
            device_code = self._oauth_app.get_device_code()
            console.print(f"[yellow]Please open url: {device_code.verification_url}[/yellow]")
            return self._oauth_app.get_access_token(device_code.device_code, poll=True)
        except Exception:
            return None

    @lru_cache(maxsize=1)
    def _cache_key(self) -> str:
        """Get token cache file path"""
        return f"coze_token_{self._client_id}.json"


class RichBot(Bot):
    def __init__(self, bot: Bot):
        super().__init__(**bot.model_dump())

    def print(self, json_output: bool):
        if json_output:
            print(self.model_dump_json())
            return

        console.print(
            """[bold blue]Bot Info[/bold blue]
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
        )


class RichWorkspaceList(object):
    def __init__(self, workspaces: List[Workspace], total: int, page: int, size: int, json_output: bool):
        self._workspaces = workspaces
        self._total = total
        self._page = page
        self._size = size
        self._json_output = json_output

    def print(self):
        if self._json_output:
            print(self._get_json())
            return
        table = self._get_table()
        console.print(table)
        console.print(f"Total: {self._total} | Page: {self._page} | Size: {self._size}")

    def _get_table(self) -> Table:
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID", style="dim")
        table.add_column("Name")
        table.add_column("Type")
        table.add_column("Role")

        for ws in self._workspaces:
            table.add_row(ws.id, ws.name, ws.workspace_type, ws.role_type)

        return table

    def _get_json(self) -> str:
        return json.dumps(
            {
                "total": self._total,
                "page": self._page,
                "size": self._size,
                "items": [ws.model_dump(mode="json") for ws in self._workspaces],
            },
            indent=2,
            ensure_ascii=False,
        )


class RichBotList(object):
    def __init__(self, bots: List[Bot], total: int, page: int, size: int, json_output: bool):
        self._bots = bots
        self._total = total
        self._page = page
        self._size = size
        self._json_output = json_output

    def __rich__(self) -> str:
        if self._json_output:
            return self._get_json()
        table = self._get_table()
        table.add_section()
        table.add_row(
            f"Total: {self._total} | Page: {self._page} | Size: {self._size}", style="bold cyan", end_section=True
        )
        return table

    def _get_table(self) -> Table:
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID", style="dim")
        table.add_column("Name")
        table.add_column("Description")
        table.add_column("Publish Time")

        for bot in self._bots:
            table.add_row(bot.bot_id, bot.bot_name, bot.description or "-", bot.publish_time)

        return table

    def _get_json(self) -> str:
        return json.dumps(
            {
                "total": self._total,
                "page": self._page,
                "size": self._size,
                "items": [bot.model_dump(mode="json") for bot in self._bots],
            },
            indent=2,
            ensure_ascii=False,
        )


class RichVoiceList(object):
    def __init__(self, voices: List[Voice], json_output: bool = False):
        self._voices = voices
        self._json_output = json_output

    def __rich__(self) -> str:
        if self._json_output:
            return self._get_json()
        return self._get_table()

    def _get_table(self) -> Table:
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID", style="dim")
        table.add_column("Name")
        table.add_column("System")
        table.add_column("Language")
        # table.add_column("Preview Audio")
        table.add_column("Training Times")
        table.add_column("Create Time")
        table.add_column("Update Time")

        for voice in self._voices:
            table.add_row(
                voice.voice_id,
                voice.name,
                "[bold blue]Yes[/bold blue]" if voice.is_system_voice else "[bold yellow]No[/bold yellow]",
                f"({voice.language_code}) {voice.language_name}",
                # f"[link={voice.preview_audio}]{voice.preview_audio}[/link]",
                f"{voice.available_training_times} times",
                format_time(voice.create_time),
                format_time(voice.update_time),
            )

        return table

    def _get_json(self) -> str:
        return json.dumps(
            {
                "items": [voice.model_dump(mode="json") for voice in self._voices],
            },
            indent=2,
            ensure_ascii=False,
        )


class CozeAPI(object):
    """Coze API"""

    def __init__(self):
        self._auth = DeviceAuth()
        self._file_cache = FileCache(".cache")

    @property
    def client(self) -> Coze:
        return self._auth.client()

    def logout(self):
        for file in os.listdir(".cache"):
            os.remove(os.path.join(".cache", file))

    def list_workspaces(
        self,
        page: int = 1,
        size: int = 10,
        json_output: bool = False,
        all_pages: bool = False,
        name_filter: Optional[str] = None,
    ):
        """List workspaces"""
        total = 0
        workspaces = []
        try:
            workspaces_page = self.client.workspaces.list(page_num=page, page_size=size)
            total = workspaces_page.total
            if all_pages:
                workspaces = [ws for ws in workspaces_page]
            else:
                workspaces = workspaces_page.items
        except Exception as e:
            console.print(f"[red]Get workspace list failed: {str(e)}[/red]")
            return

        for ws in workspaces:
            self._set_workspace_cache(ws)

        # Filter by name
        if name_filter:
            workspaces = [ws for ws in workspaces if name_filter.lower() in ws.name.lower()]

        RichWorkspaceList(workspaces, total, page, size, json_output).print()

    def list_bots(
        self,
        workspace_id: str,
        page: int = 1,
        size: int = 10,
        json_output: bool = False,
        all_pages: bool = False,
        name_filter: Optional[str] = None,
    ):
        """List bots in a workspace"""
        bots = []
        try:
            # Get bot list
            bots_page = self.client.bots.list(space_id=workspace_id, page_num=page, page_size=size)
            if all_pages:
                bots = [bot for bot in bots_page]
            else:
                bots = bots_page.items
        except Exception as e:
            console.print(f"[red]Get bot list failed: {str(e)}[/red]")
            return

        for bot in bots:
            self._set_bot_cache(bot)

        if name_filter:
            bots = [bot for bot in bots if name_filter.lower() in bot.bot_name.lower()]

        rich_bot_list = RichBotList(bots, bots_page.total, page, size, json_output)
        console.print(rich_bot_list)

    def retrieve_bot(self, workspace_id: str, bot_id: str) -> Bot:
        """Show bot details"""
        workspace = self._get_workspace_cache(workspace_id)
        if not workspace:
            raise Exception(f"Workspace not found: {workspace_id}")

        # Get bot
        bot = self.client.bots.retrieve(bot_id=bot_id)
        if not bot:
            raise Exception(f"Bot not found: {bot_id}")

        return bot

    def list_voices(
        self,
        page: int = 1,
        size: int = 10,
        json_output: bool = False,
        all_pages: bool = False,
        name_filter: Optional[str] = None,
        exclude_system_voice: bool = False,
    ):
        """List all available voices"""
        voices = []
        try:
            voices_page = self.client.audio.voices.list(
                filter_system_voice=exclude_system_voice, page_num=page, page_size=size
            )
            if all_pages:
                voices = [voice for voice in voices_page]
            else:
                voices = voices_page.items
        except Exception as e:
            console.print(f"[red]Get voice list failed: {str(e)}[/red]")
            return

        for voice in voices:
            self._set_voice_cache(voice)

        if name_filter:
            voices = [voice for voice in voices if name_filter.lower() in voice.name.lower()]

        rich_voice_list = RichVoiceList(voices, json_output)
        console.print(rich_voice_list)

    def create_speech(
        self,
        text: str,
        voice_id: str,
        output_file: Optional[str] = None,
        response_format: str = "mp3",
        speed: float = 1,
        sample_rate: int = 24000,
    ) -> str:
        if not output_file:
            raise ValueError("Please specify output file")

        speech = self.client.audio.speech.create(
            input=text,
            voice_id=voice_id,
            response_format=response_format,
            speed=speed,
            sample_rate=sample_rate,
        )
        speech.write_to_file(output_file)
        return output_file

    """dataset"""

    def create_dataset(
        self, name: str, space_id: str, format_type: DatasetFormatType, description: Optional[str], icon: Optional[str]
    ) -> CreateDatasetRes:
        if not name:
            raise ValueError("Please specify dataset name")
        if not space_id:
            raise ValueError("Please specify space id")
        if format_type is None:
            raise ValueError("Please specify dataset format")
        if icon and os.path.exists(icon):
            file = self.client.files.upload(file=icon)
            icon_file_id = file.id
        else:
            icon_file_id = icon

        res = self._auth.client().datasets.create(
            name=name,
            space_id=space_id,
            format_type=format_type,
            description=description,
            icon_file_id=icon_file_id,
        )
        return res

    def _set_workspace_cache(self, workspace: Workspace):
        self._file_cache.set_typed(f"workspace_{workspace.id}.json", workspace)

    def _get_workspace_cache(self, workspace_id: str) -> Optional[Workspace]:
        return self._file_cache.get_typed(f"workspace_{workspace_id}.json", Workspace)

    def _set_bot_cache(self, bot: Bot):
        self._file_cache.set_typed(f"bot_{bot.bot_id}.json", bot)

    def _get_bot_cache(self, bot_id: str) -> Optional[Bot]:
        return self._file_cache.get_typed(f"bot_{bot_id}.json", Bot)

    def _set_voice_cache(self, voice: Voice):
        self._file_cache.set_typed(f"voice_{voice.voice_id}.json", voice)

    def _get_voice_cache(self, voice_id: str) -> Optional[Voice]:
        return self._file_cache.get_typed(f"voice_{voice_id}.json", Voice)


coze = CozeAPI()


@click.group()
def cli():
    """Coze CLI"""
    pass


# logout or auth revoke
@cli.command("logout")
def logout():
    """Logout"""
    coze.logout()
    console.print("[green]Logout successfully[/green]")


@cli.group()
def workspace():
    """Workspace"""
    pass


@workspace.command("list")
@click.option("--page", default=1, help="page number")
@click.option("--size", default=10, help="page size")
@click.option("--json", "json_output", is_flag=True, help="output in json format")
@click.option("--all", "all_pages", is_flag=True, help="get all bots")
@click.option("--name", "name_filter", help="filter by name")
def list_workspaces(page: int, size: int, json_output: bool, all_pages: bool, name_filter: Optional[str]):
    """List all workspaces"""
    try:
        coze.list_workspaces(page, size, json_output, all_pages, name_filter)
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")


@cli.group()
def bot():
    """Bot"""
    pass


@bot.command("list")
@click.argument("workspace_id")
@click.option("--page", default=1, help="page number")
@click.option("--size", default=10, help="page size")
@click.option("--json", "json_output", is_flag=True, help="output in json format")
@click.option("--all", "all_pages", is_flag=True, help="get all bots")
@click.option("--name", "name_filter", help="filter by name")
def list_bots(workspace_id: str, page: int, size: int, json_output: bool, all_pages: bool, name_filter: Optional[str]):
    """List all bots in a workspace"""
    try:
        coze.list_bots(workspace_id, page, size, json_output, all_pages, name_filter)
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")


@bot.command("retrieve")
@click.argument("workspace_id")
@click.argument("bot_id")
@click.option("--json", "json_output", is_flag=True, help="output in json format")
def retrieve_bot(workspace_id: str, bot_id: str, json_output: bool):
    """Retrieve bot details"""
    try:
        bot = coze.retrieve_bot(workspace_id, bot_id)
        RichBot(bot).print(json_output)
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")


@cli.group()
def audio():
    """Audio"""
    pass


@audio.group()
def voice():
    """Voice"""
    pass


@voice.command("list")
@click.option("--page", default=1, help="page number")
@click.option("--size", default=10, help="page size")
@click.option("--json", "json_output", is_flag=True, help="output in json format")
@click.option("--all", "all_pages", is_flag=True, help="get all voices")
@click.option("--name", "name_filter", help="filter by name")
@click.option("--exclude-system", "exclude_system", is_flag=True, help="exclude system voice")
def list_voices(
    page: int, size: int, json_output: bool, all_pages: bool, name_filter: Optional[str], exclude_system: bool
):
    """List all available voices"""
    try:
        coze.list_voices(page, size, json_output, all_pages, name_filter, exclude_system)
    except Exception as e:
        console.print(f"[red]错误: {str(e)}[/red]")


@audio.group()
def speech():
    """Speech"""
    pass


@speech.command("create")
@click.argument("text")
@click.option("--voice_id", "voice_id", help="Voice ID")
@click.option("--output", "-o", "output_file", help="Save audio file path")
@click.option("--format", "response_format", help="Audio format", default="mp3")
@click.option("--speed", "speed", help="Speech speed", default=1)
@click.option("--sample_rate", "sample_rate", help="Sample rate", default=24000)
def create_speech(
    text: str, voice_id: str, output_file: Optional[str], response_format: str, speed: float, sample_rate: int
):
    """Create speech synthesis task

    VOICE_ID: Voice ID
    TEXT: Text to be synthesized
    """
    try:
        output_file = coze.create_speech(text, voice_id, output_file, response_format, speed, sample_rate)
        console.print(f"\n[green]Audio saved to: {output_file}[/green]")
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")


@cli.group()
def dataset():
    """Dataset"""
    pass


@dataset.command("create")
@click.option("--name", "name", help="Dataset name")
@click.option("--space_id", "space_id", help="Space ID")
@click.option("--format", "format_type", help="Dataset format", default=0)
@click.option("--description", "description", help="Dataset description")
@click.option("--icon", "icon", help="Dataset icon")
def create_dataset(
    name: str, space_id: str, format_type: DatasetFormatType, description: Optional[str], icon: Optional[str]
):
    """Create a dataset"""
    try:
        res = coze.create_dataset(name, space_id, format_type, description, icon)
        console.print(f"[green]Dataset created: {res.dataset_id}[/green]")
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")


@cli.group()
def template():
    """Template"""
    pass


@template.command("duplicate")
@click.argument("template_id")
@click.argument("workspace_id")
@click.option("--name", "name", help="Template name")
def duplicate_template(template_id: str, workspace_id: str, name: Optional[str]):
    """Duplicate a template"""
    try:
        res = coze._auth.client().templates.duplicate(
            template_id=template_id,
            workspace_id=workspace_id,
            name=name,
        )
        console.print(f"[green]Template duplicated: {res.entity_id}, {res.entity_type}[/green]")
        if res.entity_type == TemplateEntityType.AGENT:
            agent_url = f"https://www.coze.cn/space/{workspace_id}/bot/{res.entity_id}"
            console.print(f"[green]Agent URL: {agent_url}[/green]")
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")


if __name__ == "__main__":
    cli()
