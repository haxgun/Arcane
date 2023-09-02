from peewee import DoesNotExist
from twitchio.ext import commands

from haxbod.bot import Haxbod
from haxbod.models import Channel, Command, Alias
from haxbod.utils.custom_commands import starts_with_emoji
from haxbod.utils.decorators import permission


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
        channel = Channel.get(Channel.name == ctx.channel.name)
        commands_list = [command.name for command in Command.select().where(Command.channel == channel)]
        if commands_list:
            commands_str = ', '.join(commands_list)
            await ctx.reply(f'Commands: {commands_str}')
            return
        await ctx.reply(f'No commands.')

    @commands.command(name='addcommand', aliases=['addcmd'])
    @permission('moderator', 'broadcaster')
    async def cmd_add_command(self, ctx: commands.Context, *args: str) -> None:
        if len(args) < 2:
            await self.send_usage(ctx)
            return
        command_name = args[0]
        response = ' '.join(args[1:])
        if starts_with_emoji(command_name):
            await ctx.reply(f'Command must not contain an emoji!')
            return
        channel = Channel.get(Channel.name == ctx.channel.name)
        try:
            command = Command.get(Command.name == command_name, Command.channel == channel)
            await ctx.reply(f'Command !{command_name} already exists.')
        except DoesNotExist:
            command = Command.create(
                name=command_name,
                response=response,
                channel=channel
            )
            await ctx.reply(f'Command !{command_name} has been added.')

    @commands.command(name='rmcommand', aliases=['rmcmd'])
    @permission('moderator', 'broadcaster')
    async def cmd_delete_command(self, ctx: commands.Context, *args: str) -> None:
        if len(args) < 1:
            await self.send_usage(ctx)
            return
        command_name = args[0]
        try:
            channel = Channel.get(Channel.name == ctx.channel.name)
            command = Command.get(Command.name == command_name, Command.channel == channel)
            command.delete_instance()
            command.save()
            await ctx.reply(f'Command !{command_name} has been deleted.')
        except DoesNotExist:
            await ctx.reply(f'Command !{command_name} not found.')

    @commands.command(name='editcommand', aliases=['editcmd'])
    @permission('moderator', 'broadcaster')
    async def cmd_edit_command(self, ctx: commands.Context, *args: str) -> None:
        if len(args) < 2:
            await self.send_usage(ctx)
            return
        command_name = args[0]
        new_response = ' '.join(args[1:])

        try:
            channel = Channel.get(Channel.name == ctx.channel.name)
            command = Command.get(Command.name == command_name, Command.channel == channel)
            command.response = new_response
            command.save()
            await ctx.reply(f'Command !{command_name} has been updated.')
        except DoesNotExist:
            await ctx.reply(f'Command !{command_name} not found.')

    @commands.command(name='spam', aliases=['sm'])
    @permission('moderator', 'broadcaster')
    async def cmd_spam(self, ctx: commands.Context, *args: str) -> None:
        if len(args) < 1:
            await ctx.reply('Usage: !spam <count> <response>')
            return
        count = int(args[0])
        max_count = 20
        if count < max_count:
            response = ' '.join(args[1:])
            for _ in range(count):
                await ctx.send(response)
        else:
            await ctx.reply(f'Error! Count must be less than {max_count}!')

    @commands.command(name='aliases', aliases=['als'])
    async def cmd_aliases(self, ctx: commands.Context) -> None:
        channel = Channel.get(Channel.name == ctx.channel.name)
        aliases = Alias.select().join(Command).where(Command.channel == channel)
        if aliases:
            aliases_str = ', '.join([alias.name for alias in aliases])
            await ctx.send(f"Aliases: {aliases_str}")
        else:
            await ctx.send("No aliases")

    @commands.command(name='addalias', aliases=['addals'])
    @permission('moderator', 'broadcaster')
    async def cmd_add_aliases(self, ctx: commands.Context, *args: str) -> None:
        if len(args) < 2:
            await self.send_usage(ctx)
            return
        command_name, alias_name = args[0], args[1]
        if starts_with_emoji(command_name):
            await ctx.reply(f'Command must not contain an emoji!')
            return
        channel = Channel.get(name=ctx.channel.name)
        command = Command.get_or_none(name=command_name, channel=channel)
        if command:
            alias = Alias.get_or_none(name=alias_name, channel=channel)
            if alias:
                await ctx.send(f"Alias '{alias_name}' already exists.")
            else:
                Alias.create(name=alias_name, command=command, channel=channel)
                await ctx.send(f"Alias '{alias_name}' for command '{command_name}' created successfully.")
            return
        await ctx.send(f"Command '{command_name}' not found.")

    @commands.command(name='rmalias', aliases=['rmals'])
    @permission('moderator', 'broadcaster')
    async def cmd_remove_aliases(self, ctx: commands.Context, *args: str) -> None:
        if len(args) < 2:
            await self.send_usage(ctx)
            return
        alias_name = args[1]
        channel = Channel.get(name=ctx.channel.name)
        alias = Alias.get_or_none(name=alias_name, channel=channel)
        if alias:
            alias.delete_instance()
            await ctx.send(f"Alias '{alias_name}' has been deleted.")
            return
        await ctx.send(f"Alias '{alias_name}' not found.")


def prepare(bot: Haxbod) -> None:
    bot.add_cog(Moderator(bot))
