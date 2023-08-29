from asyncio import gather
from typing import Any

from peewee import IntegrityError, DoesNotExist
from twitchio.ext import commands

from haxbod.bot import Haxbod
from haxbod.models import Channel
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
            try:
                channel = Channel.create(name=channel_name)
                await self.bot.join_channels([channel_name])
                await ctx.reply(f'The user @{channel_name} added.')
            except IntegrityError:
                await ctx.reply(f'The user @{channel_name} already exists.')

    @commands.command(name='delchannel', aliases=['delchl'])
    @owner_only()
    async def cmd_del_channel(self, ctx: commands.Context, *args: Any) -> None:
        channel_name = args[0]
        try:
            channel = Channel.get(Channel.name == channel_name)
            channel.delete_instance()
            channel.save()
            await self.bot.part_channels([channel_name])
            await ctx.reply(f'The user @{channel_name} has been removed from the database.')
        except DoesNotExist:
            await ctx.reply(f'The user @{channel_name} is not in the database.')


def prepare(bot: Haxbod) -> None:
    bot.add_cog(Owner(bot))
