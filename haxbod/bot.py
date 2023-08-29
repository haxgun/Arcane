import sys
import traceback
from pathlib import Path

from twitchio import Message
from twitchio.ext import commands
from haxbod import settings
from haxbod.models import Channel
from haxbod.utils.print import print_success, print_error
from haxbod.utils.custom_commands import find_custom_command, custom_command_response
from rich.console import Console

console = Console()


class Haxbod(commands.Bot):
    __slots__ = ('ready', 'extensions')

    def __init__(self) -> None:
        self.ready = False
        self.extensions = [p.stem for p in Path(f'{settings.BASE_DIR}/haxbod/cogs/').glob('*.py')]

        super().__init__(
            token=settings.ACCESS_TOKEN,
            prefix=settings.PREFIX,
            initial_channels=Channel.get_all_channel_names()
        )

    def setup(self) -> None:
        if self.extensions:
            with console.status("[bold green]Installation of cogs begins...") as status:
                for ext in self.extensions:
                    try:
                        self.load_module(f'haxbod.cogs.{ext}')
                        print_success(f'"{ext.capitalize()}" cog loaded.')
                    except Exception:
                        print_error(f'"{ext.capitalize()}" cog doesn\'t load.')
                        console.print_exception()

    def run(self) -> None:
        self.setup()
        super().run()

    async def close(self) -> None:
        print_error('Shutdown...')
        await super().close()

    async def event_ready(self) -> None:
        if self.ready:
            return

        self.ready = True
        bot_nick = f'[link=https://twitch.tv/{self.nick}][yellow]@{self.nick}[/link][/yellow]'
        bot_id = f'[yellow]ID: {self.user_id}[/yellow]'
        channel_connected = ', '.join([f'[link=https://twitch.tv/{self.nick}][yellow]@{channel.name}[/link][/yellow]' for channel in self.connected_channels])
        print_success(f'Connected as {bot_nick} with {bot_id}')
        print_success(f'Connected to {channel_connected}')
        print_success('Have a nice day!\n')

    async def event_message(self, message: Message) -> None:
        if message.echo:
            return

        if settings.DEBUG:
            channel_name = f'[purple3][@[link=https://twitch.tv/{message.channel.name}]{message.channel.name}][/link][/purple3]'
            message_author = f'[link=https://twitch.tv/{message.author.name}]{message.author.name}'
            message_author_color = f'[{message.author.color}]' if message.author.color else ''
            console.print(f'[bold]{channel_name} {message_author_color}{message_author}[/]: [white]{message.content}')

        await self.handle_commands(message)

    async def event_command_error(self, context: commands.Context, error: Exception) -> None:
        if settings.DEBUG:
            print(f"Ignoring exception in command: {error}:", file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
            return
        pass

    async def handle_commands(self, message: Message) -> None:
        context = await self.get_context(message)
        await self.invoke_custom(context)

    async def invoke_custom(self, context: commands.Context) -> None:
        if await find_custom_command(context):
            response = await custom_command_response(context)
            await context.reply(response)
            return

        if not context.prefix or not context.is_valid:
            return

        self.run_event("command_invoke", context)
        await context.command(context)
