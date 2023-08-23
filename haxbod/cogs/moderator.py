from typing import Any

from pony.orm import db_session
from twitchio.ext import commands
from twitchio.ext.commands.core import group

from haxbod.bot import Haxbod
from haxbod.models import db
from haxbod.utils.custom_commands import starts_with_emoji
from haxbod.utils.decorators import permission


class Moderator(commands.Cog):
    __slots__ = 'bot'

    def __init__(self, bot: Haxbod) -> None:
        self.bot = bot

    @staticmethod
    async def send_usage(ctx: commands.Context, command: str) -> None:
        await ctx.reply(f'Usage: {command} <command> <response>')

    @group(name='command')
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
            main_command = ctx.message.content.split()[0]
            await self.send_usage(ctx, main_command)

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
            main_command = ctx.message.content.split()[0]
            await self.send_usage(ctx, main_command)

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
            main_command = ctx.message.content.split()[0]
            await self.send_usage(ctx, main_command)


def prepare(bot: Haxbod) -> None:
    bot.add_cog(Moderator(bot))
