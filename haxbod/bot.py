from pathlib import Path

from twitchio import Message
from twitchio.ext import commands

from haxbod import settings
from haxbod.models import db
from haxbod.utils.print import print_success, print_error, print_loading

from colorama import init, Fore, Style

init(autoreset=True)


class Haxbod(commands.Bot):
    def __init__(self):
        self.ready = False
        self.extensions = [p.stem for p in Path(f'{settings.BASE_DIR}/haxbod/cogs/').glob('*.py')]

        super().__init__(
            token=settings.ACCESS_TOKEN,
            prefix=settings.PREFIX,
            initial_channels=db.Channel.get_all_channel_names()
        )

    def setup(self) -> None:
        if self.extensions:
            print_loading('Installation of cogs begins...')
            for ext in self.extensions:
                try:
                    self.load_module(f'haxbod.cogs.{ext}')
                    print_success(f'"{ext}" cog loaded.')
                except Exception:
                    print_error(f'"{ext}" cog doesn\'t load.')

    def run(self) -> None:
        self.setup()
        print_loading('Bot running...')
        super().run()

    async def close(self) -> None:
        print_error('Shutdown...')
        await super().close()

    async def event_ready(self):
        if self.ready:
            return

        print_success(f'Connected as @{self.nick} with ID: {self.user_id}')
        self.ready = True
        print_success('Have a nice day!\n')

    async def event_message(self, message: Message):
        if message.echo:
            return

        channel_name = f'{Fore.MAGENTA}[@{message.channel.name}]'
        message_author = f'{Fore.WHITE}{message.author.name}'
        message_content = f'{Style.RESET_ALL}{message.content}'

        print(f'{Style.BRIGHT}{channel_name} {message_author}: {message_content}')
        await self.handle_commands(message)
