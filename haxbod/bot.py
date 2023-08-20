from pathlib import Path

from twitchio import Message
from twitchio.ext import commands

from haxbod import settings
from haxbod.models import db

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
            print('⏳ Installation of cogs begins...')
            for ext in self.extensions:
                self.load_module(f'haxbod.cogs.{ext}')
                print(f'🔩 "{ext}" cog loaded.')

    def run(self) -> None:
        self.setup()
        print('⌛ Bot running...')
        super().run()

    async def close(self) -> None:
        print('❌ Shutdown...')
        await super().close()

    async def event_ready(self):
        if self.ready:
            return

        print(f'✔ Connected as {self.nick} with ID: {self.user_id}')
        self.ready = True
        print('🤖 Have a nice day!\n')

    async def event_message(self, message: Message):
        if message.echo:
            return

        channel_name = f'{Fore.GREEN}@{message.channel.name}'
        message_author = f'{Fore.BLUE}{message.author.name}'
        message_content = f'{Style.RESET_ALL}{message.content}'

        print(f'👤 {channel_name} {message_author}: {message_content}')
        await self.handle_commands(message)
