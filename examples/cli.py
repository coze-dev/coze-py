#!/usr/bin/env python3
import json
import logging
import os
import time
import warnings
from datetime import datetime
from functools import lru_cache
from typing import List, Optional, Tuple, Type, TypeVar, Union

from pydantic import BaseModel

from cozepy import (
    COZE_CN_BASE_URL,
    Bot,
    Coze,
    CreateDatasetResp,
    Dataset,
    DeviceOAuthApp,
    Document,
    DocumentBase,
    DocumentFormatType,
    DocumentProgress,
    DocumentSourceInfo,
    OAuthToken,
    Photo,
    TemplateEntityType,
    TokenAuth,
    Voice,
    Workspace,
    WorkspaceType,
)
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

DEBUG = os.getenv("DEBUG", "false").lower() == "true"

setup_logging(logging.ERROR if not DEBUG else logging.DEBUG)
console = Console()


def format_time(timestamp: int) -> str:
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


def is_image_file(file: str) -> bool:
    return file.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".ico", ".webp"))


def is_int(value: str) -> bool:
    try:
        int(value)
        return True
    except ValueError:
        return False


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
    def __init__(self, workspaces: List[Workspace], total: int, page: int, size: int):
        self._workspaces = workspaces
        self._total = total
        self._page = page
        self._size = size

    def print(self, json_output: bool = False):
        if json_output:
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
    def __init__(self, bots: List[Bot], total: int, page: int, size: int):
        self._bots = bots
        self._total = total
        self._page = page
        self._size = size

    def print(self, json_output: bool = False):
        if json_output:
            print(self._get_json())
            return

        console.print(self._get_table())
        console.print(f"Total: {self._total} | Page: {self._page} | Size: {self._size}")

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


class RichDatasetList(object):
    def __init__(self, datasets: List[Dataset], total: int, page: int, size: int):
        self._datasets = datasets
        self._total = total
        self._page = page
        self._size = size

    def print(self, json_output: bool = False):
        if json_output:
            print(self._get_json())
            return

        console.print(self._get_table())
        console.print(f"Total: {self._total} | Page: {self._page} | Size: {self._size}")

    def _get_table(self) -> Table:
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID", style="dim")
        table.add_column("Name")
        table.add_column("Format")
        table.add_column("Create Time")
        table.add_column("Update Time")

        for dataset in self._datasets:
            table.add_row(
                dataset.dataset_id,
                dataset.name,
                {0: "Text", 1: "Table", 2: "Image"}[dataset.format_type],
                format_time(dataset.create_time),
                format_time(dataset.update_time),
            )

        return table

    def _get_json(self) -> str:
        return json.dumps(
            {
                "total": self._total,
                "page": self._page,
                "size": self._size,
                "items": [dataset.model_dump(mode="json") for dataset in self._datasets],
            },
            indent=2,
            ensure_ascii=False,
        )


class RichDocumentProgressList(object):
    def __init__(self, document_progress: DocumentProgress):
        self._document_progress = document_progress

    def print(self):
        console.print(
            """[bold blue]Document Progress[/bold blue]
[yellow]ID:[/yellow] [dim]{document_id}[/dim]
[yellow]Name:[/yellow] {document_name}
[yellow]Type:[/yellow] {type}
[yellow]Status:[/yellow] {status}
[yellow]Progress:[/yellow] {progress}%
[yellow]Remaining Time:[/yellow] {remaining_time}
""".format(
                document_id=self._document_progress.document_id,
                document_name=self._document_progress.document_name,
                type=self._document_progress.type,
                status=self._document_progress.status.name,
                progress=self._document_progress.progress,
                remaining_time=format_time(self._document_progress.remaining_time),
            )
        )


class RichDocumentList(object):
    def __init__(self, documents: List[Document], total: int, page: int, size: int):
        self._documents = documents
        self._total = total
        self._page = page
        self._size = size

    def print(self, json_output: bool = False):
        if json_output:
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
        table.add_column("Create Time")
        table.add_column("Update Time")

        for document in self._documents:
            table.add_row(
                document.document_id,
                document.name,
                document.type,
                format_time(document.create_time),
                format_time(document.update_time),
            )

        return table

    def _get_json(self) -> str:
        return json.dumps(
            {
                "total": self._total,
                "page": self._page,
                "size": self._size,
                "items": [document.model_dump(mode="json") for document in self._documents],
            },
            indent=2,
            ensure_ascii=False,
        )


class RichDocument(object):
    def __init__(self, document: Document):
        self._document = document

    def print(self, json_output: bool = False):
        if json_output:
            print(self._document.model_dump_json(indent=2))
            return

        console.print(f"ID: [dim]{self._document.document_id}[/dim]")
        console.print(f"Name: {self._document.name}")
        console.print(f"Type: {self._document.type}")
        console.print(f"Create Time: {format_time(self._document.create_time)}")
        console.print(f"Update Time: {format_time(self._document.update_time)}")


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
        all_pages: bool = False,
        name_filter: Optional[str] = None,
        workspace_type: Optional[WorkspaceType] = None,
    ) -> RichWorkspaceList:
        """List workspaces"""
        workspaces_page = self.client.workspaces.list(page_num=page, page_size=size)
        if all_pages:
            workspaces = [ws for ws in workspaces_page]
        else:
            workspaces = workspaces_page.items

        for ws in workspaces:
            self._set_workspace_cache(ws)

        # Filter by name
        if name_filter:
            workspaces = [ws for ws in workspaces if name_filter.lower() in ws.name.lower()]
        if workspace_type:
            workspaces = [ws for ws in workspaces if ws.workspace_type == workspace_type]

        return RichWorkspaceList(workspaces, workspaces_page.total, page, size)

    def list_bots(
        self,
        workspace_id: str,
        page: int = 1,
        size: int = 10,
        all_pages: bool = False,
        name_filter: Optional[str] = None,
    ) -> RichBotList:
        """List bots in a workspace"""
        bots_page = self.client.bots.list(space_id=workspace_id, page_num=page, page_size=size)
        if all_pages:
            bots = [bot for bot in bots_page]
        else:
            bots = bots_page.items

        for bot in bots:
            self._set_bot_cache(bot)

        if name_filter:
            bots = [bot for bot in bots if name_filter.lower() in bot.bot_name.lower()]

        return RichBotList(bots, bots_page.total, page, size)

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
        self, name: str, space_id: str, format_type: DocumentFormatType, description: Optional[str], icon: Optional[str]
    ) -> CreateDatasetResp:
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

    def list_datasets(
        self,
        space_id: str,
        name: Optional[str] = None,
        format_type: Optional[DocumentFormatType] = None,
        page: int = 1,
        size: int = 10,
        all_pages: bool = False,
    ) -> RichDatasetList:
        """List datasets in a space"""
        datasets_page = self.client.datasets.list(
            space_id=space_id,
            name=name,
            format_type=format_type,
            page_num=page,
            page_size=size,
        )
        if all_pages:
            datasets = [dataset for dataset in datasets_page]
        else:
            datasets = datasets_page.items

        for dataset in datasets:
            self._set_dataset_cache(dataset)

        return RichDatasetList(datasets, datasets_page.total, page, size)

    def update_dataset(self, dataset_id: str, name: Optional[str], description: Optional[str], icon: Optional[str]):
        if not dataset_id:
            raise ValueError("Please specify dataset id")
        if icon and os.path.exists(icon):
            file = self.client.files.upload(file=icon)
            icon_file_id = file.id
        else:
            icon_file_id = icon

        self.client.datasets.update(
            dataset_id=dataset_id, name=name, description=description, icon_file_id=icon_file_id
        )

    def delete_dataset(self, dataset_id: str):
        if not dataset_id:
            raise ValueError("Please specify dataset id")
        self.client.datasets.delete(dataset_id=dataset_id)

    def get_dataset_process(self, dataset_id: str, document_id: str) -> RichDocumentProgressList:
        if not dataset_id:
            raise ValueError("Please specify dataset id")
        if not document_id:
            raise ValueError("Please specify document id")
        res = self.client.datasets.process(dataset_id=dataset_id, document_ids=[document_id])
        return RichDocumentProgressList(res.items[0])

    def list_dataset_documents(
        self, dataset_id: str, page: int = 1, size: int = 10, all_pages: bool = False
    ) -> RichDocumentList:
        if not dataset_id:
            raise ValueError("Please specify dataset id")
        documents_page = self.client.datasets.documents.list(dataset_id=dataset_id, page_num=page, page_size=size)
        if all_pages:
            documents = [document for document in documents_page]
        else:
            documents = documents_page.items

        for document in documents:
            self._set_document_cache(document)

        return RichDocumentList(documents, documents_page.total, page, size)

    def create_dataset_document(self, dataset_id: str, filepath: str) -> RichDocument:
        if not dataset_id:
            raise ValueError("Please specify dataset id")
        if not filepath:
            raise ValueError("Please specify file")
        if is_image_file(filepath):
            if os.path.exists(filepath):
                file = self.client.files.upload(file=filepath)
                file_id = file.id
            else:
                raise ValueError("File not found")
            res = self.client.datasets.documents.create(
                dataset_id=dataset_id,
                document_bases=[
                    DocumentBase(
                        name=os.path.basename(filepath),
                        source_info=DocumentSourceInfo.build_file_id(file_id),
                    )
                ],
                format_type=DocumentFormatType.IMAGE,
            )
            return RichDocument(res[0])
        else:
            raise ValueError("Unsupported file type")

    def list_dataset_images(
        self,
        dataset_id: str,
        keyword: Optional[str] = None,
        has_caption: bool = False,
        page: int = 1,
        size: int = 10,
        all_pages: bool = False,
    ) -> RichDocumentList:
        if not dataset_id:
            raise ValueError("Please specify dataset id")
        images_page = self.client.datasets.images.list(
            dataset_id=dataset_id, page_num=page, page_size=size, keyword=keyword, has_caption=has_caption
        )
        if all_pages:
            images = [image for image in images_page]
        else:
            images = images_page.items

        for image in images:
            self._set_image_cache(image)

        return RichDocumentList(images, images_page.total, page, size)

    def update_dataset_image(self, dataset_id: str, document_id: str, caption: str):
        if not dataset_id:
            raise ValueError("Please specify dataset id")
        if not document_id:
            raise ValueError("Please specify document id")
        self.client.datasets.images.update(dataset_id=dataset_id, document_id=document_id, caption=caption)

    def upload_file(self, file: Union[os.PathLike, Tuple[str, bytes]]):
        return self.client.files.upload(file=file)

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

    def _set_dataset_cache(self, dataset: Dataset):
        self._file_cache.set_typed(f"dataset_{dataset.dataset_id}.json", dataset)

    def _get_dataset_cache(self, dataset_id: str) -> Optional[Dataset]:
        return self._file_cache.get_typed(f"dataset_{dataset_id}.json", Dataset)

    def _set_document_cache(self, document: Document):
        self._file_cache.set_typed(f"document_{document.document_id}.json", document)

    def _get_document_cache(self, document_id: str) -> Optional[Document]:
        return self._file_cache.get_typed(f"document_{document_id}.json", Document)

    def _set_image_cache(self, image: Photo):
        self._file_cache.set_typed(f"image_{image.document_id}.json", image)

    def _get_image_cache(self, document_id: str) -> Optional[Photo]:
        return self._file_cache.get_typed(f"image_{document_id}.json", Photo)


coze = CozeAPI()

"""cli"""


@click.group()
def cli():
    """Coze CLI"""
    pass


"""auth"""


# logout or auth revoke
@cli.command("logout")
def logout():
    """Logout"""
    coze.logout()
    console.print("[green]Logout successfully[/green]")


"""workspace"""


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
@click.option(
    "--type", "workspace_type", help="workspace type", type=click.Choice([WorkspaceType.PERSONAL, WorkspaceType.TEAM])
)
def list_workspaces(
    page: int, size: int, json_output: bool, all_pages: bool, name_filter: Optional[str], workspace_type: WorkspaceType
):
    """List all workspaces"""
    try:
        res = coze.list_workspaces(page, size, all_pages, name_filter, workspace_type)
        res.print(json_output)
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")


"""bot"""


@cli.group()
def bot():
    """Bot"""
    pass


@bot.command("list")
@click.option("--workspace_id", "workspace_id", help="Workspace ID")
@click.option("--page", default=1, help="page number")
@click.option("--size", default=10, help="page size")
@click.option("--json", "json_output", is_flag=True, help="output in json format")
@click.option("--all", "all_pages", is_flag=True, help="get all bots")
@click.option("--name", "name_filter", help="filter by name")
def list_bots(workspace_id: str, page: int, size: int, json_output: bool, all_pages: bool, name_filter: Optional[str]):
    """List all bots in a workspace"""
    try:
        res = coze.list_bots(workspace_id, page, size, all_pages, name_filter)
        res.print(json_output)
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")


@bot.command("retrieve")
@click.option("--workspace_id", "workspace_id", help="Workspace ID")
@click.option("--bot_id", "bot_id", help="Bot ID")
@click.option("--json", "json_output", is_flag=True, help="output in json format")
def retrieve_bot(workspace_id: str, bot_id: str, json_output: bool):
    """Retrieve bot details"""
    try:
        bot = coze.retrieve_bot(workspace_id, bot_id)
        RichBot(bot).print(json_output)
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")


"""audio"""


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
@click.option("--text", "text", help="Text")
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


"""dataset"""


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
    name: str, space_id: str, format_type: DocumentFormatType, description: Optional[str], icon: Optional[str]
):
    """Create a dataset"""
    try:
        res = coze.create_dataset(name, space_id, format_type, description, icon)
        console.print(f"[green]Dataset created: {res.dataset_id}[/green]")
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")


@dataset.command("list")
@click.option("--space_id", "space_id", help="Space ID")
@click.option("--name", "name", help="Dataset name")
@click.option("--format", "format_type", help="Dataset format", type=click.Choice(["txt", "table", "image"]))
@click.option("--page", default=1, help="page number")
@click.option("--size", default=10, help="page size")
@click.option("--json", "json_output", is_flag=True, help="output in json format")
@click.option("--all", "all_pages", is_flag=True, help="get all datasets")
def list_datasets(
    space_id: str,
    name: Optional[str],
    format_type: Optional[str],
    page: int,
    size: int,
    json_output: bool,
    all_pages: bool,
):
    """List all datasets in a space"""
    try:
        format_type = (
            {
                "txt": DocumentFormatType.DOCUMENT,
                "table": DocumentFormatType.SPREADSHEET,
                "image": DocumentFormatType.IMAGE,
            }[format_type]
            if format_type
            else None
        )
        res = coze.list_datasets(space_id, name, format_type, page, size, all_pages)
        res.print(json_output)
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")


@dataset.command("update")
@click.option("--dataset_id", "dataset_id", help="Dataset ID")
@click.option("--name", "name", help="Dataset name")
@click.option("--description", "description", help="Dataset description")
@click.option("--icon", "icon", help="Dataset icon")
def update_dataset(dataset_id: str, name: Optional[str], description: Optional[str], icon: Optional[str]):
    """Update a dataset"""
    try:
        coze.update_dataset(dataset_id, name, description, icon)
        console.print(f"[green]Dataset updated: {dataset_id}[/green]")
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")


@dataset.command("delete")
@click.option("--dataset_id", "dataset_id", help="Dataset ID")
def delete_dataset(dataset_id: str):
    """Delete a dataset"""
    try:
        coze.delete_dataset(dataset_id)
        console.print(f"[green]Dataset deleted: {dataset_id}[/green]")
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")


@dataset.command("process")
@click.option("--dataset_id", "dataset_id", help="Dataset ID")
@click.option("--document_id", "document_id", help="Document ID")
def process_dataset(dataset_id: str, document_id: str):
    """get dataset process"""
    try:
        res = coze.get_dataset_process(dataset_id, document_id)
        res.print()
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")


@dataset.group()
def document():
    """Dataset Document"""
    pass


@document.command("list")
@click.option("--dataset_id", "dataset_id", help="Dataset ID")
@click.option("--page", default=1, help="page number")
@click.option("--size", default=10, help="page size")
@click.option("--json", "json_output", is_flag=True, help="output in json format")
@click.option("--all", "all_pages", is_flag=True, help="get all documents")
def list_dataset_documents(dataset_id: str, page: int, size: int, json_output: bool, all_pages: bool):
    """List all documents in a dataset"""
    try:
        res = coze.list_dataset_documents(dataset_id, page, size, all_pages)
        res.print(json_output)
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")


@document.command("create")
@click.option("--dataset_id", "dataset_id", help="Dataset ID")
@click.option("--file", "file", help="File")
def create_dataset_document(dataset_id: str, file: str):
    """Upload a document to a dataset"""
    try:
        res = coze.create_dataset_document(dataset_id, file)
        res.print()
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")


@dataset.group()
def image():
    """Dataset Image"""
    pass


@image.command("list")
@click.option("--dataset_id", "dataset_id", help="Dataset ID")
@click.option("--keyword", "keyword", help="keyword")
@click.option("--has_caption", "has_caption", help="has caption")
@click.option("--page", default=1, help="page number")
@click.option("--size", default=10, help="page size")
@click.option("--json", "json_output", is_flag=True, help="output in json format")
@click.option("--all", "all_pages", is_flag=True, help="get all images")
def list_dataset_images(
    dataset_id: str, keyword: str, has_caption: bool, page: int, size: int, json_output: bool, all_pages: bool
):
    """List all images in a dataset"""
    try:
        res = coze.list_dataset_images(dataset_id, keyword, has_caption, page, size, all_pages)
        res.print(json_output)
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")


@image.command("update")
@click.option("--dataset_id", "dataset_id", help="Dataset ID")
@click.option("--document_id", "document_id", help="Document ID")
@click.option("--caption", "caption", help="Caption")
def update_dataset_image(dataset_id: str, document_id: str, caption: str):
    """Update a dataset image"""
    try:
        coze.update_dataset_image(dataset_id, document_id, caption)
        console.print(f"[green]Dataset image updated: {dataset_id}[/green]")
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")


"""template"""


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


"""files"""


@cli.group()
def files():
    """Files"""
    pass


@files.command("upload")
@click.option("--file", "file", help="File")
@click.option("--filename", "filename", help="Filename")
@click.option("--content", "content", help="Content")
def upload_file(file: Optional[str], filename: Optional[str], content: Optional[str]):
    """Upload a file"""
    try:
        if file:
            res = coze.upload_file(file)
            print("File: ", res.id, res.file_name)
        elif filename and content:
            res = coze.upload_file((filename, content))
            print("File: ", res.id, res.file_name)
        else:
            raise ValueError("file or filename and content must be provided")
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")


if __name__ == "__main__":
    """
    example:

    # alias
    alias first_workspace="./examples/cli.py workspace list --json | jq '.items[0].id' -r"
    alias personal_workspace="./examples/cli.py workspace list --type personal --json | jq '.items[0].id' -r"
    alias first_bot="./examples/cli.py bot list --workspace_id `personal_workspace` --json | jq '.items[0].bot_id' -r"

    # workspace
    ## list workspaces
    ./examples/cli.py workspace list --page 1 --size 10 --json
    ## get personal workspace id
    ./examples/cli.py workspace list --type personal --json | jq '.items[0].id' -r
    # bot
    ## list personal workspace bots
    ./examples/cli.py bot list --workspace_id `get_personal_workspace` --page 1 --size 10 --json
    ## get bot details
    ./examples/cli.py bot retrieve --workspace_id 1234567890 --bot_id 1234567890 --json
    # dataset
    ## list datasets
    ./examples/cli.py dataset list --space_id 1234567890 --page 1 --size 10 --json
    ## create dataset
    ./examples/cli.py dataset create --name "test" --space_id 1234567890 --format 0 --description "test" --icon "https://www.coze.cn/favicon.ico"

    """
    cli()
