from typing import Any

from pony.orm import db_session
from twitchio.ext import commands
from twitchio.ext.commands.core import group

from haxbod.bot import Haxbod
from haxbod.models import db
from haxbod.utils.custom_commands import starts_with_emoji
from haxbod.utils.decorators import permission
from haxbod.utils.twitchapi import cmd_set_stream_title, get_stream_title


class Moderator(commands.Cog):
    __slots__ = 'bot'

    def __init__(self, bot: Haxbod) -> None:
        self.bot = bot

    @staticmethod
    async def send_usage(ctx: commands.Context) -> None:
        main_command = ctx.message.content.split()[0]
        sub_command = ctx.message.content.split()[1]
        await ctx.reply(f'Usage: {main_command} {sub_command} <command> <response>')

    @commands.command(name='commands', aliases=['cmds'])
    async def cmd_commands(self, ctx: commands.Context) -> None:
        with db_session:
            channel_id = db.Channel.get(name=ctx.channel.name).id
            commands_list = [command.name for command in db.Command.select(channel=channel_id)]
            commands_str = ', '.join(commands_list)
            await ctx.reply(f'Commands: {commands_str}')

    @group(name='command', aliases=['cmd'])
    @permission('moderator', 'broadcaster')
    async def cmd_command(self, ctx: commands.Context) -> None:
        await ctx.reply("Usage: !command [add|remove|edit]")

    @cmd_command.command(name='add')
    @permission('moderator', 'broadcaster')
    @db_session
    async def cmd_add_command(self, ctx: commands.Context, *args: Any) -> None:
        if len(args) >= 2:
            command_name = args[0]
            response = ' '.join(args[1:])

            if starts_with_emoji(command_name):
                await ctx.reply(f'Command must not contain an emoji!')
                return

            channel = db.Channel.get(name=ctx.channel.name)
            command = db.Command.get(name=command_name, channel=channel.id)

            if not command:
                command = db.Command(
                    name=command_name,
                    response=response,
                    channel=channel.id,
                )
            else:
                await ctx.reply(f'Command !{command_name} already exists.')
                return
            await ctx.reply(f'Command !{command_name} has been added.')
        else:
            await self.send_usage(ctx)

    @cmd_command.command(name='remove')
    @permission('moderator', 'broadcaster')
    @db_session
    async def cmd_delete_command(self, ctx: commands.Context, *args: Any) -> None:
        if len(args) >= 1:
            command_name = args[0]

            channel = db.Channel.get(name=ctx.channel.name)
            command = db.Command.get(name=command_name, channel=channel.id)

            if channel and command:
                command.delete()
                await ctx.reply(f'Command !{command_name} has been deleted.')
            else:
                await ctx.reply(f'Command !{command_name} not found.')
        else:
            await self.send_usage(ctx)

    @cmd_command.command(name='edit')
    @permission('moderator', 'broadcaster')
    @db_session
    async def cmd_edit_command(self, ctx: commands.Context, *args: Any) -> None:
        if len(args) >= 2:
            command_name = args[0]
            new_response = ' '.join(args[1:])

            channel = db.Channel.get(name=ctx.channel.name)
            command = db.Command.get(name=command_name, channel=channel.id)

            if channel and command:
                command.response = new_response
                db.commit()
                await ctx.reply(f'Command !{command_name} has been updated.')
            else:
                await ctx.reply(f'Command !{command_name} not found.')
        else:
            await self.send_usage(ctx)

    @commands.command(name='title')
    async def cmd_title(self, ctx: commands.Context, *, new_title: str = None) -> None:
        channel_name = ctx.channel.name
        if new_title is not None and (ctx.author.is_mod or ctx.author.is_broadcaster):
            if new_title == await get_stream_title(channel_name=channel_name):
                await ctx.reply('Error! This title is already in use!')
                return
            new_title_result = await cmd_set_stream_title(channel_name=channel_name, title=new_title)
            if new_title_result:
                await ctx.reply('Title has been changed!')
                return
            await ctx.reply('Title has not been changed!')
            return
        channel_info = await self.bot.fetch_channel(broadcaster=channel_name)
        channel_title = channel_info.title
        await ctx.reply(channel_title)


def prepare(bot: Haxbod) -> None:
    bot.add_cog(Moderator(bot))
