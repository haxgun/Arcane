from twitchio.ext import commands

from arcane.bot import Arcane
from arcane.utils.decorators import permission
from arcane.utils.twitchapi import get_stream_title, get_game_id, set_stream_title, change_stream_game, get_game_name


class Stream(commands.Cog):
    __slots__ = 'bot'

    def __init__(self, bot: Arcane) -> None:
        self.bot = bot

    @commands.command(name='title')
    @permission('moderator', 'broadcaster')
    async def cmd_title(self, ctx: commands.Context, *args: str) -> None:
        channel_name = ctx.channel.name
        new_title = ' '.join(args)
        if len(new_title) > 1 and (ctx.author.is_mod or ctx.author.is_broadcaster):
            if new_title == await get_stream_title(channel_name=channel_name):
                await ctx.reply('Error! This title is already in use!')
                return
            new_title_result = await set_stream_title(channel_name=channel_name, title=new_title)
            if new_title_result:
                await ctx.reply('Title has been changed!')
                return
            await ctx.reply('Title has not been changed!')
            return
        channel_info = await self.bot.fetch_channel(broadcaster=channel_name)
        channel_title = channel_info.title
        await ctx.reply(channel_title)

    @commands.command(name='game')
    @permission('moderator', 'broadcaster')
    async def cmd_game(self, ctx: commands.Context, *args) -> None:
        new_game = ' '.join(args)
        channel_name = ctx.channel.name
        new_game_id = await get_game_id(new_game)
        new_game_name = await get_game_name(new_game)

        if new_game_id:
            if await change_stream_game(channel_name, new_game_id):
                await ctx.send(f"{new_game_name} ✅")
            else:
                await ctx.send("Failed ❌")
        else:
            await ctx.send("Game not found.")


def prepare(bot: Arcane) -> None:
    bot.add_cog(Stream(bot))
