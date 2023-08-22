from asyncio import gather
from typing import Any

from pony.orm import db_session
from twitchio.ext import commands

from haxbod.bot import Haxbod
from haxbod.models import db
from haxbod.utils.decorators import owner_only


class Owner(commands.Cog):
    __slots__ = 'bot'

    def __init__(self, bot: Haxbod) -> None:
        self.bot = bot

    @commands.command(name='addchannel', aliases=['addchl'])
    @owner_only()
    async def cmd_add_channel(self, ctx: commands.Context, *args: Any) -> None:
        if len(args) >= 1:
            channel_name = args[0]
            try:
                exists, *_ = await gather(self.bot.fetch_channel(channel_name))
            except Exception:
                await ctx.reply('There is no such user!')
                return

            with db_session:
                channel = db.Channel(name=channel_name)

            if channel:
                await self.bot.join_channels([channel_name])
                await ctx.reply(f'The user @{channel_name} added.')
            else:
                await ctx.reply(f'The user @{channel_name} already exists.')

    @commands.command(name='delchannel', aliases=['delchl'])
    @owner_only()
    async def cmd_del_channel(self, ctx: commands.Context, *args: Any) -> None:
        channel_name = args[0]

        with db_session:
            channel = db.Channel.get(name=channel_name)

            if channel:
                channel.delete()
                await self.bot.part_channels([channel_name])
                await ctx.reply(f'The user @{channel_name} has been removed from the database.')
            else:
                await ctx.reply(f'The user @{channel_name} is not in the database.')


def prepare(bot: Haxbod) -> None:
    bot.add_cog(Owner(bot))
