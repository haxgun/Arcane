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

    @commands.command(name='commands', aliases=['cmds'])
    async def cmd_commands(self, ctx: commands.Context, subcommand: str = None, *args: str) -> None:
        if subcommand:
            subcommand_handlers = {
                'add': self.cmd_add_command,
                'a': self.cmd_add_command,
                'remove': self.cmd_remove_command,
                'rm': self.cmd_remove_command,
                'r': self.cmd_remove_command,
                'edit': self.cmd_edit_command,
                'e': self.cmd_edit_command,
            }

            subcommand = subcommand.lower()
            if subcommand in subcommand_handlers:
                await subcommand_handlers[subcommand](ctx, *args)
                return

        channel = Channel.get(Channel.name == ctx.channel.name)
        commands_list = Command.select().where(Command.channel == channel)
        if commands_list:
            commands_str = ', '.join([command.name for command in commands_list])
            await ctx.reply(f'Commands: {commands_str}')
        else:
            await ctx.reply(f'No commands.')

    @permission('moderator', 'broadcaster')
    async def cmd_add_command(self, ctx: commands.Context, *args: str) -> None:
        if len(args) < 2:
            await self.send_usage(ctx)
            return
        command_name = args[0]
        response = ' '.join(args[1:])
        if starts_with_emoji(command_name):
            await ctx.reply('❌ Command must not contain an emoji!')
            return
        channel = Channel.get(Channel.name == ctx.channel.name)
        command = Command.get_or_none(Command.name == command_name, Command.channel == channel)
        if not command:
            command = Command.create(
                name=command_name,
                response=response,
                channel=channel
            )
            await ctx.reply(f'✅ !{command_name}')
        else:
            await ctx.reply(f'❌ !{command_name} already exists.')

    @permission('moderator', 'broadcaster')
    async def cmd_remove_command(self, ctx: commands.Context, *args: str) -> None:
        if len(args) < 1:
            await self.send_usage(ctx)
            return
        command_name = args[0]
        channel = Channel.get(Channel.name == ctx.channel.name)
        command = Command.get_or_none(Command.name == command_name, Command.channel == channel)

        if command:
            command.delete_instance()
            command.save()
            await ctx.reply('✅')
        else:
            await ctx.reply('❌')

    @permission('moderator', 'broadcaster')
    async def cmd_edit_command(self, ctx: commands.Context, *args: str) -> None:
        if len(args) < 2:
            await self.send_usage(ctx)
            return
        command_name = args[0]
        new_response = ' '.join(args[1:])

        channel = Channel.get(Channel.name == ctx.channel.name)
        command = Command.get_or_none(Command.name == command_name, Command.channel == channel)
        if command:
            command.response = new_response
            command.save()
            await ctx.reply(f'✅ !{command_name}')
        else:
            await ctx.reply('❌')

    @commands.command(name='aliases', aliases=['als'])
    async def cmd_aliases(self, ctx: commands.Context, subcommand: str = None, *args: str) -> None:
        if subcommand:
            subcommand_handlers = {
                'add': self.cmd_add_alias,
                'a': self.cmd_add_alias,
                'remove': self.cmd_remove_alias,
                'rm': self.cmd_remove_alias,
                'r': self.cmd_remove_alias,
                'edit': self.cmd_edit_alias,
                'e': self.cmd_edit_alias,
            }

            subcommand = subcommand.lower()
            if subcommand in subcommand_handlers:
                await subcommand_handlers[subcommand](ctx, *args)
                return

        channel = Channel.get(Channel.name == ctx.channel.name)
        aliases = Alias.select().join(Command).where(Command.channel == channel)
        if aliases:
            aliases_str = ', '.join([alias.name for alias in aliases])
            await ctx.reply(f'Aliases: {aliases_str}')
        else:
            await ctx.reply(f'No aliases.')

    @permission('moderator', 'broadcaster')
    async def cmd_add_alias(self, ctx: commands.Context, *args: str) -> None:
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
                await ctx.send(f'❌ !{alias_name} already exists.')
            else:
                Alias.create(name=alias_name, command=command, channel=channel)
                await ctx.send(f'✅ !{alias_name}')
            return
        await ctx.send('❌')

    @permission('moderator', 'broadcaster')
    async def cmd_remove_alias(self, ctx: commands.Context, *args: str) -> None:
        if len(args) < 1:
            await self.send_usage(ctx)
            return
        alias_name = args[0]
        channel = Channel.get(name=ctx.channel.name)
        alias = Alias.get_or_none(name=alias_name, channel=channel)
        if alias:
            alias.delete_instance()
            await ctx.reply('✅')
        else:
            await ctx.reply('❌')

    @permission('moderator', 'broadcaster')
    async def cmd_edit_alias(self, ctx: commands.Context, *args: str) -> None:
        if len(args) < 2:
            await self.send_usage(ctx)
            return
        alias_name = args[0]
        new_name = args[1]

        try:
            channel = Channel.get(Channel.name == ctx.channel.name)
            alias = Alias.get(Alias.name == alias_name, Alias.channel == channel)
            alias.name = new_name
            alias.save()
            await ctx.reply(f'✅ !{new_name}')
        except DoesNotExist as e:
            print(e)
            await ctx.reply('❌')


def prepare(bot: Haxbod) -> None:
    bot.add_cog(Moderator(bot))
