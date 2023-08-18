from twitchio.ext import commands
from config import config


class Haxbod(commands.Bot):
    def __init__(self):
        super().__init__(
            token=config.ACCESS_TOKEN,
            prefix=config.PREFIX,
            initial_channels=config.CHANNELS
        )

    async def event_ready(self):
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')

    async def event_message(self, message):
        if message.echo:
            return

        print(f'{message.author.name}: {message.content}')
        await self.handle_commands(message)

    @commands.command()
    async def hello(self, ctx: commands.Context):
        await ctx.reply(f'Hello {ctx.author.name}!')
